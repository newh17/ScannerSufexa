"""
Servicio de logging centralizado.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class LoggerService:
    """
    Servicio centralizado de logging.

    Características:
    - Logs en archivo con rotación automática
    - Logs en consola (opcional)
    - Formato estandarizado con timestamps
    - Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - Thread-safe
    """

    def __init__(
        self,
        nombre_logger: str = "ScannerSufexa",
        archivo_log: Optional[str] = None,
        nivel: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        log_consola: bool = True
    ):
        """
        Inicializa el servicio de logging.

        Args:
            nombre_logger: Nombre del logger
            archivo_log: Ruta al archivo de log (opcional)
            nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Tamaño máximo del archivo de log antes de rotar
            backup_count: Número de archivos de backup a mantener
            log_consola: Si True, también imprime en consola
        """
        self.nombre_logger = nombre_logger
        self.archivo_log = archivo_log
        self.nivel = nivel
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.log_consola = log_consola

        # Crear logger
        self.logger = logging.getLogger(nombre_logger)
        self.logger.setLevel(self._obtener_nivel(nivel))

        # Evitar duplicar handlers si ya existe
        if not self.logger.handlers:
            self._configurar_handlers()

    def _obtener_nivel(self, nivel: str) -> int:
        """Convierte string de nivel a constante de logging."""
        niveles = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        return niveles.get(nivel.upper(), logging.INFO)

    def _configurar_handlers(self):
        """Configura los handlers de logging."""
        # Formato con timestamp, nivel y mensaje
        formato = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler de archivo con rotación
        if self.archivo_log:
            # Crear directorio si no existe
            archivo_path = Path(self.archivo_log)
            archivo_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                self.archivo_log,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.logger.level)
            file_handler.setFormatter(formato)
            self.logger.addHandler(file_handler)

        # Handler de consola
        if self.log_consola:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.logger.level)
            console_handler.setFormatter(formato)
            self.logger.addHandler(console_handler)

    def debug(self, mensaje: str):
        """Log nivel DEBUG."""
        self.logger.debug(mensaje)

    def info(self, mensaje: str):
        """Log nivel INFO."""
        self.logger.info(mensaje)

    def warning(self, mensaje: str):
        """Log nivel WARNING."""
        self.logger.warning(mensaje)

    def error(self, mensaje: str, exc_info: bool = False):
        """
        Log nivel ERROR.

        Args:
            mensaje: Mensaje de error
            exc_info: Si True, incluye información de excepción
        """
        self.logger.error(mensaje, exc_info=exc_info)

    def critical(self, mensaje: str, exc_info: bool = False):
        """
        Log nivel CRITICAL.

        Args:
            mensaje: Mensaje crítico
            exc_info: Si True, incluye información de excepción
        """
        self.logger.critical(mensaje, exc_info=exc_info)

    def log_procesamiento_inicio(self, archivo: str):
        """Log de inicio de procesamiento de archivo."""
        self.info(f"▶️  INICIO procesamiento: {Path(archivo).name}")

    def log_procesamiento_exito(
        self,
        archivo: str,
        cliente: str,
        numero: int,
        fecha: str,
        tiempo_ms: Optional[float] = None
    ):
        """Log de procesamiento exitoso."""
        mensaje = (
            f"✅ ÉXITO procesamiento: {Path(archivo).name} | "
            f"Cliente: {cliente} | #{numero} | {fecha}"
        )
        if tiempo_ms:
            mensaje += f" | Tiempo: {tiempo_ms:.2f}ms"
        self.info(mensaje)

    def log_procesamiento_error(
        self,
        archivo: str,
        razon: str,
        exc_info: bool = False
    ):
        """Log de error en procesamiento."""
        self.error(
            f"❌ ERROR procesamiento: {Path(archivo).name} | Razón: {razon}",
            exc_info=exc_info
        )

    def log_duplicado(self, archivo: str, numero: int, fecha: str):
        """Log de albarán duplicado."""
        self.warning(
            f"⚠️  DUPLICADO: {Path(archivo).name} | #{numero} | {fecha}"
        )

    def log_ocr(self, archivo: str, caracteres: int, confianza: Optional[float] = None):
        """Log de proceso OCR."""
        mensaje = f"🔍 OCR: {Path(archivo).name} | {caracteres} caracteres"
        if confianza:
            mensaje += f" | Confianza: {confianza:.1f}%"
        self.debug(mensaje)

    def log_extraccion(
        self,
        archivo: str,
        cliente: Optional[str],
        fecha: Optional[str],
        numero: Optional[int]
    ):
        """Log de extracción de datos."""
        self.debug(
            f"📊 Extracción: {Path(archivo).name} | "
            f"Cliente: {cliente or 'N/A'} | "
            f"Fecha: {fecha or 'N/A'} | "
            f"Número: {numero or 'N/A'}"
        )

    def log_movimiento_archivo(self, origen: str, destino: str):
        """Log de movimiento de archivo."""
        self.debug(
            f"📁 Movido: {Path(origen).name} → {Path(destino).parent.name}/{Path(destino).name}"
        )

    def log_estadisticas(
        self,
        total: int,
        exitosos: int,
        errores: int,
        duplicados: int = 0
    ):
        """Log de estadísticas."""
        tasa_exito = (exitosos / total * 100) if total > 0 else 0
        self.info(
            f"📊 Estadísticas: Total={total} | "
            f"Exitosos={exitosos} | Errores={errores} | "
            f"Duplicados={duplicados} | Tasa éxito={tasa_exito:.1f}%"
        )

    def log_monitor_inicio(self, carpeta: str):
        """Log de inicio del monitor."""
        self.info(f"👀 Monitor iniciado: {carpeta}")

    def log_monitor_detenido(self):
        """Log de detención del monitor."""
        self.info("🛑 Monitor detenido")

    def separador(self):
        """Log de separador visual."""
        self.info("=" * 70)

    @staticmethod
    def crear_logger_archivo(
        archivo_log: str,
        nivel: str = "INFO"
    ) -> "LoggerService":
        """
        Crea un logger que solo escribe a archivo (sin consola).

        Args:
            archivo_log: Ruta al archivo de log
            nivel: Nivel de logging

        Returns:
            LoggerService: Instancia configurada
        """
        return LoggerService(
            archivo_log=archivo_log,
            nivel=nivel,
            log_consola=False
        )

    @staticmethod
    def crear_logger_consola(nivel: str = "INFO") -> "LoggerService":
        """
        Crea un logger que solo imprime en consola.

        Args:
            nivel: Nivel de logging

        Returns:
            LoggerService: Instancia configurada
        """
        return LoggerService(
            archivo_log=None,
            nivel=nivel,
            log_consola=True
        )
