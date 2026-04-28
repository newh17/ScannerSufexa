"""
Widget para mostrar el log de errores.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QFrame, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from datetime import datetime


class ErrorLogWidget(QWidget):
    """
    Widget que muestra un log de errores en tiempo real.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_lines = 1000  # Máximo de líneas en el log
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)

        # Cabecera con título y botón limpiar
        header_layout = QHBoxLayout()

        titulo = QLabel("📋 Log de Eventos")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(titulo)

        header_layout.addStretch()

        btn_limpiar = QPushButton("🗑 Limpiar")
        btn_limpiar.clicked.connect(self.limpiar)
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        header_layout.addWidget(btn_limpiar)

        layout.addLayout(header_layout)

        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linea)

        # Text edit para el log
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.text_log)

    def agregar_log(self, nivel: str, mensaje: str):
        """
        Agrega una línea al log.

        Args:
            nivel: Nivel del log (INFO, WARNING, ERROR, etc.)
            mensaje: Mensaje a mostrar
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color según nivel
        colores = {
            "INFO": "#3498db",     # Azul
            "WARNING": "#f39c12",  # Naranja
            "ERROR": "#e74c3c",    # Rojo
            "SUCCESS": "#2ecc71",  # Verde
            "DEBUG": "#95a5a6",    # Gris
        }

        color = colores.get(nivel, "#d4d4d4")

        # Formatear línea
        linea = (
            f'<span style="color: #7f8c8d;">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">{nivel:8}</span> '
            f'<span style="color: #d4d4d4;">{mensaje}</span>'
        )

        self.text_log.append(linea)

        # Limitar número de líneas
        document = self.text_log.document()
        if document.blockCount() > self.max_lines:
            cursor = self.text_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # Eliminar el salto de línea

        # Auto-scroll al final
        self.text_log.verticalScrollBar().setValue(
            self.text_log.verticalScrollBar().maximum()
        )

    def log_info(self, mensaje: str):
        """Log nivel INFO."""
        self.agregar_log("INFO", mensaje)

    def log_warning(self, mensaje: str):
        """Log nivel WARNING."""
        self.agregar_log("WARNING", mensaje)

    def log_error(self, mensaje: str):
        """Log nivel ERROR."""
        self.agregar_log("ERROR", mensaje)

    def log_success(self, mensaje: str):
        """Log nivel SUCCESS."""
        self.agregar_log("SUCCESS", mensaje)

    def log_debug(self, mensaje: str):
        """Log nivel DEBUG."""
        self.agregar_log("DEBUG", mensaje)

    def limpiar(self):
        """Limpia el log."""
        self.text_log.clear()
