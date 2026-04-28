"""
Value Object para representar la fecha de un albarán.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..exceptions import DatosInvalidosException


@dataclass(frozen=True)
class FechaAlbaran:
    """
    Value Object inmutable que representa una fecha de albarán.

    Formato esperado: DD/MM/YYYY
    Validaciones:
    - Formato correcto
    - Fecha no puede ser futura
    - Fecha válida según calendario
    """

    valor: str  # Formato: DD/MM/YYYY

    def __post_init__(self):
        """Valida la fecha al crear el objeto."""
        self._validar()

    def _validar(self):
        """Valida que la fecha sea correcta."""
        # Validar formato
        if not self.valor or len(self.valor) != 10:
            raise DatosInvalidosException(
                "fecha",
                self.valor,
                "El formato debe ser DD/MM/YYYY"
            )

        if self.valor.count("/") != 2:
            raise DatosInvalidosException(
                "fecha",
                self.valor,
                "Debe contener dos barras separadoras"
            )

        # Parsear y validar fecha
        try:
            fecha_obj = datetime.strptime(self.valor, "%d/%m/%Y")
        except ValueError as e:
            raise DatosInvalidosException(
                "fecha",
                self.valor,
                f"Fecha inválida: {str(e)}"
            )

        # Validar que no sea futura
        if fecha_obj > datetime.now():
            raise DatosInvalidosException(
                "fecha",
                self.valor,
                "La fecha no puede ser futura"
            )

    def to_filename_format(self) -> str:
        """
        Convierte la fecha al formato usado en nombres de archivo.

        Returns:
            str: Fecha en formato DD-MM-YYYY
        """
        return self.valor.replace("/", "-")

    def to_datetime(self) -> datetime:
        """
        Convierte a objeto datetime.

        Returns:
            datetime: Objeto datetime correspondiente
        """
        return datetime.strptime(self.valor, "%d/%m/%Y")

    def __str__(self) -> str:
        return self.valor

    @staticmethod
    def from_filename_format(fecha_str: str) -> "FechaAlbaran":
        """
        Crea un FechaAlbaran desde formato de nombre de archivo.

        Args:
            fecha_str: Fecha en formato DD-MM-YYYY

        Returns:
            FechaAlbaran: Nueva instancia
        """
        fecha_normalizada = fecha_str.replace("-", "/")
        return FechaAlbaran(fecha_normalizada)
