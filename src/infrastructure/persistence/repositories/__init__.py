"""
Implementaciones de repositorios.
"""

from .sqlite_cliente_repository import SQLiteClienteRepository
from .sqlite_albaran_repository import SQLiteAlbaranRepository

__all__ = [
    "SQLiteClienteRepository",
    "SQLiteAlbaranRepository",
]
