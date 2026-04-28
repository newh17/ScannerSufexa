"""
Value Object para representar el número de un albarán.
"""

from dataclasses import dataclass

from ..exceptions import DatosInvalidosException


@dataclass(frozen=True)
class NumeroAlbaran:
    """
    Value Object inmutable que representa un número de albarán.

    Validaciones:
    - Debe ser un entero positivo
    - No puede ser cero
    """

    valor: int

    def __post_init__(self):
        """Valida el número al crear el objeto."""
        self._validar()

    def _validar(self):
        """Valida que el número sea correcto."""
        if not isinstance(self.valor, int):
            raise DatosInvalidosException(
                "numero_albaran",
                str(self.valor),
                "Debe ser un número entero"
            )

        if self.valor <= 0:
            raise DatosInvalidosException(
                "numero_albaran",
                str(self.valor),
                "Debe ser un número positivo mayor que cero"
            )

    def __str__(self) -> str:
        return str(self.valor)

    def __int__(self) -> int:
        return self.valor

    @staticmethod
    def from_string(numero_str: str) -> "NumeroAlbaran":
        """
        Crea un NumeroAlbaran desde una cadena de texto.

        Args:
            numero_str: Número como string (ej: "71206")

        Returns:
            NumeroAlbaran: Nueva instancia

        Raises:
            DatosInvalidosException: Si no se puede convertir a entero
        """
        try:
            numero_int = int(numero_str.strip())
            return NumeroAlbaran(numero_int)
        except ValueError:
            raise DatosInvalidosException(
                "numero_albaran",
                numero_str,
                "No se puede convertir a número entero"
            )
