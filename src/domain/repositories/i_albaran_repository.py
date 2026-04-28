"""
Interface del repositorio de albaranes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Albaran
from ..value_objects import FechaAlbaran, NumeroAlbaran


class IAlbaranRepository(ABC):
    """
    Interface que define el contrato para el repositorio de albaranes.

    El dominio define QUÉ operaciones necesita, pero no CÓMO se implementan.
    La infraestructura se encargará de la implementación concreta.
    """

    @abstractmethod
    def save(self, albaran: Albaran) -> Albaran:
        """
        Guarda un albarán en el repositorio.

        Args:
            albaran: Albarán a guardar

        Returns:
            Albaran: Albarán guardado con ID asignado

        Raises:
            AlbaranDuplicadoException: Si ya existe un albarán con mismo número y fecha
        """
        pass

    @abstractmethod
    def find_by_id(self, albaran_id: int) -> Optional[Albaran]:
        """
        Busca un albarán por su ID.

        Args:
            albaran_id: ID del albarán

        Returns:
            Optional[Albaran]: Albarán encontrado o None
        """
        pass

    @abstractmethod
    def find_by_numero_y_fecha(
        self,
        numero: NumeroAlbaran,
        fecha: FechaAlbaran
    ) -> Optional[Albaran]:
        """
        Busca un albarán por número y fecha.

        Args:
            numero: Número del albarán
            fecha: Fecha del albarán

        Returns:
            Optional[Albaran]: Albarán encontrado o None
        """
        pass

    @abstractmethod
    def exists(self, numero: NumeroAlbaran, fecha: FechaAlbaran) -> bool:
        """
        Verifica si existe un albarán con el número y fecha dados.

        Args:
            numero: Número del albarán
            fecha: Fecha del albarán

        Returns:
            bool: True si existe, False en caso contrario
        """
        pass

    @abstractmethod
    def get_all(self, limite: Optional[int] = None) -> List[Albaran]:
        """
        Obtiene todos los albaranes.

        Args:
            limite: Número máximo de albaranes a retornar (opcional)

        Returns:
            List[Albaran]: Lista de albaranes
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Cuenta el total de albaranes.

        Returns:
            int: Número total de albaranes
        """
        pass
