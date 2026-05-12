"""
Servicio para extraer datos específicos del texto OCR de albaranes Sufexa.
"""

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class DatosExtraidos:
    numero_cliente: Optional[str] = None  # extraído del albarán, tratado siempre como string
    fecha: Optional[str] = None           # DD/MM/YYYY
    numero: Optional[int] = None          # número de albarán
    cliente: Optional[str] = None         # rellenado desde el CSV, nunca desde OCR
    confianza: float = 0.0


class ExtractorDatosService:
    """
    Extractor adaptado al formato real de los albaranes Sufexa.

    Extrae:
      - numero_cliente : código de cliente (ej. 43001234), siempre como string
      - fecha          : DD/MM/YYYY
      - numero         : número de albarán (5 dígitos, rango 60000-99999)

    El nombre del cliente NO se extrae del albarán.
    Se obtiene del CSV usando numero_cliente como clave exacta.
    """

    RE_CABECERA_ALBARA = re.compile(r'a[il]bara', re.IGNORECASE)

    RE_FECHA = re.compile(r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{3,4})\b')

    RE_NUMERO_ALBARA = re.compile(r'(?<![/\d])(\d{5})(?![/\d])')

    # Número de cliente específico de Sufexa: 4300 + 4 dígitos
    # Permite espacio opcional entre grupos por errores OCR (ej: "4300 0034")
    RE_NUMERO_CLIENTE_SUFEXA = re.compile(r'(?<!\d)(4300\s*\d{4})(?!\d)')
    RE_NUMERO_CLIENTE_CORTO  = re.compile(r'(?<!\d)(430\d{5})(?!\d)')

    # Labels que preceden al número de cliente en el albarán
    RE_LABEL_CLIENTE = re.compile(
        r'(?:'
        r'n[ºo°]?\s*(?:de\s+)?cliente'   # Nº cliente / N cliente
        r'|c[oó]d(?:igo)?\.?\s*(?:de\s+)?cliente'  # Código cliente / Cod. cliente
        r'|cliente'                        # Cliente
        r'|customer\s*(?:number|id|code)'  # Customer number / id / code
        r'|client\s*(?:id|number)?'        # Client ID / Client number
        r')',
        re.IGNORECASE
    )

    # Número genérico tras un label (4-10 dígitos, preserva ceros iniciales)
    RE_CODIGO_TRAS_LABEL = re.compile(r'(\d{4,10})')

    def extraer_datos(self, texto_ocr: str) -> DatosExtraidos:
        datos = DatosExtraidos()
        datos.fecha = self.extraer_fecha(texto_ocr)
        datos.numero = self.extraer_numero(texto_ocr)
        datos.numero_cliente = self.extraer_numero_cliente(texto_ocr)

        campos = sum([
            datos.fecha is not None,
            datos.numero is not None,
            datos.numero_cliente is not None,
        ])
        datos.confianza = (campos / 3.0) * 100
        return datos

    # ------------------------------------------------------------------
    # Número de cliente
    # ------------------------------------------------------------------

    def extraer_numero_cliente(self, texto: str) -> Optional[str]:
        """
        Extrae el número de cliente del texto OCR.

        Estrategia:
        1. Buscar el patrón específico de Sufexa: 4300XXXX (8 dígitos)
        2. Si no aparece, buscar número tras labels conocidos
           (Nº cliente, Código cliente, Customer number, etc.)
           en la misma línea o en la línea siguiente.

        Siempre devuelve string para preservar ceros iniciales.
        """
        # Estrategia 1: patrón específico 4300XXXX — muy fiable
        m = self.RE_NUMERO_CLIENTE_SUFEXA.search(texto)
        if m:
            return re.sub(r'\s', '', m.group(1))  # quitar espacio si OCR lo insertó

        # Estrategia 1b: misma idea pero OCR leyó "430" + 5 dígitos (ej: 4300034 → 43000034)
        m = self.RE_NUMERO_CLIENTE_CORTO.search(texto)
        if m:
            return re.sub(r'\s', '', m.group(1))

        # Estrategia 2: label + número en la misma línea o la siguiente
        lineas = texto.split('\n')
        for i, linea in enumerate(lineas):
            if not self.RE_LABEL_CLIENTE.search(linea):
                continue

            # Quitar el label y buscar número en lo que queda de la línea
            resto = self.RE_LABEL_CLIENTE.sub('', linea)
            resto = re.sub(r'[:\-\s]+', ' ', resto).strip()
            m = self.RE_CODIGO_TRAS_LABEL.search(resto)
            if m:
                return self._normalizar_numero_cliente(m.group(1))

            # Buscar en la línea siguiente si la actual solo tiene el label
            if i + 1 < len(lineas):
                siguiente = lineas[i + 1].strip()
                m = self.RE_CODIGO_TRAS_LABEL.search(siguiente)
                if m:
                    return self._normalizar_numero_cliente(m.group(1))

        return None

    @staticmethod
    def _normalizar_numero_cliente(codigo: str) -> str:
        """
        Normaliza el código de cliente:
        - Elimina espacios y caracteres no alfanuméricos
        - Conserva ceros iniciales (nunca convierte a int)
        """
        codigo = re.sub(r'[^0-9A-Za-z]', '', codigo)
        return codigo.strip()

    # ------------------------------------------------------------------
    # Fecha
    # ------------------------------------------------------------------

    def extraer_fecha(self, texto: str) -> Optional[str]:
        lineas = texto.split('\n')

        fecha = self._buscar_en_contexto_albara(lineas, 'fecha')
        if fecha:
            return fecha

        for linea in lineas:
            m = self.RE_FECHA.search(linea)
            if m:
                return self._normalizar_fecha(m.group(1))

        return None

    # ------------------------------------------------------------------
    # Número de albarán
    # ------------------------------------------------------------------

    def extraer_numero(self, texto: str) -> Optional[int]:
        lineas = texto.split('\n')

        # Estrategia 1: número en la misma línea que la fecha
        for linea in lineas:
            if not self.RE_FECHA.search(linea):
                continue
            linea_sin_fecha = self.RE_FECHA.sub('', linea)
            for n in self.RE_NUMERO_ALBARA.findall(linea_sin_fecha):
                try:
                    val = int(n)
                    if self._es_numero_albaran_valido(val):
                        return val
                except ValueError:
                    pass

        # Estrategia 2: contexto estrecho alrededor de 'Albara'
        for i, linea in enumerate(lineas):
            if not self.RE_CABECERA_ALBARA.search(linea):
                continue
            for ctx in lineas[max(0, i - 1):i + 4]:
                linea_sin_fecha = self.RE_FECHA.sub('', ctx)
                for n in self.RE_NUMERO_ALBARA.findall(linea_sin_fecha):
                    try:
                        val = int(n)
                        if self._es_numero_albaran_valido(val):
                            return val
                    except ValueError:
                        pass

        return None

    @staticmethod
    def _es_numero_albaran_valido(val: int) -> bool:
        return 60000 <= val <= 99999

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------

    def validar_datos(self, datos: DatosExtraidos) -> Tuple[bool, list]:
        """
        Valida fecha y número de albarán.
        El cliente NO se valida aquí — se valida en el use_case tras el lookup CSV.
        """
        errores = []

        if not datos.fecha:
            errores.append("No se pudo extraer la fecha")
        elif not re.match(r'\d{2}/\d{2}/\d{4}', datos.fecha):
            errores.append(f"Formato de fecha inválido: {datos.fecha}")

        if not datos.numero:
            errores.append("No se pudo extraer el número de albarán")
        elif datos.numero <= 0:
            errores.append(f"Número de albarán inválido: {datos.numero}")

        return len(errores) == 0, errores

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _buscar_en_contexto_albara(self, lineas: List[str], campo: str):
        for i, linea in enumerate(lineas):
            if not self.RE_CABECERA_ALBARA.search(linea):
                continue
            start = max(0, i - 2)
            for ctx_linea in lineas[start:i + 8]:
                if campo == 'fecha':
                    m = self.RE_FECHA.search(ctx_linea)
                    if m:
                        return self._normalizar_fecha(m.group(1))
                elif campo == 'numero':
                    linea_sin_fecha = self.RE_FECHA.sub('', ctx_linea)
                    nums = self.RE_NUMERO_ALBARA.findall(linea_sin_fecha)
                    if nums:
                        try:
                            return int(nums[0])
                        except ValueError:
                            pass
        return None

    def _normalizar_fecha(self, fecha_raw: str) -> str:
        fecha = fecha_raw.replace('-', '/').replace('.', '/')
        partes = fecha.split('/')
        if len(partes) != 3:
            return fecha_raw

        dia = partes[0].zfill(2)
        mes = partes[1].zfill(2)
        anio = partes[2]

        if len(anio) == 3 and anio.startswith('20'):
            anio = anio + '6'
        elif len(anio) == 3:
            anio = '2' + anio

        try:
            d = int(dia)
            m_val = int(mes)
            if d > 31 and dia[0] == '4':
                dia = '1' + dia[1:]
            if m_val > 12 and mes[0] == '4':
                mes = '1' + mes[1:]
        except ValueError:
            pass

        return f"{dia}/{mes}/{anio}"
