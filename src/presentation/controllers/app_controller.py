"""
Controlador principal de la aplicación.

Conecta la UI con el backend: watchdog, OCR, pipeline y filesystem.
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal, Qt

from presentation.ui import MainWindow
from infrastructure.monitoring import WatchdogFileMonitor
from infrastructure.filesystem import FileSystemService
from infrastructure.logging import LoggerService
from infrastructure.persistence.repositories import NullAlbaranRepository, NullClienteRepository
from application.services import ExtractorDatosService
from application.use_cases import ProcesarAlbaranUseCase

try:
    from infrastructure.ocr import TesseractOCRService, PDFProcessor
    OCR_DISPONIBLE = True
except ImportError:
    OCR_DISPONIBLE = False

# Archivo de configuración junto al .exe
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "config.json"

CONFIG_DEFAULTS = {
    "scanner": "C:\\scan\\entrada",
    "salida": "C:\\albaranes",
    "errores": "C:\\albaranes\\errores",
}


class _Signals(QObject):
    """Señales internas para actualizar la UI desde hilos de fondo."""
    albaran_ok = Signal(str, str, str, str)   # cliente, numero, fecha, ruta_final
    albaran_error = Signal(str, str)           # nombre_archivo, razon
    log_msg = Signal(str, str)                 # nivel (info/warning/error/success), mensaje
    stats = Signal(int, int)                   # procesados, errores


class AppController:
    """
    Controlador que conecta MainWindow con el pipeline completo.

    Responsabilidades:
    - Leer y guardar configuración en config.json
    - Construir todos los servicios del backend
    - Arrancar/parar el WatchdogFileMonitor
    - Recibir resultados del pipeline (hilo de fondo) y actualizarla UI de forma segura
    """

    def __init__(self, window: MainWindow):
        self._window = window
        self._monitor: Optional[WatchdogFileMonitor] = None
        self._use_case: Optional[ProcesarAlbaranUseCase] = None
        self._procesados = 0
        self._errores = 0
        self._lock = threading.Lock()

        # Señales thread-safe (Qt encola automáticamente entre hilos)
        self._signals = _Signals()
        self._signals.albaran_ok.connect(self._ui_albaran_ok, Qt.QueuedConnection)
        self._signals.albaran_error.connect(self._ui_albaran_error, Qt.QueuedConnection)
        self._signals.log_msg.connect(self._ui_log, Qt.QueuedConnection)
        self._signals.stats.connect(self._ui_stats, Qt.QueuedConnection)

        # Logger
        log_path = Path(__file__).parent.parent.parent.parent / "logs" / "scanner.log"
        self._logger = LoggerService(
            archivo_log=str(log_path),
            nivel="INFO",
            log_consola=False
        )

        # Cargar configuración persistida
        self._config = self._cargar_config()

        # Conectar señales de la ventana
        window.start_monitor.connect(self._on_iniciar)
        window.stop_monitor.connect(self._on_detener)
        window.config_changed.connect(self._on_config_cambiada)
        window.refresh_requested.connect(self._on_refrescar)

        # Mostrar configuración actual en la UI
        self._window.actualizar_carpeta(self._config["scanner"])
        self._window.log_info("Sistema listo. Pulsa ▶ Iniciar para comenzar.")

    # ------------------------------------------------------------------
    # Slots de la UI (hilo principal)
    # ------------------------------------------------------------------

    def _on_iniciar(self):
        if self._monitor is not None:
            return

        if not OCR_DISPONIBLE:
            self._window.mostrar_error(
                "OCR no disponible",
                "No se encontró Tesseract o sus dependencias.\n"
                "Comprueba que tesseract.exe esté instalado en el sistema."
            )
            return

        carpeta_scanner = self._config["scanner"]

        try:
            self._construir_use_case()
            self._monitor = WatchdogFileMonitor(
                carpeta_monitoreada=carpeta_scanner,
                callback_procesamiento=self._procesar_pdf,
                tiempo_espera=2.0,
                verbose=False,
            )
            self._monitor.start()

            self._window.actualizar_estado_monitor(True)
            self._window.actualizar_carpeta(carpeta_scanner)
            self._window.log_success(f"Monitor iniciado → {carpeta_scanner}")
            self._logger.log_monitor_inicio(carpeta_scanner)

        except Exception as e:
            self._window.mostrar_error("Error al iniciar", str(e))
            self._window.log_error(f"No se pudo iniciar: {e}")
            self._monitor = None

    def _on_detener(self):
        if self._monitor is None:
            return

        self._monitor.stop()
        self._monitor = None

        self._window.actualizar_estado_monitor(False)
        self._window.log_info("Monitor detenido.")
        self._logger.log_monitor_detenido()

    def _on_config_cambiada(self, config: dict):
        self._config.update(config)
        self._guardar_config()
        self._window.actualizar_carpeta(config.get("scanner", ""))
        self._window.log_info("Configuración guardada.")

        # Reconstruir use_case con nuevas carpetas (si no está corriendo)
        if self._monitor is None:
            self._use_case = None

    def _on_refrescar(self):
        with self._lock:
            p, e = self._procesados, self._errores
        self._window.actualizar_estadisticas(p, e)

    # ------------------------------------------------------------------
    # Callback del watchdog (hilo de fondo)
    # ------------------------------------------------------------------

    def _procesar_pdf(self, pdf_path: str) -> bool:
        """
        Llamado por WatchdogFileMonitor desde su hilo de procesamiento.
        No puede tocar widgets Qt directamente — usa señales.
        """
        nombre = Path(pdf_path).name
        self._signals.log_msg.emit("info", f"Procesando: {nombre}")

        resultado = self._use_case.ejecutar(pdf_path)

        with self._lock:
            if resultado.exito:
                self._procesados += 1
                p, e = self._procesados, self._errores
            else:
                self._errores += 1
                p, e = self._procesados, self._errores

        if resultado.exito and resultado.albaran:
            alb = resultado.albaran
            self._signals.albaran_ok.emit(
                str(alb.cliente.nombre),
                str(alb.numero),
                str(alb.fecha),
                pdf_path,
            )
            self._signals.log_msg.emit(
                "success",
                f"OK: {alb.cliente.nombre} | #{alb.numero} | {alb.fecha}"
            )
        else:
            self._signals.albaran_error.emit(nombre, resultado.razon or "Error desconocido")
            self._signals.log_msg.emit("error", f"Error: {nombre} → {resultado.razon}")

        self._signals.stats.emit(p, e)
        return resultado.exito

    # ------------------------------------------------------------------
    # Slots de señales internas (hilo principal, seguros para UI)
    # ------------------------------------------------------------------

    def _ui_albaran_ok(self, cliente: str, numero: str, fecha: str, ruta: str):
        fecha_proc = datetime.now().strftime("%d/%m/%Y %H:%M")
        self._window.agregar_albaran(None, cliente, numero, fecha, fecha_proc)
        self._window.actualizar_ranking([])  # sin BD, ranking vacío

    def _ui_albaran_error(self, nombre: str, razon: str):
        pass  # ya logueado en _ui_log

    def _ui_log(self, nivel: str, mensaje: str):
        if nivel == "success":
            self._window.log_success(mensaje)
        elif nivel == "warning":
            self._window.log_warning(mensaje)
        elif nivel == "error":
            self._window.log_error(mensaje)
        else:
            self._window.log_info(mensaje)

    def _ui_stats(self, procesados: int, errores: int):
        self._window.actualizar_estadisticas(procesados, errores)

    # ------------------------------------------------------------------
    # Construcción de servicios
    # ------------------------------------------------------------------

    def _construir_use_case(self):
        if self._use_case is not None:
            return

        pdf_processor = PDFProcessor(dpi=300)
        ocr_service = TesseractOCRService(language='spa', config='--psm 3')
        extractor = ExtractorDatosService()
        file_system = FileSystemService(
            carpeta_salida_base=self._config["salida"],
            carpeta_errores=self._config["errores"],
        )
        albaran_repo = NullAlbaranRepository()
        cliente_repo = NullClienteRepository()

        self._use_case = ProcesarAlbaranUseCase(
            pdf_processor=pdf_processor,
            ocr_service=ocr_service,
            extractor=extractor,
            albaran_repo=albaran_repo,
            cliente_repo=cliente_repo,
            file_system=file_system,
            logger=self._logger,
        )

    # ------------------------------------------------------------------
    # Persistencia de configuración
    # ------------------------------------------------------------------

    def _cargar_config(self) -> dict:
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return {**CONFIG_DEFAULTS, **data}
        except Exception:
            pass
        return dict(CONFIG_DEFAULTS)

    def _guardar_config(self):
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._window.log_warning(f"No se pudo guardar configuración: {e}")

    def cerrar(self):
        """Llamar al cerrar la ventana para detener el monitor limpiamente."""
        if self._monitor:
            self._monitor.stop()
