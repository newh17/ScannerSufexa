"""
Widget para mostrar el ranking de clientes.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QFrame
)
from PySide6.QtCore import Qt


class RankingWidget(QWidget):
    """
    Widget que muestra el ranking de clientes por número de albaranes.

    Columnas:
    - Posición
    - Cliente
    - Total Albaranes
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("🏆 Ranking de Clientes")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linea)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "#", "Cliente", "Albaranes"
        ])

        # Configurar tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Posición
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Cliente
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Total

        layout.addWidget(self.table)

    def actualizar_ranking(self, clientes: list):
        """
        Actualiza el ranking con una lista de clientes.

        Args:
            clientes: Lista de tuplas (nombre, total_albaranes)
        """
        self.table.setRowCount(0)

        for i, (nombre, total) in enumerate(clientes, 1):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Posición
            item_pos = QTableWidgetItem(str(i))
            item_pos.setTextAlignment(Qt.AlignCenter)

            # Medalla para top 3
            if i == 1:
                item_pos.setText("🥇")
            elif i == 2:
                item_pos.setText("🥈")
            elif i == 3:
                item_pos.setText("🥉")

            self.table.setItem(row, 0, item_pos)

            # Cliente
            item_cliente = QTableWidgetItem(nombre)
            self.table.setItem(row, 1, item_cliente)

            # Total
            item_total = QTableWidgetItem(str(total))
            item_total.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_total)

    def limpiar(self):
        """Limpia el ranking."""
        self.table.setRowCount(0)
