"""
Servicio de lookup de clientes por número de cliente.

Lee clientes.xlsx (o clientes.csv) junto al .exe.
El CSV/Excel debe tener dos columnas: numero_cliente, nombre_cliente.
El nombre SIEMPRE proviene del archivo — nunca del OCR.
"""

import re
import sys
from pathlib import Path
from typing import Optional

try:
    import openpyxl
    _OPENPYXL_OK = True
except ImportError:
    _OPENPYXL_OK = False


def _normalizar_numero(numero: str) -> str:
    """Elimina espacios y caracteres no alfanuméricos para comparar."""
    return re.sub(r'[^0-9A-Za-z]', '', numero).strip()


class ClienteLookupService:
    """
    Dado un número de cliente extraído del OCR, devuelve el nombre EXACTO del Excel/CSV.

    El CSV/Excel debe tener dos columnas:
      - numero_cliente  (ej. 43001234)
      - nombre_cliente  (ej. METALCRISMAR, S.L.)

    La búsqueda es exacta tras normalización (elimina espacios y caracteres no alfanuméricos).
    Si el número no está en el archivo → devuelve None.
    """

    def __init__(self, ruta_csv: Optional[str] = None):
        self._tabla: dict[str, str] = {}   # numero_normalizado → nombre_oficial
        self._cargado: bool = False
        self._error_carga: Optional[str] = None

        ruta = Path(ruta_csv) if ruta_csv else self._ruta_por_defecto()
        self._cargar(ruta)

    # ------------------------------------------------------------------

    def buscar_por_numero(self, numero_cliente: str) -> Optional[str]:
        """
        Devuelve el nombre oficial del cliente, o None si no se encontró.

        Args:
            numero_cliente: Número extraído del OCR (string)

        Returns:
            Nombre exacto del archivo, o None si no hay coincidencia
        """
        if not numero_cliente or not self._tabla:
            return None

        clave = _normalizar_numero(numero_cliente)
        return self._tabla.get(clave)

    def is_loaded(self) -> bool:
        """Indica si el archivo se cargó con al menos un cliente."""
        return self._cargado and len(self._tabla) > 0

    def total_clientes(self) -> int:
        return len(self._tabla)

    def error_carga(self) -> Optional[str]:
        """Mensaje de error si la carga falló, o None si fue bien."""
        return self._error_carga

    def recargar(self):
        ruta = self._ruta_por_defecto()
        self._cargar(ruta)

    # ------------------------------------------------------------------

    def _cargar(self, ruta: Path):
        self._tabla = {}
        self._cargado = False
        self._error_carga = None

        if not ruta.exists():
            self._error_carga = f"Archivo de clientes no encontrado: {ruta}"
            print(f"[ClienteLookup] AVISO: {self._error_carga}", file=sys.stderr)
            return

        try:
            if ruta.suffix.lower() == '.xlsx':
                self._cargar_xlsx(ruta)
                if not self._tabla and _OPENPYXL_OK:
                    ruta_csv = ruta.with_suffix('.csv')
                    if ruta_csv.exists():
                        self._cargar_csv(ruta_csv)
                elif not self._tabla and not _OPENPYXL_OK:
                    ruta_csv = ruta.with_suffix('.csv')
                    if ruta_csv.exists():
                        self._cargar_csv(ruta_csv)
            else:
                self._cargar_csv(ruta)

            if self._tabla:
                self._cargado = True
                print(
                    f"[ClienteLookup] {len(self._tabla)} clientes cargados desde {ruta.name}",
                    file=sys.stderr
                )
            else:
                self._error_carga = f"El archivo {ruta.name} no contiene datos válidos"

        except Exception as e:
            self._error_carga = f"Error al leer {ruta.name}: {e}"
            print(f"[ClienteLookup] ERROR: {self._error_carga}", file=sys.stderr)

    def _cargar_csv(self, ruta: Path):
        """
        Lee un CSV con dos columnas: numero_cliente, nombre_cliente.
        La primera línea puede ser cabecera (se detecta automáticamente).
        Separador: coma o punto y coma.
        """
        with open(ruta, encoding='utf-8-sig') as f:
            for i, linea in enumerate(f):
                linea = linea.strip()
                if not linea:
                    continue

                # Detectar separador
                if ';' in linea:
                    partes = linea.split(';', 1)
                else:
                    partes = linea.split(',', 1)

                if len(partes) < 2:
                    continue

                numero_raw = partes[0].strip()
                nombre_raw = partes[1].strip()

                # Saltar cabecera
                if i == 0 and numero_raw.lower() in ('numero_cliente', 'num_cliente', 'numero', 'client', 'id'):
                    continue

                numero_norm = _normalizar_numero(numero_raw)
                if numero_norm and nombre_raw:
                    self._tabla[numero_norm] = nombre_raw

    def _cargar_xlsx(self, ruta: Path):
        if not _OPENPYXL_OK:
            return

        wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
        ws = wb.active

        col_numero = 0
        col_nombre = 1

        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if not row:
                continue

            if i == 0:
                # Detectar columnas por cabecera
                for j, cel in enumerate(row):
                    if cel is None:
                        continue
                    cel_str = str(cel).strip().lower()
                    if cel_str in ('numero_cliente', 'num_cliente', 'numero', 'client', 'id'):
                        col_numero = j
                    elif cel_str in ('nombre_cliente', 'nombre', 'name', 'cliente'):
                        col_nombre = j
                # Si la primera fila parece cabecera, saltar
                primer_cel = str(row[0]).strip().lower() if row[0] else ''
                if primer_cel in ('numero_cliente', 'num_cliente', 'numero', 'client', 'id'):
                    continue
                # Si no hay cabecera, procesar la primera fila como dato

            try:
                numero_raw = str(row[col_numero]).strip() if row[col_numero] is not None else ''
                nombre_raw = str(row[col_nombre]).strip() if col_nombre < len(row) and row[col_nombre] is not None else ''
            except (IndexError, TypeError):
                continue

            numero_norm = _normalizar_numero(numero_raw)
            if numero_norm and nombre_raw:
                self._tabla[numero_norm] = nombre_raw

        wb.close()

    @staticmethod
    def _ruta_por_defecto() -> Path:
        candidatos: list[Path] = []

        if getattr(sys, 'frozen', False):
            candidatos.append(Path(sys.executable).parent)

        candidatos += [
            Path(__file__).parent.parent.parent.parent,
            Path(__file__).parent.parent.parent.parent.parent,
        ]

        for base in candidatos:
            for nombre in ("clientes.xlsx", "clientes.csv"):
                ruta = base / nombre
                if ruta.exists():
                    return ruta

        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent / "clientes.xlsx"
        return candidatos[-1] / "clientes.xlsx"
