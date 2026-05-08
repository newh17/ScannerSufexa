"""
Servicio de lookup de clientes conocidos.

Lee clientes.xlsx (o clientes.csv) junto al .exe.
El nombre del cliente es SIEMPRE el del archivo — nunca el texto crudo del OCR.
Si no se encuentra una coincidencia suficiente, devuelve None y el albarán
va a la carpeta de errores para revisión manual.
"""

import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

try:
    import openpyxl
    _OPENPYXL_OK = True
except ImportError:
    _OPENPYXL_OK = False


def _normalizar(nombre: str) -> str:
    """Elimina puntuación y pasa a mayúsculas para comparar."""
    return re.sub(r'[^A-Z0-9\s]', '', nombre.upper()).strip()


def _tokens(nombre_norm: str) -> set:
    """Palabras significativas (3+ caracteres) del nombre normalizado."""
    return set(t for t in nombre_norm.split() if len(t) >= 3)


class ClienteLookupService:
    """
    Dado el texto OCR extraído, devuelve el nombre EXACTO del Excel.

    Estrategia de puntuación (toma el máximo de las dos):
      - seq_score:   similitud global de cadena (SequenceMatcher)
      - token_score: fracción de palabras del OCR que coinciden con el
                     candidato (denominador = mínimo de ambos conjuntos)

    Si el mejor score supera UMBRAL → devuelve el nombre del Excel.
    Si no → devuelve None (el albarán irá a errores para revisión manual).
    """

    UMBRAL = 0.55   # por debajo de esto el OCR falló demasiado → error manual

    def __init__(self, ruta_csv: Optional[str] = None):
        self._clientes: list[str] = []
        self._clientes_norm: list[str] = []
        self._clientes_tokens: list[set] = []

        ruta = Path(ruta_csv) if ruta_csv else self._ruta_por_defecto()
        self._cargar(ruta)

    # ------------------------------------------------------------------

    def corregir(self, nombre_ocr: str) -> Optional[str]:
        """
        Devuelve el nombre oficial del Excel más parecido al texto OCR,
        o None si la coincidencia es demasiado débil (→ error manual).
        """
        if not nombre_ocr or not self._clientes:
            return None

        nombre_norm = _normalizar(nombre_ocr)
        ocr_tok = _tokens(nombre_norm)

        mejor_score = 0.0
        mejor_nombre = None

        for oficial, oficial_norm, oficial_tok in zip(
            self._clientes, self._clientes_norm, self._clientes_tokens
        ):
            # Similitud global de cadena
            seq = SequenceMatcher(None, nombre_norm, oficial_norm).ratio()

            # Solapamiento de tokens (denominador = el conjunto más pequeño)
            if ocr_tok and oficial_tok:
                comunes = len(ocr_tok & oficial_tok)
                token = comunes / min(len(ocr_tok), len(oficial_tok))
            else:
                token = 0.0

            score = max(seq, token)
            if score > mejor_score:
                mejor_score = score
                mejor_nombre = oficial

        if mejor_score >= self.UMBRAL:
            return mejor_nombre

        return None   # OCR demasiado garbled → irá a errores

    def total_clientes(self) -> int:
        return len(self._clientes)

    def recargar(self):
        ruta = self._ruta_por_defecto()
        self._cargar(ruta)

    # ------------------------------------------------------------------

    def _agregar(self, nombre: str):
        nombre = nombre.strip()
        if not nombre:
            return
        norm = _normalizar(nombre)
        self._clientes.append(nombre)
        self._clientes_norm.append(norm)
        self._clientes_tokens.append(_tokens(norm))

    def _cargar(self, ruta: Path):
        self._clientes = []
        self._clientes_norm = []
        self._clientes_tokens = []

        if not ruta.exists():
            return
        try:
            if ruta.suffix.lower() == '.xlsx':
                self._cargar_xlsx(ruta)
            else:
                self._cargar_txt(ruta)
        except Exception:
            pass

    def _cargar_txt(self, ruta: Path):
        with open(ruta, encoding='utf-8-sig') as f:
            for i, linea in enumerate(f):
                nombre = linea.strip()
                if not nombre:
                    continue
                if i == 0 and nombre.lower() in ('nombre', 'cliente', 'name'):
                    continue
                self._agregar(nombre)

    def _cargar_xlsx(self, ruta: Path):
        if not _OPENPYXL_OK:
            return
        wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
        ws = wb.active
        nombre_col = None
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                for j, cel in enumerate(row):
                    if cel and str(cel).strip().lower() in ('nombre', 'cliente', 'name'):
                        nombre_col = j
                        break
                if nombre_col is None:
                    nombre_col = 0
                    if row[nombre_col]:
                        self._agregar(str(row[nombre_col]))
                continue
            if not row or row[nombre_col] is None:
                continue
            self._agregar(str(row[nombre_col]))
        wb.close()

    @staticmethod
    def _ruta_por_defecto() -> Path:
        bases = [
            Path(__file__).parent.parent.parent.parent,
            Path(__file__).parent.parent.parent.parent.parent,
        ]
        for base in bases:
            for nombre in ("clientes.xlsx", "clientes.csv"):
                ruta = base / nombre
                if ruta.exists():
                    return ruta
        return bases[0] / "clientes.csv"
