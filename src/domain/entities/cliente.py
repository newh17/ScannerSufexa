"""
Entidad Cliente del dominio.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..exceptions import ClienteInvalidoException


@dataclass
class Cliente:
    """
    Entidad que representa un cliente.

    Reglas de negocio:
    - El nombre no puede estar vacío
    - El nombre se normaliza para uso en sistema de archivos
    - Se mantiene un contador de albaranes procesados
    - Se registra la fecha del último albarán
    """

    nombre: str
    id: Optional[int] = None
    total_albaranes: int = 0
    fecha_ultimo_albaran: Optional[datetime] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Valida y normaliza el cliente al crearlo."""
        self._validar()
        self._normalizar_nombre()

    def _validar(self):
        """Valida las reglas de negocio del cliente."""
        if not self.nombre or not self.nombre.strip():
            raise ClienteInvalidoException(
                self.nombre,
                "El nombre no puede estar vacío"
            )

        if len(self.nombre.strip()) < 2:
            raise ClienteInvalidoException(
                self.nombre,
                "El nombre debe tener al menos 2 caracteres"
            )

    def _normalizar_nombre(self):
        """Normaliza el nombre eliminando espacios extra."""
        self.nombre = " ".join(self.nombre.split())

    def incrementar_contador(self, fecha_albaran: datetime):
        """
        Incrementa el contador de albaranes y actualiza la última fecha.

        Args:
            fecha_albaran: Fecha del albarán procesado
        """
        self.total_albaranes += 1
        if (
            self.fecha_ultimo_albaran is None
            or fecha_albaran > self.fecha_ultimo_albaran
        ):
            self.fecha_ultimo_albaran = fecha_albaran

    def get_nombre_carpeta(self) -> str:
        """
        Genera el nombre de carpeta seguro para el sistema de archivos.

        Returns:
            str: Nombre sanitizado para usar como carpeta

        Ejemplo:
            "METALCRISMAR, S.L." -> "METALCRISMAR, S.L"
        """
        # Eliminar caracteres no permitidos en Windows: < > : " / \ | ? *
        nombre_limpio = re.sub(r'[<>:"/\\|?*]', '', self.nombre)

        # Eliminar espacios al final
        nombre_limpio = nombre_limpio.rstrip()

        # Limitar longitud (Windows tiene límite de 255 caracteres)
        if len(nombre_limpio) > 200:
            nombre_limpio = nombre_limpio[:200].rstrip()

        return nombre_limpio

    def __eq__(self, other):
        """Dos clientes son iguales si tienen el mismo nombre."""
        if not isinstance(other, Cliente):
            return False
        return self.nombre == other.nombre

    def __hash__(self):
        """Hash basado en el nombre del cliente."""
        return hash(self.nombre)

    def __str__(self):
        return f"Cliente({self.nombre}, {self.total_albaranes} albaranes)"
