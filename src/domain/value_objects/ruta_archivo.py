"""
Value Object para representar rutas de archivo seguras.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from ..exceptions import DatosInvalidosException


@dataclass(frozen=True)
class RutaArchivo:
    """
    Value Object inmutable que representa una ruta de archivo segura.

    Validaciones:
    - No contiene caracteres inválidos para Windows
    - Longitud razonable
    - No contiene secuencias peligrosas (.., etc.)
    """

    valor: str

    # Caracteres no permitidos en nombres de archivo Windows
    CARACTERES_INVALIDOS = r'[<>:"|?*]'
    MAX_LONGITUD_NOMBRE = 255

    def __post_init__(self):
        """Valida la ruta al crear el objeto."""
        self._validar()

    def _validar(self):
        """Valida que la ruta sea segura."""
        if not self.valor or not self.valor.strip():
            raise DatosInvalidosException(
                "ruta_archivo",
                self.valor,
                "La ruta no puede estar vacía"
            )

        # Obtener solo el nombre del archivo (sin directorio)
        nombre_archivo = Path(self.valor).name

        # Validar caracteres inválidos
        if re.search(self.CARACTERES_INVALIDOS, nombre_archivo):
            raise DatosInvalidosException(
                "ruta_archivo",
                self.valor,
                f"Contiene caracteres inválidos: {self.CARACTERES_INVALIDOS}"
            )

        # Validar longitud
        if len(nombre_archivo) > self.MAX_LONGITUD_NOMBRE:
            raise DatosInvalidosException(
                "ruta_archivo",
                self.valor,
                f"El nombre excede {self.MAX_LONGITUD_NOMBRE} caracteres"
            )

        # Validar que no contenga secuencias peligrosas
        if ".." in self.valor:
            raise DatosInvalidosException(
                "ruta_archivo",
                self.valor,
                "No puede contener secuencias de directorio padre (..)"
            )

    def __str__(self) -> str:
        return self.valor

    def to_path(self) -> Path:
        """
        Convierte a objeto Path.

        Returns:
            Path: Objeto Path correspondiente
        """
        return Path(self.valor)

    @staticmethod
    def sanitize(nombre: str) -> str:
        """
        Sanitiza un nombre eliminando caracteres peligrosos.

        Args:
            nombre: Nombre a sanitizar

        Returns:
            str: Nombre sanitizado
        """
        # Reemplazar caracteres inválidos por guión bajo
        nombre_limpio = re.sub(RutaArchivo.CARACTERES_INVALIDOS, "_", nombre)

        # Eliminar espacios múltiples
        nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio)

        # Eliminar espacios al inicio y final
        nombre_limpio = nombre_limpio.strip()

        return nombre_limpio
