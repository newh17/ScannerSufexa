"""
Implementaciones de repositorios.
"""

from .sqlite_cliente_repository import SQLiteClienteRepository
from .sqlite_albaran_repository import SQLiteAlbaranRepository
from .null_albaran_repository import NullAlbaranRepository
from .null_cliente_repository import NullClienteRepository

__all__ = [
    "SQLiteClienteRepository",
    "SQLiteAlbaranRepository",
    "NullAlbaranRepository",
    "NullClienteRepository",
]
