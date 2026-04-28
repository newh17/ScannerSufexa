"""
Caso de uso: Procesar Albarán Completo.

Orquesta todo el pipeline de procesamiento.
"""

import time
from pathlib import Path
from typing import Optional

from domain.entities import Albaran, Cliente
from domain.value_objects import FechaAlbaran, NumeroAlbaran
from domain.repositories import IAlbaranRepository, IClienteRepository
from domain.exceptions import (
    AlbaranDuplicadoException,
    DatosInvalidosException,
    ClienteInvalidoException
)
from application.services import ExtractorDatosService
from infrastructure.filesystem import FileSystemService
from infrastructure.logging import LoggerService

# Imports opcionales de OCR (pueden no estar disponibles)
try:
    from infrastructure.ocr import TesseractOCRService, PDFProcessor
except ImportError:
    # Permitir que el módulo se importe sin OCR
    TesseractOCRService = None
    PDFProcessor = None


class ResultadoProcesamiento:
    """
    DTO que representa el resultado del procesamiento.
    """

    def __init__(
        self,
        exito: bool,
        archivo: str,
        razon: Optional[str] = None,
        albaran: Optional[Albaran] = None,
        tiempo_ms: Optional[float] = None
    ):
        self.exito = exito
        self.archivo = archivo
        self.razon = razon
        self.albaran = albaran
        self.tiempo_ms = tiempo_ms


class ProcesarAlbaranUseCase:
    """
    Caso de uso principal: Procesar un albarán de principio a fin.

    Pipeline:
    1. PDF → Imagen (PDFProcessor)
    2. Imagen → Texto (TesseractOCRService)
    3. Texto → Datos (ExtractorDatosService)
    4. Datos → Entidades (Domain)
    5. Validación de duplicados
    6. Persistencia (Repositories)
    7. Movimiento de archivo (FileSystemService)

    Maneja todos los errores posibles en cada paso.
    """

    def __init__(
        self,
        pdf_processor: PDFProcessor,
        ocr_service: TesseractOCRService,
        extractor: ExtractorDatosService,
        albaran_repo: IAlbaranRepository,
        cliente_repo: IClienteRepository,
        file_system: FileSystemService,
        logger: LoggerService
    ):
        """
        Inicializa el caso de uso.

        Args:
            pdf_processor: Procesador de PDF a imagen
            ocr_service: Servicio de OCR
            extractor: Extractor de datos
            albaran_repo: Repositorio de albaranes
            cliente_repo: Repositorio de clientes
            file_system: Servicio de sistema de archivos
            logger: Servicio de logging
        """
        self.pdf_processor = pdf_processor
        self.ocr_service = ocr_service
        self.extractor = extractor
        self.albaran_repo = albaran_repo
        self.cliente_repo = cliente_repo
        self.file_system = file_system
        self.logger = logger

    def ejecutar(self, pdf_path: str) -> ResultadoProcesamiento:
        """
        Ejecuta el procesamiento completo de un albarán.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            ResultadoProcesamiento: Resultado del procesamiento
        """
        inicio = time.time()
        nombre_archivo = Path(pdf_path).name

        self.logger.log_procesamiento_inicio(pdf_path)

        try:
            # PASO 1: PDF → Imagen
            try:
                imagen = self.pdf_processor.pdf_first_page_to_image(pdf_path)
                imagen_procesada = self.pdf_processor.preprocess_image(imagen)
                self.logger.debug(f"   [1/7] ✅ PDF → Imagen")
            except Exception as e:
                return self._manejar_error(
                    pdf_path,
                    "Error_PDF",
                    f"No se pudo procesar el PDF: {e}",
                    inicio
                )

            # PASO 2: Imagen → Texto (OCR)
            try:
                texto_ocr, confianza = self.ocr_service.extract_text_with_confidence(
                    imagen_procesada
                )
                texto_normalizado = self.ocr_service.normalize_text(texto_ocr)
                self.logger.log_ocr(pdf_path, len(texto_normalizado), confianza)
                self.logger.debug(f"   [2/7] ✅ OCR (confianza: {confianza:.1f}%)")

                # Si la confianza es muy baja, advertir
                if confianza < 50:
                    self.logger.warning(
                        f"⚠️  Baja confianza OCR ({confianza:.1f}%) en {nombre_archivo}"
                    )

            except Exception as e:
                return self._manejar_error(
                    pdf_path,
                    "Error_OCR",
                    f"Error en OCR: {e}",
                    inicio
                )

            # PASO 3: Texto → Datos
            try:
                datos = self.extractor.extraer_datos(texto_normalizado)
                self.logger.log_extraccion(
                    pdf_path,
                    datos.cliente,
                    datos.fecha,
                    datos.numero
                )
                self.logger.debug(
                    f"   [3/7] ✅ Extracción (confianza: {datos.confianza:.1f}%)"
                )
            except Exception as e:
                return self._manejar_error(
                    pdf_path,
                    "Error_extraccion",
                    f"Error al extraer datos: {e}",
                    inicio
                )

            # PASO 4: Validación de datos
            es_valido, errores = self.extractor.validar_datos(datos)

            if not es_valido:
                mensaje_errores = "; ".join(errores)
                return self._manejar_error(
                    pdf_path,
                    "Datos_invalidos",
                    mensaje_errores,
                    inicio
                )

            self.logger.debug(f"   [4/7] ✅ Datos validados")

            # PASO 5: Crear entidades de dominio
            try:
                fecha_vo = FechaAlbaran(datos.fecha)
                numero_vo = NumeroAlbaran(datos.numero)
                cliente = Cliente(nombre=datos.cliente)

                self.logger.debug(f"   [5/7] ✅ Entidades creadas")

            except (DatosInvalidosException, ClienteInvalidoException) as e:
                return self._manejar_error(
                    pdf_path,
                    "Entidad_invalida",
                    str(e),
                    inicio
                )

            # PASO 6: Verificar duplicados
            if self.albaran_repo.exists(numero_vo, fecha_vo):
                self.logger.log_duplicado(pdf_path, int(numero_vo), str(fecha_vo))
                return self._manejar_error(
                    pdf_path,
                    "Duplicado",
                    f"Ya existe albarán #{numero_vo} del {fecha_vo}",
                    inicio,
                    es_duplicado=True
                )

            self.logger.debug(f"   [6/7] ✅ No duplicado")

            # PASO 7: Crear albarán
            albaran = Albaran(
                cliente=cliente,
                fecha=fecha_vo,
                numero=numero_vo,
                ruta_archivo_original=pdf_path,
            )

            # PASO 8: Guardar en BD
            try:
                # Guardar o actualizar cliente
                cliente_guardado = self.cliente_repo.save(cliente)
                cliente_guardado.incrementar_contador(fecha_vo.to_datetime())
                self.cliente_repo.save(cliente_guardado)

                # Guardar albarán
                albaran_guardado = self.albaran_repo.save(albaran)

                self.logger.debug(f"   [7/7] ✅ Guardado en BD (ID: {albaran_guardado.id})")

            except AlbaranDuplicadoException:
                # Duplicado detectado a nivel de BD (por si acaso)
                self.logger.log_duplicado(pdf_path, int(numero_vo), str(fecha_vo))
                return self._manejar_error(
                    pdf_path,
                    "Duplicado_BD",
                    f"Duplicado detectado en BD: #{numero_vo} del {fecha_vo}",
                    inicio,
                    es_duplicado=True
                )
            except Exception as e:
                return self._manejar_error(
                    pdf_path,
                    "Error_BD",
                    f"Error al guardar en BD: {e}",
                    inicio
                )

            # PASO 9: Mover archivo a carpeta del cliente
            try:
                nuevo_nombre = albaran.generar_nombre_archivo()
                carpeta_cliente = albaran.get_carpeta_destino()

                ruta_final = self.file_system.mover_a_carpeta_cliente(
                    archivo_origen=pdf_path,
                    nombre_cliente=carpeta_cliente,
                    nuevo_nombre=nuevo_nombre
                )

                # Actualizar ruta en albarán
                albaran_guardado.marcar_como_procesado(ruta_final)

                self.logger.log_movimiento_archivo(pdf_path, ruta_final)

            except FileExistsError:
                return self._manejar_error(
                    pdf_path,
                    "Archivo_existe",
                    "Ya existe un archivo con ese nombre en la carpeta del cliente",
                    inicio
                )
            except Exception as e:
                return self._manejar_error(
                    pdf_path,
                    "Error_movimiento",
                    f"Error al mover archivo: {e}",
                    inicio
                )

            # ÉXITO
            tiempo_ms = (time.time() - inicio) * 1000

            self.logger.log_procesamiento_exito(
                pdf_path,
                datos.cliente,
                datos.numero,
                datos.fecha,
                tiempo_ms
            )

            return ResultadoProcesamiento(
                exito=True,
                archivo=pdf_path,
                albaran=albaran_guardado,
                tiempo_ms=tiempo_ms
            )

        except Exception as e:
            # Error inesperado
            self.logger.error(
                f"Error inesperado procesando {nombre_archivo}: {e}",
                exc_info=True
            )
            return self._manejar_error(
                pdf_path,
                "Error_inesperado",
                str(e),
                inicio
            )

    def _manejar_error(
        self,
        pdf_path: str,
        razon: str,
        mensaje: str,
        inicio: float,
        es_duplicado: bool = False
    ) -> ResultadoProcesamiento:
        """
        Maneja un error moviendo el archivo a la carpeta de errores.

        Args:
            pdf_path: Ruta al PDF
            razon: Razón del error
            mensaje: Mensaje descriptivo
            inicio: Timestamp de inicio
            es_duplicado: Si es un error de duplicado

        Returns:
            ResultadoProcesamiento: Resultado con error
        """
        tiempo_ms = (time.time() - inicio) * 1000

        # Log
        if not es_duplicado:
            self.logger.log_procesamiento_error(pdf_path, mensaje)

        # Mover a carpeta de errores
        try:
            if self.file_system.existe_archivo(pdf_path):
                self.file_system.mover_a_errores(pdf_path, razon=razon)
                self.logger.debug(f"   ↘️  Movido a carpeta de errores")
        except Exception as e:
            self.logger.error(
                f"No se pudo mover a errores: {e}",
                exc_info=True
            )

        return ResultadoProcesamiento(
            exito=False,
            archivo=pdf_path,
            razon=mensaje,
            tiempo_ms=tiempo_ms
        )
