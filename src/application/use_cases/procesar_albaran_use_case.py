"""
Caso de uso: Procesar Albarán Completo.

Orquesta todo el pipeline de procesamiento.
"""

import time
from pathlib import Path
from typing import Optional
from collections import Counter

from domain.entities import Albaran, Cliente
from domain.value_objects import FechaAlbaran, NumeroAlbaran
from domain.repositories import IAlbaranRepository, IClienteRepository
from domain.exceptions import (
    AlbaranDuplicadoException,
    DatosInvalidosException,
    ClienteInvalidoException
)
from application.services import ExtractorDatosService, ClienteLookupService
from application.services.extractor_datos_service import DatosExtraidos
from infrastructure.filesystem import FileSystemService
from infrastructure.logging import LoggerService

try:
    from infrastructure.ocr import TesseractOCRService, PDFProcessor
except ImportError:
    TesseractOCRService = None
    PDFProcessor = None


class ResultadoProcesamiento:
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
    Pipeline:
    1. PDF → Imagen
    2. Imagen → Texto (OCR, 6 variantes con votación)
    3. Texto → Datos (numero_cliente, fecha, numero_albaran)
    4. numero_cliente → nombre exacto (CSV lookup)
    5. Validación de datos
    6. Verificación de duplicados
    7. Guardado en BD
    8. Movimiento de archivo
    """

    def __init__(
        self,
        pdf_processor: PDFProcessor,
        ocr_service: TesseractOCRService,
        extractor: ExtractorDatosService,
        albaran_repo: IAlbaranRepository,
        cliente_repo: IClienteRepository,
        file_system: FileSystemService,
        logger: LoggerService,
        cliente_lookup: Optional[ClienteLookupService] = None
    ):
        self.pdf_processor = pdf_processor
        self.ocr_service = ocr_service
        self.extractor = extractor
        self.albaran_repo = albaran_repo
        self.cliente_repo = cliente_repo
        self.file_system = file_system
        self.logger = logger
        self.cliente_lookup = cliente_lookup

    def ejecutar(self, pdf_path: str) -> ResultadoProcesamiento:
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
                    pdf_path, "Error_PDF",
                    f"No se pudo procesar el PDF: {e}", inicio
                )

            # PASO 2+3: OCR multi-variante con votación por campo
            try:
                variantes = self.pdf_processor.get_image_variants(imagen)
                datos = DatosExtraidos()
                confianza = 0.0
                votos_numero = []
                votos_fecha = []
                votos_num_cliente = []

                texto_var0 = ""  # guardamos el texto de variante 0 para diagnóstico
                for i_var, variante in enumerate(variantes):
                    try:
                        texto_ocr, conf = self.ocr_service.extract_text_with_confidence(variante)
                    except Exception:
                        continue

                    texto_norm = self.ocr_service.normalize_text(texto_ocr)
                    if i_var == 0:
                        texto_var0 = texto_norm

                    candidato = self.extractor.extraer_datos(texto_norm)
                    confianza = max(confianza, conf)

                    if candidato.numero is not None:
                        votos_numero.append(candidato.numero)
                    if candidato.fecha is not None:
                        votos_fecha.append(candidato.fecha)
                    if candidato.numero_cliente is not None:
                        votos_num_cliente.append(candidato.numero_cliente)

                    self.logger.debug(
                        f"   Variante {i_var}: num={candidato.numero} "
                        f"fecha={candidato.fecha} num_cliente={candidato.numero_cliente}"
                    )

                # Pasada adicional: OCR dedicado sobre la zona inferior-derecha
                # donde Sufexa imprime el número de cliente. Se usa PSM 7
                # (línea única) y crops ampliados 3x para leer dígitos
                # pegados al borde del recuadro.
                try:
                    crops_zona = self.pdf_processor.get_zona_numero_cliente(imagen)
                    for crop in crops_zona:
                        try:
                            import pytesseract
                            texto_crop = pytesseract.image_to_string(
                                crop,
                                lang=self.ocr_service.language,
                                config='--psm 6'
                            )
                            texto_crop_norm = self.ocr_service.normalize_text(texto_crop)
                            num_cand = self.extractor.extraer_numero_cliente(texto_crop_norm)
                            if num_cand:
                                votos_num_cliente.append(num_cand)
                                self.logger.debug(f"   Zona num_cliente: {num_cand}")
                        except Exception:
                            pass
                except Exception:
                    pass

                # Número, fecha y número de cliente por mayoría de votos
                if votos_numero:
                    datos.numero = Counter(votos_numero).most_common(1)[0][0]
                if votos_fecha:
                    datos.fecha = Counter(votos_fecha).most_common(1)[0][0]
                if votos_num_cliente:
                    datos.numero_cliente = Counter(votos_num_cliente).most_common(1)[0][0]

                datos.confianza = confianza
                self.logger.log_ocr(pdf_path, 0, confianza)
                self.logger.debug(
                    f"   [2/7] ✅ OCR+Extracción: num={datos.numero} "
                    f"fecha={datos.fecha} num_cliente={datos.numero_cliente}"
                )

            except Exception as e:
                return self._manejar_error(
                    pdf_path, "Error_OCR",
                    f"Error en OCR: {e}", inicio
                )

            # PASO 3: Lookup del nombre por número de cliente
            if not datos.numero_cliente:
                # Incluir texto OCR en el error para diagnóstico
                ocr_muestra = texto_var0[:500].replace('\n', '|') if texto_var0 else "SIN_TEXTO"
                return self._manejar_error(
                    pdf_path,
                    "CLIENTE_NO_DETECTADO",
                    f"No se pudo extraer el número de cliente. OCR: {ocr_muestra}",
                    inicio
                )

            if self.cliente_lookup:
                nombre = self.cliente_lookup.buscar_por_numero(datos.numero_cliente)
                self.logger.debug(
                    f"   Lookup: '{datos.numero_cliente}' → '{nombre}' "
                    f"({self.cliente_lookup.total_clientes()} clientes cargados)"
                )
                if nombre is None:
                    return self._manejar_error(
                        pdf_path,
                        "CLIENTE_NO_ENCONTRADO_EN_CSV",
                        f"Número de cliente '{datos.numero_cliente}' no encontrado en el archivo de clientes",
                        inicio
                    )
                datos.cliente = nombre
            else:
                # Sin lookup configurado — usar número como nombre provisional
                datos.cliente = datos.numero_cliente
                self.logger.debug("   ⚠️  Sin lookup configurado — usando número como nombre")

            # PASO 4: Validación de datos
            es_valido, errores = self.extractor.validar_datos(datos)
            if not es_valido:
                return self._manejar_error(
                    pdf_path, "Datos_invalidos",
                    "; ".join(errores), inicio
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
                    pdf_path, "Entidad_invalida",
                    str(e), inicio
                )

            # PASO 6: Verificar duplicados
            if self.albaran_repo.exists(numero_vo, fecha_vo):
                self.logger.log_duplicado(pdf_path, int(numero_vo), str(fecha_vo))
                return self._manejar_error(
                    pdf_path, "Duplicado",
                    f"Ya existe albarán #{numero_vo} del {fecha_vo}",
                    inicio, es_duplicado=True
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
                cliente_guardado = self.cliente_repo.save(cliente)
                cliente_guardado.incrementar_contador(fecha_vo.to_datetime())
                self.cliente_repo.save(cliente_guardado)

                albaran_guardado = self.albaran_repo.save(albaran)
                self.logger.debug(f"   [7/7] ✅ Guardado en BD (ID: {albaran_guardado.id})")

            except AlbaranDuplicadoException:
                self.logger.log_duplicado(pdf_path, int(numero_vo), str(fecha_vo))
                return self._manejar_error(
                    pdf_path, "Duplicado_BD",
                    f"Duplicado detectado en BD: #{numero_vo} del {fecha_vo}",
                    inicio, es_duplicado=True
                )
            except Exception as e:
                return self._manejar_error(
                    pdf_path, "Error_BD",
                    f"Error al guardar en BD: {e}", inicio
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

                albaran_guardado.marcar_como_procesado(ruta_final)
                self.logger.log_movimiento_archivo(pdf_path, ruta_final)

            except FileExistsError:
                return self._manejar_error(
                    pdf_path, "Archivo_existe",
                    "Ya existe un archivo con ese nombre en la carpeta del cliente",
                    inicio
                )
            except Exception as e:
                return self._manejar_error(
                    pdf_path, "Error_movimiento",
                    f"Error al mover archivo: {e}", inicio
                )

            # ÉXITO
            tiempo_ms = (time.time() - inicio) * 1000
            self.logger.log_procesamiento_exito(
                pdf_path, datos.cliente, datos.numero, datos.fecha, tiempo_ms
            )

            return ResultadoProcesamiento(
                exito=True,
                archivo=pdf_path,
                albaran=albaran_guardado,
                tiempo_ms=tiempo_ms
            )

        except Exception as e:
            self.logger.error(
                f"Error inesperado procesando {nombre_archivo}: {e}",
                exc_info=True
            )
            return self._manejar_error(
                pdf_path, "Error_inesperado", str(e), inicio
            )

    def _manejar_error(
        self,
        pdf_path: str,
        razon: str,
        mensaje: str,
        inicio: float,
        es_duplicado: bool = False
    ) -> ResultadoProcesamiento:
        tiempo_ms = (time.time() - inicio) * 1000

        if not es_duplicado:
            self.logger.log_procesamiento_error(pdf_path, mensaje)

        try:
            if self.file_system.existe_archivo(pdf_path):
                self.file_system.mover_a_errores(pdf_path, razon=razon)
                self.logger.debug(f"   ↘️  Movido a carpeta de errores")
        except Exception as e:
            self.logger.error(f"No se pudo mover a errores: {e}", exc_info=True)

        return ResultadoProcesamiento(
            exito=False,
            archivo=pdf_path,
            razon=mensaje,
            tiempo_ms=tiempo_ms
        )
