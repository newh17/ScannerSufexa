"""
Modelo de base de datos para Albaran.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AlbaranModel:
    """
    Modelo que representa la tabla 'albaranes' en SQLite.

    Este es el modelo de persistencia (cómo se guarda en BD),
    separado de la entidad del dominio (lógica de negocio).
    """

    numero: int
    fecha: str  # Formato: DD/MM/YYYY
    cliente_nombre: str
    ruta_archivo_original: str
    ruta_archivo_final: Optional[str] = None
    fecha_procesamiento: str = ""  # Formato ISO: YYYY-MM-DD HH:MM:SS
    id: Optional[int] = None

    @staticmethod
    def get_create_table_sql() -> str:
        """
        Devuelve el SQL para crear la tabla de albaranes.

        Returns:
            str: Statement SQL CREATE TABLE
        """
        return """
        CREATE TABLE IF NOT EXISTS albaranes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            cliente_nombre TEXT NOT NULL,
            ruta_archivo_original TEXT NOT NULL,
            ruta_archivo_final TEXT,
            fecha_procesamiento TEXT NOT NULL,
            UNIQUE(numero, fecha)
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
            """CREATE UNIQUE INDEX IF NOT EXISTS idx_albaran_unico
               ON albaranes(numero, fecha)""",
            """CREATE INDEX IF NOT EXISTS idx_albaran_cliente
               ON albaranes(cliente_nombre)""",
            """CREATE INDEX IF NOT EXISTS idx_albaran_fecha_procesamiento
               ON albaranes(fecha_procesamiento DESC)""",
        ]

    @staticmethod
    def to_dict(model: "AlbaranModel") -> dict:
        """
        Convierte el modelo a diccionario para insertar en BD.

        Args:
            model: Instancia del modelo

        Returns:
            dict: Diccionario con los campos
        """
        return {
            "numero": model.numero,
            "fecha": model.fecha,
            "cliente_nombre": model.cliente_nombre,
            "ruta_archivo_original": model.ruta_archivo_original,
            "ruta_archivo_final": model.ruta_archivo_final,
            "fecha_procesamiento": model.fecha_procesamiento,
        }
