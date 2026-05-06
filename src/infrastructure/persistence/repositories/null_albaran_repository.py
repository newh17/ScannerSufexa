"""
Repositorio de albaranes sin persistencia (Null Object Pattern).

Úsalo cuando quieras desactivar la base de datos temporalmente.
"""

from typing import List, Optional

from domain.entities import Albaran
from domain.value_objects import FechaAlbaran, NumeroAlbaran
from domain.repositories import IAlbaranRepository


class NullAlbaranRepository(IAlbaranRepository):
    """Repositorio que no persiste nada. Nunca detecta duplicados."""

    def save(self, albaran: Albaran) -> Albaran:
        albaran._id = 0
        return albaran

    def find_by_id(self, albaran_id: int) -> Optional[Albaran]:
        return None

    def find_by_numero_y_fecha(
        self,
        numero: NumeroAlbaran,
        fecha: FechaAlbaran
    ) -> Optional[Albaran]:
        return None

    def exists(self, numero: NumeroAlbaran, fecha: FechaAlbaran) -> bool:
        return False

    def get_all(self, limite: Optional[int] = None) -> List[Albaran]:
        return []

    def count(self) -> int:
        return 0
