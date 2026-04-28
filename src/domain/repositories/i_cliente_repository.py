"""
Interface del repositorio de clientes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Cliente


class IClienteRepository(ABC):
    """
    Interface que define el contrato para el repositorio de clientes.

    El dominio define QUÉ operaciones necesita, pero no CÓMO se implementan.
    La infraestructura se encargará de la implementación concreta.
    """

    @abstractmethod
    def save(self, cliente: Cliente) -> Cliente:
        """
        Guarda un cliente en el repositorio.

        Si el cliente ya existe (mismo nombre), se actualiza.
        Si no existe, se crea uno nuevo.

        Args:
            cliente: Cliente a guardar

        Returns:
            Cliente: Cliente guardado con ID asignado
        """
        pass

    @abstractmethod
    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """
        Busca un cliente por su ID.

        Args:
            cliente_id: ID del cliente

        Returns:
            Optional[Cliente]: Cliente encontrado o None
        """
        pass

    @abstractmethod
    def find_by_nombre(self, nombre: str) -> Optional[Cliente]:
        """
        Busca un cliente por su nombre.

        Args:
            nombre: Nombre del cliente

        Returns:
            Optional[Cliente]: Cliente encontrado o None
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Cliente]:
        """
        Obtiene todos los clientes.

        Returns:
            List[Cliente]: Lista de clientes
        """
        pass

    @abstractmethod
    def get_ranking(self, top_n: int = 10) -> List[Cliente]:
        """
        Obtiene el ranking de clientes por número de albaranes.

        Args:
            top_n: Número de clientes a retornar

        Returns:
            List[Cliente]: Lista de clientes ordenados por total_albaranes DESC
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Cuenta el total de clientes.

        Returns:
            int: Número total de clientes
        """
        pass
