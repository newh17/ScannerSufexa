"""
Repositorio de clientes sin persistencia (Null Object Pattern).

Úsalo cuando quieras desactivar la base de datos temporalmente.
"""

from typing import List, Optional

from domain.entities import Cliente
from domain.repositories import IClienteRepository


class NullClienteRepository(IClienteRepository):
    """Repositorio que no persiste nada."""

    def save(self, cliente: Cliente) -> Cliente:
        return cliente

    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        return None

    def find_by_nombre(self, nombre: str) -> Optional[Cliente]:
        return None

    def get_all(self) -> List[Cliente]:
        return []

    def get_ranking(self, top_n: int = 10) -> List[Cliente]:
        return []

    def count(self) -> int:
        return 0
