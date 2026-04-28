"""
Monitor de carpetas usando Watchdog para detectar nuevos PDFs.
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional, Set
from queue import Queue, Empty
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class PDFFileHandler(FileSystemEventHandler):
    """
    Handler que detecta eventos de archivos PDF.

    Se dispara cuando:
    - Se crea un nuevo archivo PDF
    - Se modifica un archivo PDF (durante escritura)
    """

    def __init__(self, queue: Queue, monitor: "WatchdogFileMonitor"):
        """
        Inicializa el handler.

        Args:
            queue: Cola donde se añaden los archivos detectados
            monitor: Referencia al monitor principal
        """
        super().__init__()
        self.queue = queue
        self.monitor = monitor
        self._archivos_en_proceso: Set[str] = set()
        self._lock = threading.Lock()

    def on_created(self, event: FileSystemEvent):
        """Se ejecuta cuando se crea un archivo."""
        if event.is_directory:
            return

        if self._es_pdf(event.src_path):
            self.monitor.log(f"📄 Archivo detectado: {Path(event.src_path).name}")
            self._encolar_archivo(event.src_path)

    def on_modified(self, event: FileSystemEvent):
        """Se ejecuta cuando se modifica un archivo."""
        # Durante la copia, el archivo se modifica varias veces
        # Solo procesamos cuando esté completo (ver _procesar_cola)
        pass

    def _es_pdf(self, path: str) -> bool:
        """Verifica si el archivo es un PDF."""
        return path.lower().endswith('.pdf')

    def _encolar_archivo(self, path: str):
        """
        Añade un archivo a la cola de procesamiento.

        Evita duplicados de archivos ya encolados.
        """
        with self._lock:
            if path not in self._archivos_en_proceso:
                self._archivos_en_proceso.add(path)
                self.queue.put({
                    'path': path,
                    'timestamp': datetime.now(),
                })
                self.monitor.log(f"   ➕ Añadido a cola de procesamiento")

    def marcar_procesado(self, path: str):
        """Marca un archivo como procesado."""
        with self._lock:
            self._archivos_en_proceso.discard(path)


class WatchdogFileMonitor:
    """
    Monitor de carpeta que detecta automáticamente nuevos PDFs.

    Características:
    - Detección automática de archivos PDF
    - Espera a que el archivo esté completamente escrito
    - Cola de procesamiento
    - Callback para procesar cada archivo
    - Manejo de errores
    - Logging de eventos
    """

    def __init__(
        self,
        carpeta_monitoreada: str,
        callback_procesamiento: Callable[[str], bool],
        tiempo_espera: float = 2.0,
        intervalo_chequeo: float = 1.0,
        verbose: bool = True
    ):
        """
        Inicializa el monitor de archivos.

        Args:
            carpeta_monitoreada: Ruta de la carpeta a monitorear
            callback_procesamiento: Función que procesa cada archivo.
                                   Debe retornar True si se procesó correctamente.
            tiempo_espera: Segundos a esperar después de detectar un archivo
                          para asegurar que esté completamente escrito (default: 2.0)
            intervalo_chequeo: Segundos entre cada chequeo de la cola (default: 1.0)
            verbose: Si True, imprime logs de eventos
        """
        self.carpeta_monitoreada = Path(carpeta_monitoreada)
        self.callback_procesamiento = callback_procesamiento
        self.tiempo_espera = tiempo_espera
        self.intervalo_chequeo = intervalo_chequeo
        self.verbose = verbose

        # Cola de archivos pendientes
        self._queue: Queue = Queue()

        # Control de ejecución
        self._running = False
        self._observer: Optional[Observer] = None
        self._thread_procesamiento: Optional[threading.Thread] = None
        self._handler: Optional[PDFFileHandler] = None

        # Estadísticas
        self.archivos_procesados = 0
        self.archivos_con_error = 0

        # Verificar que la carpeta existe
        self._asegurar_carpeta()

    def _asegurar_carpeta(self):
        """Crea la carpeta si no existe."""
        if not self.carpeta_monitoreada.exists():
            self.carpeta_monitoreada.mkdir(parents=True, exist_ok=True)
            self.log(f"📁 Carpeta creada: {self.carpeta_monitoreada}")

    def log(self, mensaje: str):
        """Imprime un mensaje si verbose está activado."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {mensaje}")

    def start(self):
        """
        Inicia el monitor de archivos.

        Esto:
        1. Inicia el observer de watchdog
        2. Inicia el thread de procesamiento de cola
        """
        if self._running:
            self.log("⚠️  El monitor ya está ejecutándose")
            return

        self._running = True

        # Configurar watchdog observer
        self._handler = PDFFileHandler(self._queue, self)
        self._observer = Observer()
        self._observer.schedule(
            self._handler,
            str(self.carpeta_monitoreada),
            recursive=False
        )

        # Iniciar observer
        self._observer.start()
        self.log(f"👀 Monitor iniciado en: {self.carpeta_monitoreada}")

        # Iniciar thread de procesamiento
        self._thread_procesamiento = threading.Thread(
            target=self._procesar_cola,
            daemon=True
        )
        self._thread_procesamiento.start()
        self.log(f"⚙️  Thread de procesamiento iniciado")

    def stop(self):
        """
        Detiene el monitor de archivos.

        Espera a que termine de procesar los archivos en cola.
        """
        if not self._running:
            return

        self.log("🛑 Deteniendo monitor...")
        self._running = False

        # Detener observer
        if self._observer:
            self._observer.stop()
            self._observer.join()

        # Esperar a que termine el thread de procesamiento
        if self._thread_procesamiento:
            self._thread_procesamiento.join(timeout=5.0)

        self.log("✅ Monitor detenido")
        self._mostrar_estadisticas()

    def _procesar_cola(self):
        """
        Thread que procesa los archivos en cola.

        Loop principal:
        1. Espera nuevos archivos en la cola
        2. Espera a que el archivo esté completo
        3. Llama al callback de procesamiento
        4. Maneja errores
        """
        self.log("🔄 Procesador de cola iniciado")

        while self._running:
            try:
                # Intentar obtener un archivo de la cola (con timeout)
                try:
                    item = self._queue.get(timeout=self.intervalo_chequeo)
                except Empty:
                    continue

                path = item['path']
                timestamp_deteccion = item['timestamp']

                # Esperar a que el archivo esté completamente escrito
                if not self._esperar_archivo_completo(path):
                    self.log(f"⚠️  Archivo no disponible: {Path(path).name}")
                    self.archivos_con_error += 1
                    if self._handler:
                        self._handler.marcar_procesado(path)
                    self._queue.task_done()
                    continue

                # Procesar el archivo
                self.log(f"⚙️  Procesando: {Path(path).name}")

                try:
                    exito = self.callback_procesamiento(path)

                    if exito:
                        self.archivos_procesados += 1
                        self.log(f"✅ Procesado exitosamente: {Path(path).name}")
                    else:
                        self.archivos_con_error += 1
                        self.log(f"❌ Error al procesar: {Path(path).name}")

                except Exception as e:
                    self.archivos_con_error += 1
                    self.log(f"❌ Excepción al procesar {Path(path).name}: {e}")

                # Marcar como procesado
                if self._handler:
                    self._handler.marcar_procesado(path)

                self._queue.task_done()

            except Exception as e:
                self.log(f"❌ Error en procesador de cola: {e}")
                time.sleep(1)

    def _esperar_archivo_completo(self, path: str, max_intentos: int = 10) -> bool:
        """
        Espera a que un archivo esté completamente escrito.

        Estrategia:
        1. Espera un tiempo inicial (tiempo_espera)
        2. Verifica que el archivo exista
        3. Verifica que el tamaño no cambie durante 1 segundo

        Args:
            path: Ruta al archivo
            max_intentos: Número máximo de intentos

        Returns:
            bool: True si el archivo está completo, False si no
        """
        # Espera inicial
        time.sleep(self.tiempo_espera)

        archivo = Path(path)

        # Verificar que existe
        if not archivo.exists():
            return False

        # Verificar que el tamaño se estabilice
        for _ in range(max_intentos):
            try:
                tamano_inicial = archivo.stat().st_size
                time.sleep(0.5)

                if not archivo.exists():
                    return False

                tamano_final = archivo.stat().st_size

                # Si el tamaño no cambió, el archivo está completo
                if tamano_inicial == tamano_final and tamano_final > 0:
                    return True

            except (OSError, FileNotFoundError):
                return False

        return False

    def _mostrar_estadisticas(self):
        """Muestra estadísticas del monitor."""
        total = self.archivos_procesados + self.archivos_con_error

        self.log("📊 Estadísticas:")
        self.log(f"   Total procesados: {total}")
        self.log(f"   ✅ Exitosos: {self.archivos_procesados}")
        self.log(f"   ❌ Con error: {self.archivos_con_error}")

        if total > 0:
            tasa_exito = (self.archivos_procesados / total) * 100
            self.log(f"   📈 Tasa de éxito: {tasa_exito:.1f}%")

    def procesar_archivos_existentes(self):
        """
        Procesa archivos PDF que ya existen en la carpeta.

        Útil para procesar un backlog de archivos al iniciar.
        """
        archivos_existentes = list(self.carpeta_monitoreada.glob("*.pdf"))

        if not archivos_existentes:
            self.log("📭 No hay archivos existentes para procesar")
            return

        self.log(f"📦 Encontrados {len(archivos_existentes)} archivos existentes")

        for archivo in archivos_existentes:
            self._queue.put({
                'path': str(archivo),
                'timestamp': datetime.now(),
            })
            self.log(f"   ➕ Encolado: {archivo.name}")

    def get_estado(self) -> dict:
        """
        Obtiene el estado actual del monitor.

        Returns:
            dict: Diccionario con información del estado
        """
        return {
            'activo': self._running,
            'carpeta': str(self.carpeta_monitoreada),
            'en_cola': self._queue.qsize(),
            'procesados': self.archivos_procesados,
            'errores': self.archivos_con_error,
        }

    def __enter__(self):
        """Permite usar el monitor como context manager."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Detiene el monitor al salir del context manager."""
        self.stop()
