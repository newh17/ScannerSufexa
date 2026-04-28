"""
Servicio para extraer datos específicos del texto OCR de albaranes.
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class DatosExtraidos:
    """
    DTO que contiene los datos extraídos de un albarán.
    """
    cliente: Optional[str] = None
    fecha: Optional[str] = None  # Formato: DD/MM/YYYY
    numero: Optional[int] = None
    confianza: float = 0.0  # Confianza de la extracción (0-100)


class ExtractorDatosService:
    """
    Servicio especializado en extraer datos del formato específico de albarán de Sufexa.

    Formato esperado:
    - Cliente: Nombre en la parte superior (ej: "METALCRISMAR, S.L.")
    - Fecha: Campo "Data" seguido de la fecha (ej: "Data 23/01/2026")
    - Número: Campo "Albarà núm." seguido del número (ej: "Albarà núm. 71206")

    Usa regex y heurísticas específicas para este formato.
    """

    # Patrones regex para extracción
    PATTERN_FECHA = r'Data[:\s]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})'
    PATTERN_NUMERO = r'Albar[àa]\s+n[úu]m[\.\:]?\s*[:\s]*(\d+)'

    # Patrones alternativos por si hay errores de OCR
    PATTERN_FECHA_ALT = r'Data[:\s]*(\d{1,2})\s*[/\-\.]\s*(\d{1,2})\s*[/\-\.]\s*(\d{4})'
    PATTERN_NUMERO_ALT = r'(?:Albara|Albaran)\s+(?:num|núm|num\.|núm\.)\s*[:\-]?\s*(\d+)'

    def __init__(self):
        """Inicializa el extractor de datos."""
        pass

    def extraer_datos(self, texto_ocr: str) -> DatosExtraidos:
        """
        Extrae todos los datos del texto OCR.

        Args:
            texto_ocr: Texto obtenido del OCR

        Returns:
            DatosExtraidos: Objeto con los datos extraídos
        """
        datos = DatosExtraidos()

        # Extraer cada campo
        datos.fecha = self.extraer_fecha(texto_ocr)
        datos.numero = self.extraer_numero(texto_ocr)
        datos.cliente = self.extraer_cliente(texto_ocr)

        # Calcular confianza (cuántos campos se extrajeron)
        campos_extraidos = sum([
            datos.fecha is not None,
            datos.numero is not None,
            datos.cliente is not None,
        ])
        datos.confianza = (campos_extraidos / 3.0) * 100

        return datos

    def extraer_fecha(self, texto: str) -> Optional[str]:
        """
        Extrae la fecha del albarán.

        Busca el patrón "Data DD/MM/YYYY" o variantes.

        Args:
            texto: Texto del OCR

        Returns:
            Optional[str]: Fecha en formato DD/MM/YYYY o None
        """
        # Buscar con el patrón principal
        match = re.search(self.PATTERN_FECHA, texto, re.IGNORECASE)

        if match:
            fecha_raw = match.group(1)
            return self._normalizar_fecha(fecha_raw)

        # Intentar con patrón alternativo (más permisivo)
        match = re.search(self.PATTERN_FECHA_ALT, texto, re.IGNORECASE)

        if match:
            dia = match.group(1).zfill(2)
            mes = match.group(2).zfill(2)
            anio = match.group(3)
            return f"{dia}/{mes}/{anio}"

        return None

    def extraer_numero(self, texto: str) -> Optional[int]:
        """
        Extrae el número del albarán.

        Busca el patrón "Albarà núm. XXXXX" o variantes.

        Args:
            texto: Texto del OCR

        Returns:
            Optional[int]: Número del albarán o None
        """
        # Buscar con el patrón principal
        match = re.search(self.PATTERN_NUMERO, texto, re.IGNORECASE)

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

        # Intentar con patrón alternativo
        match = re.search(self.PATTERN_NUMERO_ALT, texto, re.IGNORECASE)

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

        return None

    def extraer_cliente(self, texto: str) -> Optional[str]:
        """
        Extrae el nombre del cliente.

        Estrategia:
        1. Buscar líneas al inicio del documento
        2. Filtrar líneas que parezcan nombres de empresa
        3. Seleccionar la más probable

        Heurísticas:
        - Suele estar en las primeras líneas
        - Contiene palabras como S.L., S.A., S.L.U., etc.
        - Está en mayúsculas
        - No contiene palabras clave como "Data", "Albarà", etc.

        Args:
            texto: Texto del OCR

        Returns:
            Optional[str]: Nombre del cliente o None
        """
        lineas = texto.split('\n')

        # Palabras clave que NO deben aparecer en el nombre del cliente
        palabras_excluir = [
            'data', 'albara', 'albarà', 'núm', 'num', 'factura',
            'total', 'iva', 'subtotal', 'cantidad', 'descripción',
            'precio', 'importe'
        ]

        # Patrones de sufijos de empresas
        sufijos_empresa = [
            r'S\.L\.', r'S\.A\.', r'S\.L\.U\.', r'S\.COOP\.',
            r'S\.L\b', r'S\.A\b', r'SL\b', r'SA\b'
        ]

        candidatos = []

        # Analizar las primeras 10 líneas
        for i, linea in enumerate(lineas[:10]):
            linea_limpia = linea.strip()

            # Ignorar líneas vacías o muy cortas
            if not linea_limpia or len(linea_limpia) < 3:
                continue

            # Ignorar líneas que contengan palabras clave a excluir
            if any(palabra in linea_limpia.lower() for palabra in palabras_excluir):
                continue

            # Dar prioridad a líneas que contengan sufijos de empresa
            tiene_sufijo = any(
                re.search(sufijo, linea_limpia, re.IGNORECASE)
                for sufijo in sufijos_empresa
            )

            # Dar prioridad a líneas en mayúsculas
            es_mayusculas = linea_limpia.isupper()

            # Calcular score
            score = 0
            if tiene_sufijo:
                score += 10
            if es_mayusculas:
                score += 5
            # Priorizar líneas al inicio (primeras 3 líneas)
            if i < 3:
                score += (3 - i) * 2

            if score > 0:
                candidatos.append((linea_limpia, score))

        # Ordenar candidatos por score y retornar el mejor
        if candidatos:
            candidatos.sort(key=lambda x: x[1], reverse=True)
            return candidatos[0][0]

        return None

    def _normalizar_fecha(self, fecha_raw: str) -> str:
        """
        Normaliza una fecha al formato DD/MM/YYYY.

        Args:
            fecha_raw: Fecha raw (puede tener - o . como separadores)

        Returns:
            str: Fecha normalizada DD/MM/YYYY
        """
        # Reemplazar separadores por /
        fecha = fecha_raw.replace('-', '/').replace('.', '/')

        # Separar partes
        partes = fecha.split('/')

        if len(partes) != 3:
            return fecha_raw

        # Asegurar formato DD/MM/YYYY (con ceros a la izquierda)
        dia = partes[0].zfill(2)
        mes = partes[1].zfill(2)
        anio = partes[2]

        return f"{dia}/{mes}/{anio}"

    def validar_datos(self, datos: DatosExtraidos) -> Tuple[bool, list]:
        """
        Valida que los datos extraídos sean correctos.

        Args:
            datos: Datos extraídos

        Returns:
            Tuple[bool, list]: (es_valido, lista_de_errores)
        """
        errores = []

        if not datos.cliente:
            errores.append("No se pudo extraer el nombre del cliente")

        if not datos.fecha:
            errores.append("No se pudo extraer la fecha")
        else:
            # Validar formato de fecha
            if not re.match(r'\d{2}/\d{2}/\d{4}', datos.fecha):
                errores.append(f"Formato de fecha inválido: {datos.fecha}")

        if not datos.numero:
            errores.append("No se pudo extraer el número de albarán")
        elif datos.numero <= 0:
            errores.append(f"Número de albarán inválido: {datos.numero}")

        es_valido = len(errores) == 0

        return es_valido, errores
