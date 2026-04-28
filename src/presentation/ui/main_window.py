"""
Ventana principal de la aplicación.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from .components import (
    StatusWidget,
    AlbaranTableWidget,
    RankingWidget,
    ErrorLogWidget,
    ConfigDialog
)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación Scanner Sufexa.

    Integra todos los componentes:
    - Widget de estado
    - Tabla de albaranes
    - Ranking de clientes
    - Log de eventos
    - Configuración
    """

    # Señales
    start_monitor = Signal()
    stop_monitor = Signal()
    config_changed = Signal(dict)  # {scanner, salida, errores}
    refresh_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scanner Sufexa v1.0")
        self.setMinimumSize(1200, 800)
        self._setup_ui()
        self._setup_menu()

    def _setup_ui(self):
        """Configura la interfaz principal."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)

        # Splitter principal (vertical)
        splitter_main = QSplitter(Qt.Vertical)

        # Panel superior (horizontal)
        panel_superior = QWidget()
        layout_superior = QHBoxLayout(panel_superior)

        # Widget de estado (izquierda)
        self.status_widget = StatusWidget()
        self.status_widget.start_clicked.connect(self.start_monitor.emit)
        self.status_widget.stop_clicked.connect(self.stop_monitor.emit)
        layout_superior.addWidget(self.status_widget, 1)

        # Ranking (derecha)
        self.ranking_widget = RankingWidget()
        layout_superior.addWidget(self.ranking_widget, 2)

        splitter_main.addWidget(panel_superior)

        # Tabs inferiores
        self.tabs = QTabWidget()

        # Tab 1: Albaranes
        self.albaran_table = AlbaranTableWidget()
        self.tabs.addTab(self.albaran_table, "📄 Albaranes")

        # Tab 2: Log de eventos
        self.error_log = ErrorLogWidget()
        self.tabs.addTab(self.error_log, "📋 Log")

        splitter_main.addWidget(self.tabs)

        # Configurar tamaños del splitter
        splitter_main.setSizes([300, 500])

        main_layout.addWidget(splitter_main)

        # Aplicar estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-size: 11pt;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #cccccc;
                font-weight: bold;
            }
        """)

    def _setup_menu(self):
        """Configura la barra de menú."""
        menubar = self.menuBar()

        # Menú Archivo
        menu_archivo = menubar.addMenu("&Archivo")

        accion_config = QAction("⚙ &Configuración", self)
        accion_config.setShortcut("Ctrl+,")
        accion_config.triggered.connect(self._mostrar_config)
        menu_archivo.addAction(accion_config)

        menu_archivo.addSeparator()

        accion_salir = QAction("&Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

        # Menú Monitor
        menu_monitor = menubar.addMenu("&Monitor")

        accion_iniciar = QAction("▶ &Iniciar", self)
        accion_iniciar.setShortcut("Ctrl+S")
        accion_iniciar.triggered.connect(self.start_monitor.emit)
        menu_monitor.addAction(accion_iniciar)

        accion_detener = QAction("⬛ &Detener", self)
        accion_detener.setShortcut("Ctrl+D")
        accion_detener.triggered.connect(self.stop_monitor.emit)
        menu_monitor.addAction(accion_detener)

        menu_monitor.addSeparator()

        accion_refrescar = QAction("🔄 &Refrescar", self)
        accion_refrescar.setShortcut("F5")
        accion_refrescar.triggered.connect(self.refresh_requested.emit)
        menu_monitor.addAction(accion_refrescar)

        # Menú Ayuda
        menu_ayuda = menubar.addMenu("&Ayuda")

        accion_acerca = QAction("&Acerca de...", self)
        accion_acerca.triggered.connect(self._mostrar_acerca)
        menu_ayuda.addAction(accion_acerca)

    def _mostrar_config(self):
        """Muestra el diálogo de configuración."""
        dialog = ConfigDialog(self)

        # Cargar valores actuales (si existen)
        # Esto debería venir del controlador, pero lo dejamos simple por ahora
        dialog.set_carpeta_scanner("C:\\scan\\entrada")
        dialog.set_carpeta_salida("C:\\albaranes")
        dialog.set_carpeta_errores("C:\\albaranes\\errores")

        if dialog.exec():
            # Emitir señal con nueva configuración
            config = {
                "scanner": dialog.get_carpeta_scanner(),
                "salida": dialog.get_carpeta_salida(),
                "errores": dialog.get_carpeta_errores()
            }
            self.config_changed.emit(config)

    def _mostrar_acerca(self):
        """Muestra el diálogo acerca de."""
        QMessageBox.about(
            self,
            "Acerca de Scanner Sufexa",
            "<h2>Scanner Sufexa v1.0</h2>"
            "<p>Sistema de procesamiento automático de albaranes</p>"
            "<p><b>Características:</b></p>"
            "<ul>"
            "<li>Detección automática de PDFs</li>"
            "<li>OCR con Tesseract</li>"
            "<li>Extracción inteligente de datos</li>"
            "<li>Organización automática por cliente</li>"
            "<li>Prevención de duplicados</li>"
            "</ul>"
            "<p><b>Arquitectura:</b> Domain-Driven Design (DDD)</p>"
            "<p><b>Tecnologías:</b> Python, PySide6, SQLite, Tesseract</p>"
            "<p>© 2026 Scanner Sufexa</p>"
        )

    # Métodos públicos para actualizar la UI

    def actualizar_estado_monitor(self, activo: bool):
        """Actualiza el estado del monitor."""
        self.status_widget.actualizar_estado(activo)

    def actualizar_carpeta(self, carpeta: str):
        """Actualiza la carpeta monitoreada."""
        self.status_widget.actualizar_carpeta(carpeta)

    def actualizar_estadisticas(self, procesados: int, errores: int):
        """Actualiza las estadísticas."""
        self.status_widget.actualizar_estadisticas(procesados, errores)

    def agregar_albaran(self, id_albaran, cliente, numero, fecha, fecha_proc):
        """Agrega un albarán a la tabla."""
        self.albaran_table.agregar_albaran(
            id_albaran, cliente, numero, fecha, fecha_proc
        )

    def actualizar_ranking(self, clientes: list):
        """Actualiza el ranking de clientes."""
        self.ranking_widget.actualizar_ranking(clientes)

    def log_info(self, mensaje: str):
        """Añade un log INFO."""
        self.error_log.log_info(mensaje)

    def log_warning(self, mensaje: str):
        """Añade un log WARNING."""
        self.error_log.log_warning(mensaje)

    def log_error(self, mensaje: str):
        """Añade un log ERROR."""
        self.error_log.log_error(mensaje)

    def log_success(self, mensaje: str):
        """Añade un log SUCCESS."""
        self.error_log.log_success(mensaje)

    def mostrar_error(self, titulo: str, mensaje: str):
        """Muestra un diálogo de error."""
        QMessageBox.critical(self, titulo, mensaje)

    def mostrar_info(self, titulo: str, mensaje: str):
        """Muestra un diálogo de información."""
        QMessageBox.information(self, titulo, mensaje)
