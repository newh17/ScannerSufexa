"""
Widget para mostrar la tabla de albaranes procesados.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QFrame
)
from PySide6.QtCore import Qt
from datetime import datetime


class AlbaranTableWidget(QWidget):
    """
    Widget que muestra una tabla de albaranes procesados.

    Columnas:
    - ID
    - Cliente
    - Número
    - Fecha
    - Procesado
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("Albaranes Procesados")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linea)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Número", "Fecha", "Procesado"
        ])

        # Configurar tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Cliente
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Número
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Fecha
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Procesado

        layout.addWidget(self.table)

    def agregar_albaran(
        self,
        id_albaran: int,
        cliente: str,
        numero: int,
        fecha: str,
        fecha_procesamiento: datetime
    ):
        """Agrega un albarán a la tabla."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # ID
        item_id = QTableWidgetItem(str(id_albaran))
        item_id.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item_id)

        # Cliente
        item_cliente = QTableWidgetItem(cliente)
        self.table.setItem(row, 1, item_cliente)

        # Número
        item_numero = QTableWidgetItem(str(numero))
        item_numero.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, item_numero)

        # Fecha
        item_fecha = QTableWidgetItem(fecha)
        item_fecha.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, item_fecha)

        # Procesado
        fecha_proc_str = fecha_procesamiento.strftime("%d/%m/%Y %H:%M")
        item_procesado = QTableWidgetItem(fecha_proc_str)
        item_procesado.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, item_procesado)

        # Scroll al final
        self.table.scrollToBottom()

    def limpiar(self):
        """Limpia la tabla."""
        self.table.setRowCount(0)

    def get_total_albaranes(self) -> int:
        """Retorna el número total de albaranes."""
        return self.table.rowCount()
