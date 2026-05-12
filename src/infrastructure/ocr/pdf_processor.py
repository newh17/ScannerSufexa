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
        """Preprocesado estándar: escala de grises + contraste."""
        from PIL import ImageEnhance

        img_gray = image.convert('L')
        img_contrast = ImageEnhance.Contrast(img_gray).enhance(1.5)
        img_sharp = ImageEnhance.Sharpness(img_contrast).enhance(1.2)
        return img_sharp

    def get_image_variants(self, image: Image.Image) -> list:
        """
        Genera variantes de preprocesado ordenadas de menos a más agresivas.

        Se usan como fallback cuando el preprocesado estándar no extrae
        todos los campos del albarán (fecha, número, cliente).

        Returns:
            List[Image.Image]: Lista de imágenes preprocesadas para probar.
        """
        from PIL import ImageEnhance

        gray = image.convert('L')
        variantes = []

        # Variante 1: estándar (la que ya se usa primero en el pipeline)
        variantes.append(ImageEnhance.Sharpness(
            ImageEnhance.Contrast(gray).enhance(1.5)
        ).enhance(1.2))

        # Variante 2: binarización suave (umbral bajo — captura tinta tenue)
        variantes.append(gray.point(lambda x: 0 if x < 80 else 255, '1'))

        # Variante 3: binarización media
        variantes.append(gray.point(lambda x: 0 if x < 100 else 255, '1'))

        # Variante 4: binarización estándar
        variantes.append(gray.point(lambda x: 0 if x < 128 else 255, '1'))

        # Variante 5: contraste muy alto (rescata texto con poco contraste)
        variantes.append(ImageEnhance.Contrast(gray).enhance(3.0))

        # Variante 6: binarización alta (elimina ruido de fondo gris)
        variantes.append(gray.point(lambda x: 0 if x < 140 else 255, '1'))

        return variantes

    def get_zona_numero_cliente(self, image: Image.Image) -> list:
        """
        Recorta y amplía la zona inferior-derecha donde Sufexa imprime
        el número de cliente (4300XXXX). Devuelve variantes preprocesadas
        para OCR dedicado con PSM 7 (línea única).

        El número aparece siempre en el último 30% de altura y el 35%
        derecho del albarán. Ampliar 3x mejora la legibilidad de dígitos
        pegados al borde del recuadro.
        """
        from PIL import ImageEnhance

        w, h = image.size
        # Zona inferior-derecha donde está el número de cliente
        left   = int(w * 0.60)
        top    = int(h * 0.70)
        right  = w
        bottom = h

        crop = image.crop((left, top, right, bottom))

        # Escalar 3x para que el OCR vea los dígitos con más detalle
        nuevo_w = (right - left) * 3
        nuevo_h = (bottom - top) * 3
        crop_grande = crop.resize((nuevo_w, nuevo_h), Image.LANCZOS)

        gray = crop_grande.convert('L')
        variantes = []

        # V1: contraste alto
        variantes.append(ImageEnhance.Contrast(gray).enhance(2.5))

        # V2: binarización suave (captura tinta tenue cerca del borde)
        variantes.append(gray.point(lambda x: 0 if x < 90 else 255, '1'))

        # V3: binarización media
        variantes.append(gray.point(lambda x: 0 if x < 115 else 255, '1'))

        # V4: binarización estándar
        variantes.append(gray.point(lambda x: 0 if x < 135 else 255, '1'))

        return variantes

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
