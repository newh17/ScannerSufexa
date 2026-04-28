"""
Servicio de gestión de la base de datos SQLite.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .models import AlbaranModel, ClienteModel


class Database:
    """
    Servicio que gestiona la conexión y configuración de la base de datos.

    Responsabilidades:
    - Crear y mantener la conexión a SQLite
    - Crear las tablas si no existen
    - Proporcionar acceso a la conexión para los repositorios
    - Gestionar transacciones
    """

    def __init__(self, db_path: str):
        """
        Inicializa el servicio de base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._ensure_db_directory()

    def _ensure_db_directory(self):
        """Crea el directorio de la BD si no existe."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def connect(self):
        """
        Establece la conexión con la base de datos.

        Configura el modo de fila para obtener resultados como diccionarios.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # Permite uso en múltiples threads
            )
            # Configurar para obtener filas como diccionarios
            self._connection.row_factory = sqlite3.Row
            # Habilitar foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")

    def disconnect(self):
        """Cierra la conexión con la base de datos."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def get_connection(self) -> sqlite3.Connection:
        """
        Obtiene la conexión activa.

        Returns:
            sqlite3.Connection: Conexión a la base de datos

        Raises:
            RuntimeError: Si no hay conexión activa
        """
        if self._connection is None:
            raise RuntimeError(
                "No hay conexión activa. Ejecuta connect() primero."
            )
        return self._connection

    @contextmanager
    def transaction(self):
        """
        Context manager para manejar transacciones.

        Uso:
            with db.transaction():
                # operaciones en BD
                # si hay excepción, se hace rollback automático
                # si sale sin excepción, se hace commit automático

        Yields:
            sqlite3.Connection: Conexión a la base de datos
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def initialize_schema(self):
        """
        Crea las tablas e índices si no existen.

        Este método es idempotente (se puede ejecutar múltiples veces).
        """
        self.connect()
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Crear tabla de clientes
            cursor.execute(ClienteModel.get_create_table_sql())
            for index_sql in ClienteModel.get_index_sql():
                cursor.execute(index_sql)

            # Crear tabla de albaranes
            cursor.execute(AlbaranModel.get_create_table_sql())
            for index_sql in AlbaranModel.get_index_sql():
                cursor.execute(index_sql)

            conn.commit()

        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al inicializar el esquema: {e}")

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Ejecuta una query SELECT y retorna los resultados.

        Args:
            query: Query SQL
            params: Parámetros para la query (opcional)

        Returns:
            list: Lista de filas (como Row objects)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta una query INSERT y retorna el ID generado.

        Args:
            query: Query SQL INSERT
            params: Parámetros para la query

        Returns:
            int: ID del registro insertado
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta una query UPDATE/DELETE y retorna filas afectadas.

        Args:
            query: Query SQL UPDATE/DELETE
            params: Parámetros para la query

        Returns:
            int: Número de filas afectadas
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

    def __enter__(self):
        """Permite usar Database como context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        self.disconnect()
