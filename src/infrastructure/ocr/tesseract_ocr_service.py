"""
Servicio de OCR usando Tesseract.
"""

import pytesseract
from PIL import Image
from typing import Optional
import platform
import sys
from pathlib import Path


class TesseractOCRService:
    """
    Servicio para realizar OCR sobre imágenes usando Tesseract.

    Responsabilidades:
    - Configurar Tesseract
    - Ejecutar OCR sobre imágenes
    - Normalizar el texto extraído
    - Manejar errores de OCR
    """

    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        language: str = 'spa',
        config: str = '--psm 6'
    ):
        """
        Inicializa el servicio de OCR.

        Args:
            tesseract_cmd: Ruta al ejecutable de Tesseract (opcional)
            language: Idioma para OCR (default: 'spa' para español)
            config: Configuración de Tesseract (default: '--psm 6' para bloques de texto)

        PSM (Page Segmentation Mode):
            0 = Orientación y detección de script (OSD) only
            1 = Automatic page segmentation with OSD
            3 = Fully automatic page segmentation (default)
            4 = Single column of text
            6 = Uniform block of text (RECOMENDADO para albaranes)
            11 = Sparse text
        """
        self.language = language
        self.config = config

        # Configurar ruta de Tesseract si se proporciona
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Intentar detectar automáticamente según el SO
            self._auto_configure_tesseract()

    def _auto_configure_tesseract(self):
        """
        Configura automáticamente la ruta de Tesseract según el sistema operativo.

        Prioridad:
        1. Tesseract empaquetado (para ejecutables)
        2. Instalación del sistema
        3. PATH del sistema
        """
        # 1. DETECTAR SI ESTAMOS EN UN EJECUTABLE EMPAQUETADO
        if getattr(sys, 'frozen', False):
            # Ejecutable de PyInstaller
            if hasattr(sys, '_MEIPASS'):
                # Modo onefile (_MEIPASS es la carpeta temporal)
                base_path = Path(sys._MEIPASS)
            else:
                # Modo onedir
                base_path = Path(sys.executable).parent

            # Buscar Tesseract en carpeta relativa al ejecutable
            tesseract_empaquetado = base_path / "tesseract" / "tesseract.exe"
            if tesseract_empaquetado.exists():
                pytesseract.pytesseract.tesseract_cmd = str(tesseract_empaquetado)
                return

        # 2. INTENTAR RUTAS DEL SISTEMA (Windows)
        sistema = platform.system()
        if sistema == 'Windows':
            rutas_posibles = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]

            for ruta in rutas_posibles:
                if Path(ruta).exists():
                    pytesseract.pytesseract.tesseract_cmd = ruta
                    return

        # 3. En Linux/Mac, o si no se encontró, confiar en PATH

    def extract_text(self, image: Image.Image) -> str:
        """
        Extrae texto de una imagen usando OCR.

        Args:
            image: Imagen PIL

        Returns:
            str: Texto extraído

        Raises:
            RuntimeError: Si Tesseract no está instalado o falla
        """
        try:
            # Ejecutar OCR
            texto = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=self.config
            )

            return texto

        except pytesseract.TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract no está instalado o no se encuentra en el PATH. "
                "Instala Tesseract OCR desde: https://github.com/tesseract-ocr/tesseract"
            )
        except Exception as e:
            raise RuntimeError(f"Error al ejecutar OCR: {str(e)}")

    def extract_text_with_confidence(self, image: Image.Image) -> tuple[str, float]:
        """
        Extrae texto y calcula la confianza promedio del OCR.

        Args:
            image: Imagen PIL

        Returns:
            tuple: (texto, confianza_promedio)
                confianza_promedio: valor entre 0 y 100
        """
        try:
            # Intentar con el idioma configurado; si falla, usar 'eng' como fallback
            lang_usar = self.language
            try:
                pytesseract.image_to_string(image, lang=lang_usar, config='--psm 6')
            except pytesseract.TesseractError:
                lang_usar = 'eng'

            # Obtener datos detallados del OCR
            data = pytesseract.image_to_data(
                image,
                lang=lang_usar,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )

            # Extraer texto completo
            texto = pytesseract.image_to_string(
                image,
                lang=lang_usar,
                config=self.config
            )

            # Calcular confianza promedio (solo palabras reconocidas)
            confidencias = [
                float(conf)
                for conf in data['conf']
                if conf != '-1'  # -1 indica que no se reconoció
            ]

            confianza_promedio = (
                sum(confidencias) / len(confidencias)
                if confidencias
                else 0.0
            )

            return texto, confianza_promedio

        except Exception as e:
            raise RuntimeError(f"Error al ejecutar OCR con confianza: {str(e)}")

    @staticmethod
    def normalize_text(texto: str) -> str:
        """
        Normaliza el texto extraído por OCR.

        Aplica:
        - Eliminación de espacios múltiples
        - Normalización de saltos de línea
        - Eliminación de caracteres de control

        Args:
            texto: Texto raw del OCR

        Returns:
            str: Texto normalizado
        """
        if not texto:
            return ""

        # Eliminar caracteres de control (excepto \n y \t)
        texto_limpio = ''.join(
            char for char in texto
            if char.isprintable() or char in '\n\t'
        )

        # Normalizar espacios múltiples (pero mantener saltos de línea)
        lineas = texto_limpio.split('\n')
        lineas_normalizadas = [
            ' '.join(linea.split())
            for linea in lineas
        ]

        # Reconstruir texto
        texto_normalizado = '\n'.join(lineas_normalizadas)

        # Eliminar líneas vacías múltiples
        while '\n\n\n' in texto_normalizado:
            texto_normalizado = texto_normalizado.replace('\n\n\n', '\n\n')

        return texto_normalizado.strip()

    def is_available(self) -> bool:
        """
        Verifica si Tesseract está disponible y funcionando.

        Returns:
            bool: True si Tesseract funciona, False en caso contrario
        """
        try:
            # Intentar obtener la versión de Tesseract
            version = pytesseract.get_tesseract_version()
            return version is not None
        except:
            return False

    def get_version(self) -> str:
        """
        Obtiene la versión de Tesseract instalada.

        Returns:
            str: Versión de Tesseract
        """
        try:
            version = pytesseract.get_tesseract_version()
            return str(version)
        except:
            return "No disponible"
