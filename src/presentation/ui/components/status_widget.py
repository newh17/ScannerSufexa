"""
Widget para mostrar el estado del sistema.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal


class StatusWidget(QWidget):
    """
    Widget que muestra el estado del sistema.

    Muestra:
    - Estado del monitor (Activo/Inactivo)
    - Carpeta monitoreada
    - Archivos procesados
    - Archivos con error
    - Tasa de éxito
    """

    # Señales
    start_clicked = Signal()
    stop_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("Estado del Sistema")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linea)

        # Estado del monitor
        self.label_estado = QLabel("Monitor: <span style='color: red;'>●</span> Inactivo")
        self.label_estado.setTextFormat(Qt.RichText)
        layout.addWidget(self.label_estado)

        # Carpeta monitoreada
        self.label_carpeta = QLabel("Carpeta: -")
        layout.addWidget(self.label_carpeta)

        # Estadísticas
        stats_layout = QHBoxLayout()

        # Procesados
        self.label_procesados = QLabel("✅ Procesados: 0")
        stats_layout.addWidget(self.label_procesados)

        # Errores
        self.label_errores = QLabel("❌ Errores: 0")
        stats_layout.addWidget(self.label_errores)

        # Tasa de éxito
        self.label_tasa = QLabel("📈 Éxito: 0%")
        stats_layout.addWidget(self.label_tasa)

        layout.addLayout(stats_layout)

        # Botones
        botones_layout = QHBoxLayout()

        self.btn_start = QPushButton("▶ Iniciar")
        self.btn_start.clicked.connect(self.start_clicked.emit)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        botones_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⬛ Detener")
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        botones_layout.addWidget(self.btn_stop)

        layout.addLayout(botones_layout)

        layout.addStretch()

    def actualizar_estado(self, activo: bool):
        """Actualiza el estado del monitor."""
        if activo:
            self.label_estado.setText(
                "Monitor: <span style='color: green;'>●</span> Activo"
            )
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        else:
            self.label_estado.setText(
                "Monitor: <span style='color: red;'>●</span> Inactivo"
            )
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def actualizar_carpeta(self, carpeta: str):
        """Actualiza la carpeta monitoreada."""
        self.label_carpeta.setText(f"Carpeta: {carpeta}")

    def actualizar_estadisticas(self, procesados: int, errores: int):
        """Actualiza las estadísticas."""
        self.label_procesados.setText(f"✅ Procesados: {procesados}")
        self.label_errores.setText(f"❌ Errores: {errores}")

        total = procesados + errores
        if total > 0:
            tasa = (procesados / total) * 100
            self.label_tasa.setText(f"📈 Éxito: {tasa:.1f}%")
        else:
            self.label_tasa.setText("📈 Éxito: 0%")
