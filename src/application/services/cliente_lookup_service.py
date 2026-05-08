"""
Servicio de lookup de clientes conocidos.

Lee clientes.csv junto al .exe y, tras el OCR, busca el nombre más parecido.
Si la similitud supera el umbral, devuelve el nombre oficial del CSV.
"""

import csv
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
    """Quita puntuación y pasa a mayúsculas para comparar."""
    return re.sub(r'[^A-Z0-9\s]', '', nombre.upper()).strip()


class ClienteLookupService:
    """
    Compara el nombre extraído por OCR contra una lista de clientes conocidos.

    El archivo clientes.csv debe estar junto al .exe y tener una columna
    llamada 'nombre' (o simplemente una columna por fila sin cabecera).

    Ejemplo de clientes.csv:
        BC3 COCINAS, S.L.
        CARPINTERIA DIEGO, S.C.
        FUSTERIA SOYCA, S.L.
        JUAN PASCUAL JUAN
        MTG CARPINTEROS, C.B.
        VALENCIA MUEBLES A MEDIDA, S.L.
    """

    UMBRAL_SIMILITUD = 0.82  # 82 % de similitud mínima para aceptar la corrección

    def __init__(self, ruta_csv: Optional[str] = None):
        self._clientes: list[str] = []
        self._clientes_norm: list[str] = []

        ruta = Path(ruta_csv) if ruta_csv else self._ruta_por_defecto()
        self._cargar(ruta)

    # ------------------------------------------------------------------

    def corregir(self, nombre_ocr: str) -> str:
        """
        Devuelve el nombre oficial si hay coincidencia suficiente,
        o el nombre OCR (ya limpiado) si no hay ningún cliente parecido.
        """
        if not nombre_ocr or not self._clientes:
            return nombre_ocr

        nombre_norm = _normalizar(nombre_ocr)
        mejor_score = 0.0
        mejor_nombre = nombre_ocr

        for oficial, oficial_norm in zip(self._clientes, self._clientes_norm):
            score = SequenceMatcher(None, nombre_norm, oficial_norm).ratio()
            if score > mejor_score:
                mejor_score = score
                mejor_nombre = oficial

        if mejor_score >= self.UMBRAL_SIMILITUD:
            return mejor_nombre

        return nombre_ocr

    def recargar(self):
        """Vuelve a leer el CSV (útil si el usuario lo edita en caliente)."""
        ruta = self._ruta_por_defecto()
        self._cargar(ruta)

    def total_clientes(self) -> int:
        return len(self._clientes)

    # ------------------------------------------------------------------

    def _cargar(self, ruta: Path):
        self._clientes = []
        self._clientes_norm = []

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
                self._clientes.append(nombre)
                self._clientes_norm.append(_normalizar(nombre))

    def _cargar_xlsx(self, ruta: Path):
        if not _OPENPYXL_OK:
            return
        wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
        ws = wb.active
        nombre_col = None  # índice (0-based) de la columna con el nombre
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                # Detectar columna por cabecera: "Nombre", "Cliente", "Name"…
                # Si no hay cabecera reconocida, tomar la primera columna que no sea código
                for j, cel in enumerate(row):
                    if cel and str(cel).strip().lower() in ('nombre', 'cliente', 'name'):
                        nombre_col = j
                        break
                if nombre_col is None:
                    # Sin cabecera reconocida → columna 0
                    nombre_col = 0
                    nombre = str(row[nombre_col]).strip() if row[nombre_col] else ''
                    if nombre:
                        self._clientes.append(nombre)
                        self._clientes_norm.append(_normalizar(nombre))
                continue
            if not row or row[nombre_col] is None:
                continue
            nombre = str(row[nombre_col]).strip()
            if nombre:
                self._clientes.append(nombre)
                self._clientes_norm.append(_normalizar(nombre))
        wb.close()

    @staticmethod
    def _ruta_por_defecto() -> Path:
        # Junto al .exe en producción, o en la raíz del proyecto en desarrollo.
        # Prioridad: .xlsx > .csv (el xlsx es la fuente oficial del cliente)
        bases = [
            Path(__file__).parent.parent.parent.parent,
            Path(__file__).parent.parent.parent.parent.parent,
        ]
        for base in bases:
            for ext in ("clientes.xlsx", "clientes.csv"):
                ruta = base / ext
                if ruta.exists():
                    return ruta
        return bases[0] / "clientes.csv"
