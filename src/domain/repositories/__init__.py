"""
Interfaces de repositorios del dominio.
"""

from .i_albaran_repository import IAlbaranRepository
from .i_cliente_repository import IClienteRepository

__all__ = [
    "IAlbaranRepository",
    "IClienteRepository",
]
