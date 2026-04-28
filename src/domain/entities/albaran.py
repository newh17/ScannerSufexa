"""
Entidad Albaran del dominio.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import FechaAlbaran, NumeroAlbaran, RutaArchivo
from .cliente import Cliente


@dataclass
class Albaran:
    """
    Entidad que representa un albarán.

    Reglas de negocio:
    - Siempre debe tener cliente, fecha y número
    - La combinación de número + fecha debe ser única
    - Genera automáticamente el nombre del archivo
    - Registra cuándo fue procesado
    """

    cliente: Cliente
    fecha: FechaAlbaran
    numero: NumeroAlbaran
    ruta_archivo_original: str
    id: Optional[int] = None
    ruta_archivo_final: Optional[str] = None
    fecha_procesamiento: datetime = field(default_factory=datetime.now)

    def generar_nombre_archivo(self) -> str:
        """
        Genera el nombre del archivo según el formato especificado.

        Formato: CLIENTE_FECHA_NUMERO.pdf

        Returns:
            str: Nombre del archivo (ej: "METALCRISMAR, S.L_23-01-2026_71206.pdf")
        """
        nombre_cliente = self.cliente.get_nombre_carpeta()
        fecha_formateada = self.fecha.to_filename_format()
        numero = str(self.numero)

        nombre = f"{nombre_cliente}_{fecha_formateada}_{numero}.pdf"

        # Validar que el nombre sea seguro
        RutaArchivo(nombre)

        return nombre

    def get_carpeta_destino(self) -> str:
        """
        Obtiene el nombre de la carpeta destino del cliente.

        Returns:
            str: Nombre de la carpeta del cliente
        """
        return self.cliente.get_nombre_carpeta()

    def marcar_como_procesado(self, ruta_final: str):
        """
        Marca el albarán como procesado y guarda la ruta final.

        Args:
            ruta_final: Ruta donde quedó guardado el archivo
        """
        self.ruta_archivo_final = ruta_final
        self.fecha_procesamiento = datetime.now()

    def __eq__(self, other):
        """
        Dos albaranes son iguales si tienen el mismo número y fecha.
        """
        if not isinstance(other, Albaran):
            return False
        return (
            self.numero == other.numero
            and self.fecha == other.fecha
        )

    def __hash__(self):
        """Hash basado en número y fecha."""
        return hash((self.numero.valor, self.fecha.valor))

    def __str__(self):
        return (
            f"Albaran(#{self.numero}, {self.fecha}, "
            f"{self.cliente.nombre})"
        )
