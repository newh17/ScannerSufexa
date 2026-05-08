"""
Servicio para extraer datos específicos del texto OCR de albaranes Sufexa.
"""

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class DatosExtraidos:
    cliente: Optional[str] = None
    fecha: Optional[str] = None   # DD/MM/YYYY
    numero: Optional[int] = None
    confianza: float = 0.0


class ExtractorDatosService:
    """
    Extractor adaptado al formato real de los albaranes Sufexa.

    Formato observado en los PDFs escaneados:
        Cabecera:  "Data  Albara nim."  (o variantes OCR: Aibara, nam., num.)
        Valores:   "DD/MM/YYYY  NNNNN"  en la línea siguiente,
                   o número/fecha en líneas separadas.

    Estrategia:
        1. Localizar el bloque "Albara" (label de número de albarán).
        2. Buscar fecha y número de 5 dígitos en las líneas cercanas.
        3. Fallback global: primera fecha DD/MM/YYYY del documento.
        4. Cliente: primera línea con sufijo de empresa (S.L., S.A., S.C. …).
    """

    # Reconoce la cabecera aunque el OCR confunda letras (Aibara, Albara, etc.)
    RE_CABECERA_ALBARA = re.compile(
        r'a[il]bara', re.IGNORECASE
    )

    # Acepta años de 3 o 4 dígitos (el 4.º lo completamos si falta)
    RE_FECHA = re.compile(
        r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{3,4})\b'
    )

    # Número de albarán: exactamente 5 dígitos que NO sean parte de un número más largo
    RE_NUMERO_ALBARA = re.compile(
        r'(?<![/\d])(\d{5})(?![/\d])'
    )

    SUFIJOS_EMPRESA = re.compile(
        # \b al inicio ancla al inicio de palabra.
        # (?!\w) en lugar de \b al final: evita fallar cuando el sufijo
        # acaba en "." (punto = carácter no-word, \b no encuentra frontera).
        r'\bS\.L\.U?\.?(?!\w)'                   # S.L. / S.L.U.
        r'|\bS\.A\.?(?!\w)'                    # S.A.
        r'|\bS\.C\.?(?!\w)'                    # S.C. (Sociedad Civil)
        r'|\bC\.B\.?(?!\w)'                    # C.B. (Comunidad de Bienes)
        r'|\bS\.COOP\.(?:VAL\.?|V\.?)(?!\w)'  # S.COOP.VAL. / S.COOP.V.
        r'|\bS\.COOP\.?(?!\w)'                 # S.COOP. sola
        r'|\bCOOP\.\s*V\.?(?!\w)'             # COOP. V. / COOP.V.
        r'|\bCOOP\.(?:VAL\.)?LTDA\.?(?!\w)'  # COOP.VAL.LTDA. / COOP.LTDA.
        r'|\bLTDA\.?(?!\w)'                    # LTDA. sola
        r'|\bCOOP\.?(?!\w)'                    # COOP. sola
        r'|\bS\.C\.P\.?(?!\w)'                 # S.C.P. (Sociedad Civil Profesional)
        r'|\bS\.L\.L\.?(?!\w)',                # S.L.L. (Soc. Limitada Laboral)
        re.IGNORECASE
    )

    # Indicadores de que una línea es una dirección, no un cliente
    RE_ES_DIRECCION = re.compile(
        r'\bS[/\\]N\.?\b'            # S/N = sin número (dirección sin nº)
        r'|\b(?:CALLE|CARRER|AVDA?\.?|AVENIDA|PLAZA|PLA[CÇ]A'
        r'|PASEO|PASSEIG|POLIGONO?|POLIGON|CAMINO|CAMI|'
        r'VIA|RONDA|TRAVESIA|PARTIDA)\b',
        re.IGNORECASE
    )

    def extraer_datos(self, texto_ocr: str) -> DatosExtraidos:
        datos = DatosExtraidos()
        datos.fecha = self.extraer_fecha(texto_ocr)
        datos.numero = self.extraer_numero(texto_ocr)
        datos.cliente = self.extraer_cliente(texto_ocr)

        campos = sum([
            datos.fecha is not None,
            datos.numero is not None,
            datos.cliente is not None,
        ])
        datos.confianza = (campos / 3.0) * 100
        return datos

    # ------------------------------------------------------------------
    # Fecha
    # ------------------------------------------------------------------

    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Busca la fecha cerca de la cabecera 'Albara' y como fallback
        toma la primera fecha DD/MM/YYYY del documento.
        """
        lineas = texto.split('\n')

        # Paso 1: buscar fecha en el contexto de la cabecera de albarán
        fecha = self._buscar_en_contexto_albara(lineas, 'fecha')
        if fecha:
            return fecha

        # Paso 2: fallback — primera fecha válida del documento
        for linea in lineas:
            m = self.RE_FECHA.search(linea)
            if m:
                return self._normalizar_fecha(m.group(1))

        return None

    # ------------------------------------------------------------------
    # Número
    # ------------------------------------------------------------------

    def extraer_numero(self, texto: str) -> Optional[int]:
        """
        Estrategia de extracción del número de albarán:

        1. MISMA LÍNEA que la fecha: patrón más fiable.
           Los albaranes Sufexa muestran 'DD/MM/YYYY 7XXXX' en la misma línea.
        2. CONTEXTO ESTRECHO (±3 líneas) alrededor de la cabecera 'Albara'.
           Para el caso en que número y fecha están en líneas separadas.

        Los códigos postales (46xxx, 46xxx) se descartan porque no coinciden
        con el rango numérico de los albaranes (7xxxx).
        """
        lineas = texto.split('\n')

        # Estrategia 1: número en la misma línea que la fecha
        for linea in lineas:
            if not self.RE_FECHA.search(linea):
                continue
            linea_sin_fecha = self.RE_FECHA.sub('', linea)
            nums = self.RE_NUMERO_ALBARA.findall(linea_sin_fecha)
            for n in nums:
                try:
                    val = int(n)
                    if self._es_numero_albaran_valido(val):
                        return val
                except ValueError:
                    pass

        # Estrategia 2: contexto estrecho alrededor de 'Albara' (solo 3 líneas)
        for i, linea in enumerate(lineas):
            if not self.RE_CABECERA_ALBARA.search(linea):
                continue
            start = max(0, i - 1)
            for ctx in lineas[start:i + 4]:
                linea_sin_fecha = self.RE_FECHA.sub('', ctx)
                nums = self.RE_NUMERO_ALBARA.findall(linea_sin_fecha)
                for n in nums:
                    try:
                        val = int(n)
                        if self._es_numero_albaran_valido(val):
                            return val
                    except ValueError:
                        pass

        return None

    @staticmethod
    def _es_numero_albaran_valido(val: int) -> bool:
        """
        Descarta números que claramente no son albaranes:
        - Códigos postales españoles: 01000-52999
        - Números de teléfono: >9 dígitos
        - Números muy pequeños o muy grandes
        Los albaranes de Sufexa están en el rango 60000-99999.
        """
        return 60000 <= val <= 99999

    # ------------------------------------------------------------------
    # Cliente
    # ------------------------------------------------------------------

    def extraer_cliente(self, texto: str) -> Optional[str]:
        """
        Busca el nombre del cliente en todo el texto.

        Prioridad:
        1. Línea con sufijo de empresa (S.L., S.A., S.C. …)
        2. Línea en MAYÚSCULAS corta, no relacionada con cabeceras
        """
        lineas = texto.split('\n')

        # Palabras clave que descartan la línea — comparación por palabra completa
        RE_EXCLUIR = re.compile(
            r'\b(?:data|albara|albar|aibara|n[iu]m|n[ao]m|referencia|referéncia'
            r'|article|quantitat|preu|import|subtotal|total|iva|factura'
            r'|suministres|suministwes|poligon|avda|calle|carrer'
            r'|tel(?:éfon|efon|\.)?|fax|correu|coreu|electronic|email'
            r'|novetle|xativa|valencia|industrial)\b',
            re.IGNORECASE
        )

        candidatos: List[Tuple[str, int]] = []

        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue

            # Si la línea tiene sufijo de empresa pero es larga por basura OCR al inicio,
            # limpiarla antes del filtro de longitud para no descartarla
            if self.SUFIJOS_EMPRESA.search(linea) and len(linea) > 80:
                linea = self._limpiar_nombre_cliente(linea)

            if len(linea) < 4 or len(linea) > 80:
                continue

            # RE_EXCLUIR no se aplica si la línea tiene sufijo de empresa:
            # evita descartar nombres como "VALENCIA MUEBLES A MEDIDA, S.L."
            if RE_EXCLUIR.search(linea) and not self.SUFIJOS_EMPRESA.search(linea):
                continue

            # Ignorar líneas de solo números/símbolos/separadores
            if re.match(r'^[\d\s\.\,\-\/\|\+\=\*\_\#\@\!\?\:\;]+$', linea):
                continue

            # Ignorar líneas que son claramente direcciones
            if self.RE_ES_DIRECCION.search(linea):
                continue

            # Ignorar líneas que terminan en número de portal sin sufijo empresa
            if re.search(r'\b\d{1,5}\s*[,\.]?\s*$', linea) and not self.SUFIJOS_EMPRESA.search(linea):
                continue

            score = 0

            tiene_sufijo = bool(self.SUFIJOS_EMPRESA.search(linea))
            if tiene_sufijo:
                score += 20

            # Palabras reales de la línea (mínimo 2 letras)
            palabras = [w for w in re.split(r'[\s,\.]+', linea)
                        if re.search(r'[A-Za-záéíóúÁÉÍÓÚñÑ]{2,}', w)]

            # Sin sufijo: descartar líneas de 1 sola palabra (son pueblos, cabeceras, etc.)
            if not tiene_sufijo and len(palabras) < 2:
                continue

            solo_letras = re.sub(r'[^A-Za-záéíóúàèìòùÁÉÍÓÚÀÈÌÒÙñÑ]', '', linea)
            if solo_letras:
                if solo_letras.isupper() and len(linea) <= 60:
                    score += 5  # Todo en mayúsculas: empresa o nombre propio en caps
                elif all(w[0].isupper() for w in palabras if w):
                    score += 3  # Title Case: nombre propio en mayúscula inicial

            if score > 0:
                candidatos.append((linea, score))

        if candidatos:
            candidatos.sort(key=lambda x: x[1], reverse=True)
            return self._limpiar_nombre_cliente(candidatos[0][0])

        return None

    def _limpiar_nombre_cliente(self, nombre: str) -> str:
        """
        Limpia el nombre de cliente eliminando basura OCR al inicio y al final.
        """
        # Si hay '|', tomar la parte izquierda (la derecha suele quedar vacía)
        if '|' in nombre:
            partes = [p.strip() for p in nombre.split('|') if p.strip()]
            nombre = partes[0] if partes else nombre

        sufijo_m = self.SUFIJOS_EMPRESA.search(nombre)
        if sufijo_m:
            # Con sufijo: extraer nombre real + sufijo exacto, descartar basura OCR al inicio/final.
            pre_sufijo = nombre[:sufijo_m.start()]
            sufijo_str = nombre[sufijo_m.start():sufijo_m.end()]  # solo el sufijo (sin trailing)
            # Última secuencia que empiece y acabe en mayúscula, permite dígitos entre medias
            # (ej: "BC3 COCINAS" o "FUSTERIA ESTIL NOU MIRAVET")
            m = re.search(
                r'([A-ZÁÉÍÓÚÀÈÑ][A-ZÁÉÍÓÚÀÈÑ\d\s\.]*[A-ZÁÉÍÓÚÀÈÑ])\s*[,\s]*$',
                pre_sufijo
            )
            if m:
                parte = m.group(1).rstrip(', ')
                # Quitar letra suelta al inicio (basura OCR tipo "S FUSTERIA…")
                parte = re.sub(r'^[A-ZÁÉÍÓÚÀÈÑ] (?=[A-ZÁÉÍÓÚÀÈÑ]{2})', '', parte)
                nombre = parte + ', ' + sufijo_str
            else:
                # Fallback: primer par de mayúsculas consecutivas
                m2 = re.search(r'[A-ZÁÉÍÓÚÀÈÑ]{2}', pre_sufijo)
                if m2:
                    nombre = nombre[m2.start():sufijo_m.end()]
        else:
            # Sin sufijo: eliminar basura al inicio hasta primera letra mayúscula de palabra real
            m = re.search(r'[A-ZÁÉÍÓÚÀÈÑ][A-ZÁÉÍÓÚÀÈÑa-záéíóúàèñ]', nombre)
            if m and m.start() > 0:
                nombre = nombre[m.start():]

        # Eliminar CIF/NIF al final (8+ dígitos solos) y trailing garbage (—, -)
        nombre = re.sub(r'\s+\d{8,}$', '', nombre)
        nombre = re.sub(r'[\s\-—]+$', '', nombre)

        # Normalizar a mayúsculas (el OCR a veces produce Title Case en lugar de CAPS)
        return nombre.strip().upper()

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _buscar_en_contexto_albara(self, lineas: List[str], campo: str):
        """
        Localiza la línea cabecera que contiene 'Albara' y examina
        las 3 líneas siguientes buscando fecha o número de albarán.
        """
        for i, linea in enumerate(lineas):
            if not self.RE_CABECERA_ALBARA.search(linea):
                continue

            # Contexto: 2 líneas anteriores + esta línea + las 7 siguientes
            start = max(0, i - 2)
            contexto_lineas = lineas[start:i + 8]

            for ctx_linea in contexto_lineas:
                if campo == 'fecha':
                    m = self.RE_FECHA.search(ctx_linea)
                    if m:
                        return self._normalizar_fecha(m.group(1))

                elif campo == 'numero':
                    # Quitar primero las fechas para no confundir dígitos
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

        # Año truncado (3 dígitos) → completar asumiendo 202x
        if len(anio) == 3 and anio.startswith('20'):
            anio = anio + '6'  # 202 → 2026 (ajustar si cambia el año)
        elif len(anio) == 3:
            anio = '2' + anio  # fallback

        # Corrección OCR habitual: 4→1 en día/mes
        try:
            d = int(dia)
            m = int(mes)
            if d > 31 and dia[0] == '4':
                dia = '1' + dia[1:]
            if m > 12 and mes[0] == '4':
                mes = '1' + mes[1:]
        except ValueError:
            pass

        return f"{dia}/{mes}/{anio}"

    def validar_datos(self, datos: DatosExtraidos) -> Tuple[bool, list]:
        errores = []

        if not datos.cliente:
            errores.append("No se pudo extraer el nombre del cliente")

        if not datos.fecha:
            errores.append("No se pudo extraer la fecha")
        else:
            if not re.match(r'\d{2}/\d{2}/\d{4}', datos.fecha):
                errores.append(f"Formato de fecha inválido: {datos.fecha}")

        if not datos.numero:
            errores.append("No se pudo extraer el número de albarán")
        elif datos.numero <= 0:
            errores.append(f"Número de albarán inválido: {datos.numero}")

        return len(errores) == 0, errores
