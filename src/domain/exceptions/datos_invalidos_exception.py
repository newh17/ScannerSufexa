"""
Excepción lanzada cuando los datos extraídos son inválidos.
"""


class DatosInvalidosException(Exception):
    """Se lanza cuando los datos no cumplen las reglas de negocio."""

    def __init__(self, campo: str, valor: str, razon: str):
        self.campo = campo
        self.valor = valor
        self.razon = razon
        super().__init__(
            f"Dato inválido en campo '{campo}' con valor '{valor}': {razon}"
        )
