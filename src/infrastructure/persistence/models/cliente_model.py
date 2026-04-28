"""
Modelo de base de datos para Cliente.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ClienteModel:
    """
    Modelo que representa la tabla 'clientes' en SQLite.

    Este es el modelo de persistencia (cómo se guarda en BD),
    separado de la entidad del dominio (lógica de negocio).
    """

    nombre: str
    total_albaranes: int = 0
    fecha_ultimo_albaran: Optional[str] = None  # Formato ISO: YYYY-MM-DD HH:MM:SS
    fecha_creacion: str = ""  # Formato ISO
    id: Optional[int] = None

    @staticmethod
    def get_create_table_sql() -> str:
        """
        Devuelve el SQL para crear la tabla de clientes.

        Returns:
            str: Statement SQL CREATE TABLE
        """
        return """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            total_albaranes INTEGER NOT NULL DEFAULT 0,
            fecha_ultimo_albaran TEXT,
            fecha_creacion TEXT NOT NULL
        )
        """

    @staticmethod
    def get_index_sql() -> list:
        """
        Devuelve las sentencias SQL para crear índices en la tabla.

        Returns:
            list: Lista de statements SQL CREATE INDEX
        """
        return [
            """CREATE INDEX IF NOT EXISTS idx_cliente_nombre
               ON clientes(nombre)""",
            """CREATE INDEX IF NOT EXISTS idx_cliente_total_albaranes
               ON clientes(total_albaranes DESC)""",
        ]

    @staticmethod
    def to_dict(model: "ClienteModel") -> dict:
        """
        Convierte el modelo a diccionario para insertar en BD.

        Args:
            model: Instancia del modelo

        Returns:
            dict: Diccionario con los campos
        """
        return {
            "nombre": model.nombre,
            "total_albaranes": model.total_albaranes,
            "fecha_ultimo_albaran": model.fecha_ultimo_albaran,
            "fecha_creacion": model.fecha_creacion,
        }
