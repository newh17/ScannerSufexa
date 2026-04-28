"""
Excepción lanzada cuando un cliente no es válido.
"""


class ClienteInvalidoException(Exception):
    """Se lanza cuando el nombre del cliente no cumple las reglas de negocio."""

    def __init__(self, nombre: str, razon: str):
        self.nombre = nombre
        self.razon = razon
        super().__init__(
            f"Cliente inválido '{nombre}': {razon}"
        )
