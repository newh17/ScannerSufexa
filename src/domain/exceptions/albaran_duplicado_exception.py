"""
Excepción lanzada cuando se intenta procesar un albarán duplicado.
"""


class AlbaranDuplicadoException(Exception):
    """Se lanza cuando ya existe un albarán con el mismo número y fecha."""

    def __init__(self, numero: int, fecha: str):
        self.numero = numero
        self.fecha = fecha
        super().__init__(
            f"Ya existe un albarán con número {numero} y fecha {fecha}"
        )
