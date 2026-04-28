"""
Procesador de archivos PDF a imágenes.
"""

from pathlib import Path
from typing import List, Optional
from PIL import Image
import fitz  # PyMuPDF


class PDFProcessor:
    """
    Servicio para convertir archivos PDF a imágenes.

    Usa PyMuPDF (fitz) para extraer páginas como imágenes.
    Optimizado para PDFs escaneados de albaranes.
    """

    def __init__(self, dpi: int = 300):
        """
        Inicializa el procesador de PDF.

        Args:
            dpi: Resolución para la conversión (default: 300 DPI para buena calidad OCR)
        """
        self.dpi = dpi
        # Zoom factor para conseguir el DPI deseado
        # PyMuPDF usa 72 DPI por defecto, así que zoom = dpi / 72
        self.zoom = dpi / 72.0

    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convierte todas las páginas de un PDF a imágenes.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            List[Image.Image]: Lista de imágenes PIL (una por página)

        Raises:
            FileNotFoundError: Si el PDF no existe
            ValueError: Si el PDF está corrupto o no se puede abrir
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"No se encuentra el archivo: {pdf_path}")

        if not pdf_file.is_file():
            raise ValueError(f"La ruta no es un archivo: {pdf_path}")

        try:
            # Abrir el PDF
            doc = fitz.open(pdf_path)

            if doc.page_count == 0:
                raise ValueError("El PDF no contiene páginas")

            imagenes = []

            # Convertir cada página
            for page_num in range(doc.page_count):
                page = doc[page_num]

                # Crear matriz de transformación para el zoom
                mat = fitz.Matrix(self.zoom, self.zoom)

                # Renderizar página como imagen
                pix = page.get_pixmap(matrix=mat)

                # Convertir a PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                imagenes.append(img)

            doc.close()

            return imagenes

        except Exception as e:
            raise ValueError(f"Error al procesar el PDF: {str(e)}")

    def pdf_first_page_to_image(self, pdf_path: str) -> Image.Image:
        """
        Convierte solo la primera página del PDF a imagen.

        Optimizado para albaranes de una sola página.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Image.Image: Imagen PIL de la primera página

        Raises:
            FileNotFoundError: Si el PDF no existe
            ValueError: Si el PDF está corrupto o no se puede abrir
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"No se encuentra el archivo: {pdf_path}")

        try:
            # Abrir el PDF
            doc = fitz.open(pdf_path)

            if doc.page_count == 0:
                raise ValueError("El PDF no contiene páginas")

            # Obtener solo la primera página
            page = doc[0]

            # Crear matriz de transformación
            mat = fitz.Matrix(self.zoom, self.zoom)

            # Renderizar como imagen
            pix = page.get_pixmap(matrix=mat)

            # Convertir a PIL Image
            import io
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            doc.close()

            return img

        except Exception as e:
            raise ValueError(f"Error al procesar el PDF: {str(e)}")

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocesa la imagen para mejorar el OCR.

        Aplica:
        - Conversión a escala de grises
        - Aumento de contraste
        - Reducción de ruido (opcional)

        Args:
            image: Imagen PIL original

        Returns:
            Image.Image: Imagen procesada
        """
        from PIL import ImageEnhance

        # Convertir a escala de grises
        img_gray = image.convert('L')

        # Aumentar contraste (mejora reconocimiento de texto)
        enhancer = ImageEnhance.Contrast(img_gray)
        img_contrast = enhancer.enhance(1.5)  # Factor 1.5 = +50% contraste

        # Aumentar nitidez
        enhancer = ImageEnhance.Sharpness(img_contrast)
        img_sharp = enhancer.enhance(1.2)

        return img_sharp

    def save_image(self, image: Image.Image, output_path: str):
        """
        Guarda una imagen en disco.

        Args:
            image: Imagen PIL
            output_path: Ruta donde guardar la imagen
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        image.save(output_path, format='PNG', optimize=True)
