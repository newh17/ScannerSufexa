"""
Implementación SQLite del repositorio de clientes.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from domain.entities import Cliente
from domain.repositories import IClienteRepository
from infrastructure.persistence.database import Database


class SQLiteClienteRepository(IClienteRepository):
    """
    Implementación del repositorio de clientes usando SQLite.

    Implementa la interface IClienteRepository definida en el dominio.
    """

    def __init__(self, database: Database):
        """
        Inicializa el repositorio.

        Args:
            database: Instancia del servicio de base de datos
        """
        self.db = database

    def save(self, cliente: Cliente) -> Cliente:
        """
        Guarda o actualiza un cliente.

        Si el cliente ya existe (mismo nombre), actualiza el contador.
        Si no existe, lo crea.

        Args:
            cliente: Cliente a guardar

        Returns:
            Cliente: Cliente guardado con ID asignado
        """
        # Buscar si ya existe
        existente = self.find_by_nombre(cliente.nombre)

        if existente:
            # Actualizar cliente existente
            cliente.id = existente.id
            self._update(cliente)
        else:
            # Crear nuevo cliente
            cliente_id = self._insert(cliente)
            cliente.id = cliente_id

        return cliente

    def _insert(self, cliente: Cliente) -> int:
        """Inserta un nuevo cliente y retorna su ID."""
        query = """
        INSERT INTO clientes (
            nombre,
            total_albaranes,
            fecha_ultimo_albaran,
            fecha_creacion
        ) VALUES (?, ?, ?, ?)
        """

        fecha_creacion_iso = cliente.fecha_creacion.isoformat()
        fecha_ultimo_iso = (
            cliente.fecha_ultimo_albaran.isoformat()
            if cliente.fecha_ultimo_albaran
            else None
        )

        params = (
            cliente.nombre,
            cliente.total_albaranes,
            fecha_ultimo_iso,
            fecha_creacion_iso,
        )

        return self.db.execute_insert(query, params)

    def _update(self, cliente: Cliente):
        """Actualiza un cliente existente."""
        query = """
        UPDATE clientes
        SET total_albaranes = ?,
            fecha_ultimo_albaran = ?
        WHERE id = ?
        """

        fecha_ultimo_iso = (
            cliente.fecha_ultimo_albaran.isoformat()
            if cliente.fecha_ultimo_albaran
            else None
        )

        params = (
            cliente.total_albaranes,
            fecha_ultimo_iso,
            cliente.id,
        )

        self.db.execute_update(query, params)

    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Busca un cliente por ID."""
        query = "SELECT * FROM clientes WHERE id = ?"
        rows = self.db.execute_query(query, (cliente_id,))

        if not rows:
            return None

        return self._row_to_entity(rows[0])

    def find_by_nombre(self, nombre: str) -> Optional[Cliente]:
        """Busca un cliente por nombre exacto."""
        query = "SELECT * FROM clientes WHERE nombre = ?"
        rows = self.db.execute_query(query, (nombre,))

        if not rows:
            return None

        return self._row_to_entity(rows[0])

    def get_all(self) -> List[Cliente]:
        """Obtiene todos los clientes."""
        query = "SELECT * FROM clientes ORDER BY nombre"
        rows = self.db.execute_query(query)

        return [self._row_to_entity(row) for row in rows]

    def get_ranking(self, top_n: int = 10) -> List[Cliente]:
        """
        Obtiene el ranking de clientes por número de albaranes.

        Args:
            top_n: Número de clientes a retornar

        Returns:
            List[Cliente]: Clientes ordenados por total_albaranes DESC
        """
        query = """
        SELECT * FROM clientes
        ORDER BY total_albaranes DESC, nombre ASC
        LIMIT ?
        """
        rows = self.db.execute_query(query, (top_n,))

        return [self._row_to_entity(row) for row in rows]

    def count(self) -> int:
        """Cuenta el total de clientes."""
        query = "SELECT COUNT(*) as total FROM clientes"
        rows = self.db.execute_query(query)
        return rows[0]["total"]

    def _row_to_entity(self, row: sqlite3.Row) -> Cliente:
        """
        Convierte una fila de BD a entidad Cliente.

        Args:
            row: Fila de SQLite

        Returns:
            Cliente: Entidad del dominio
        """
        # Parsear fechas
        fecha_creacion = datetime.fromisoformat(row["fecha_creacion"])
        fecha_ultimo_albaran = (
            datetime.fromisoformat(row["fecha_ultimo_albaran"])
            if row["fecha_ultimo_albaran"]
            else None
        )

        # Crear entidad (sin validaciones porque viene de BD confiable)
        cliente = Cliente.__new__(Cliente)
        cliente.id = row["id"]
        cliente.nombre = row["nombre"]
        cliente.total_albaranes = row["total_albaranes"]
        cliente.fecha_ultimo_albaran = fecha_ultimo_albaran
        cliente.fecha_creacion = fecha_creacion

        return cliente
