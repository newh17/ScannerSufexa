"""
Implementación SQLite del repositorio de albaranes.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from domain.entities import Albaran, Cliente
from domain.value_objects import FechaAlbaran, NumeroAlbaran
from domain.repositories import IAlbaranRepository
from domain.exceptions import AlbaranDuplicadoException
from infrastructure.persistence.database import Database


class SQLiteAlbaranRepository(IAlbaranRepository):
    """
    Implementación del repositorio de albaranes usando SQLite.

    Implementa la interface IAlbaranRepository definida en el dominio.
    Incluye prevención de duplicados mediante índice único.
    """

    def __init__(self, database: Database):
        """
        Inicializa el repositorio.

        Args:
            database: Instancia del servicio de base de datos
        """
        self.db = database

    def save(self, albaran: Albaran) -> Albaran:
        """
        Guarda un albarán.

        Verifica duplicados antes de insertar.

        Args:
            albaran: Albarán a guardar

        Returns:
            Albaran: Albarán guardado con ID asignado

        Raises:
            AlbaranDuplicadoException: Si ya existe un albarán con mismo número y fecha
        """
        # Verificar duplicados
        if self.exists(albaran.numero, albaran.fecha):
            raise AlbaranDuplicadoException(
                int(albaran.numero),
                str(albaran.fecha)
            )

        # Insertar
        albaran_id = self._insert(albaran)
        albaran.id = albaran_id

        return albaran

    def _insert(self, albaran: Albaran) -> int:
        """
        Inserta un nuevo albarán y retorna su ID.

        Raises:
            AlbaranDuplicadoException: Si viola la restricción UNIQUE
        """
        query = """
        INSERT INTO albaranes (
            numero,
            fecha,
            cliente_nombre,
            ruta_archivo_original,
            ruta_archivo_final,
            fecha_procesamiento
        ) VALUES (?, ?, ?, ?, ?, ?)
        """

        fecha_procesamiento_iso = albaran.fecha_procesamiento.isoformat()

        params = (
            int(albaran.numero),
            str(albaran.fecha),
            albaran.cliente.nombre,
            albaran.ruta_archivo_original,
            albaran.ruta_archivo_final,
            fecha_procesamiento_iso,
        )

        try:
            return self.db.execute_insert(query, params)
        except sqlite3.IntegrityError as e:
            # Si falla por duplicado (índice UNIQUE)
            if "UNIQUE constraint failed" in str(e):
                raise AlbaranDuplicadoException(
                    int(albaran.numero),
                    str(albaran.fecha)
                )
            raise

    def find_by_id(self, albaran_id: int) -> Optional[Albaran]:
        """Busca un albarán por ID."""
        query = "SELECT * FROM albaranes WHERE id = ?"
        rows = self.db.execute_query(query, (albaran_id,))

        if not rows:
            return None

        return self._row_to_entity(rows[0])

    def find_by_numero_y_fecha(
        self,
        numero: NumeroAlbaran,
        fecha: FechaAlbaran
    ) -> Optional[Albaran]:
        """Busca un albarán por número y fecha."""
        query = "SELECT * FROM albaranes WHERE numero = ? AND fecha = ?"
        rows = self.db.execute_query(query, (int(numero), str(fecha)))

        if not rows:
            return None

        return self._row_to_entity(rows[0])

    def exists(self, numero: NumeroAlbaran, fecha: FechaAlbaran) -> bool:
        """Verifica si existe un albarán con el número y fecha dados."""
        query = """
        SELECT COUNT(*) as total
        FROM albaranes
        WHERE numero = ? AND fecha = ?
        """
        rows = self.db.execute_query(query, (int(numero), str(fecha)))
        return rows[0]["total"] > 0

    def get_all(self, limite: Optional[int] = None) -> List[Albaran]:
        """Obtiene todos los albaranes."""
        if limite:
            query = """
            SELECT * FROM albaranes
            ORDER BY fecha_procesamiento DESC
            LIMIT ?
            """
            rows = self.db.execute_query(query, (limite,))
        else:
            query = """
            SELECT * FROM albaranes
            ORDER BY fecha_procesamiento DESC
            """
            rows = self.db.execute_query(query)

        return [self._row_to_entity(row) for row in rows]

    def count(self) -> int:
        """Cuenta el total de albaranes."""
        query = "SELECT COUNT(*) as total FROM albaranes"
        rows = self.db.execute_query(query)
        return rows[0]["total"]

    def _row_to_entity(self, row: sqlite3.Row) -> Albaran:
        """
        Convierte una fila de BD a entidad Albaran.

        Args:
            row: Fila de SQLite

        Returns:
            Albaran: Entidad del dominio
        """
        # Parsear fecha de procesamiento
        fecha_procesamiento = datetime.fromisoformat(
            row["fecha_procesamiento"]
        )

        # Crear Value Objects
        numero = NumeroAlbaran(row["numero"])
        fecha = FechaAlbaran(row["fecha"])

        # Crear Cliente (simplificado, solo con nombre)
        cliente = Cliente.__new__(Cliente)
        cliente.nombre = row["cliente_nombre"]
        cliente.total_albaranes = 0  # No se carga aquí

        # Crear Albaran (sin validaciones porque viene de BD confiable)
        albaran = Albaran.__new__(Albaran)
        albaran.id = row["id"]
        albaran.numero = numero
        albaran.fecha = fecha
        albaran.cliente = cliente
        albaran.ruta_archivo_original = row["ruta_archivo_original"]
        albaran.ruta_archivo_final = row["ruta_archivo_final"]
        albaran.fecha_procesamiento = fecha_procesamiento

        return albaran
