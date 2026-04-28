"""
Capa de Dominio.

Contiene la lógica de negocio pura, independiente de frameworks y tecnologías.
"""

from .entities import Albaran, Cliente
from .value_objects import FechaAlbaran, NumeroAlbaran, RutaArchivo
from .repositories import IAlbaranRepository, IClienteRepository
from .exceptions import (
    AlbaranDuplicadoException,
    DatosInvalidosException,
    ClienteInvalidoException,
)

__all__ = [
    # Entidades
    "Albaran",
    "Cliente",
    # Value Objects
    "FechaAlbaran",
    "NumeroAlbaran",
    "RutaArchivo",
    # Repositorios
    "IAlbaranRepository",
    "IClienteRepository",
    # Excepciones
    "AlbaranDuplicadoException",
    "DatosInvalidosException",
    "ClienteInvalidoException",
]
