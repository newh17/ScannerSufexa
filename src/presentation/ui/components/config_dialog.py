"""
Diálogo de configuración.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt


class ConfigDialog(QDialog):
    """
    Diálogo para configurar las rutas del sistema.

    Permite configurar:
    - Carpeta de entrada (scanner)
    - Carpeta de salida (albaranes)
    - Carpeta de errores
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙ Configuración")
        self.setMinimumWidth(600)
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)

        # Grupo de carpetas
        grupo_carpetas = QGroupBox("Carpetas del Sistema")
        form = QFormLayout(grupo_carpetas)

        # Carpeta de entrada
        self.input_scanner = QLineEdit()
        btn_scanner = QPushButton("📁 Buscar")
        btn_scanner.clicked.connect(
            lambda: self._seleccionar_carpeta(self.input_scanner)
        )

        layout_scanner = QHBoxLayout()
        layout_scanner.addWidget(self.input_scanner)
        layout_scanner.addWidget(btn_scanner)

        form.addRow("Carpeta Scanner:", layout_scanner)

        # Carpeta de salida
        self.input_salida = QLineEdit()
        btn_salida = QPushButton("📁 Buscar")
        btn_salida.clicked.connect(
            lambda: self._seleccionar_carpeta(self.input_salida)
        )

        layout_salida = QHBoxLayout()
        layout_salida.addWidget(self.input_salida)
        layout_salida.addWidget(btn_salida)

        form.addRow("Carpeta Albaranes:", layout_salida)

        # Carpeta de errores
        self.input_errores = QLineEdit()
        btn_errores = QPushButton("📁 Buscar")
        btn_errores.clicked.connect(
            lambda: self._seleccionar_carpeta(self.input_errores)
        )

        layout_errores = QHBoxLayout()
        layout_errores.addWidget(self.input_errores)
        layout_errores.addWidget(btn_errores)

        form.addRow("Carpeta Errores:", layout_errores)

        layout.addWidget(grupo_carpetas)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)

        btn_guardar = QPushButton("✔ Guardar")
        btn_guardar.setStyleSheet("""
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
        """)
        btn_guardar.clicked.connect(self.accept)
        botones_layout.addWidget(btn_guardar)

        layout.addLayout(botones_layout)

    def _seleccionar_carpeta(self, line_edit: QLineEdit):
        """Abre un diálogo para seleccionar carpeta."""
        carpeta = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Carpeta",
            line_edit.text()
        )

        if carpeta:
            line_edit.setText(carpeta)

    def set_carpeta_scanner(self, carpeta: str):
        """Establece la carpeta del scanner."""
        self.input_scanner.setText(carpeta)

    def set_carpeta_salida(self, carpeta: str):
        """Establece la carpeta de salida."""
        self.input_salida.setText(carpeta)

    def set_carpeta_errores(self, carpeta: str):
        """Establece la carpeta de errores."""
        self.input_errores.setText(carpeta)

    def get_carpeta_scanner(self) -> str:
        """Obtiene la carpeta del scanner."""
        return self.input_scanner.text()

    def get_carpeta_salida(self) -> str:
        """Obtiene la carpeta de salida."""
        return self.input_salida.text()

    def get_carpeta_errores(self) -> str:
        """Obtiene la carpeta de errores."""
        return self.input_errores.text()
