"""
Script de prueba del pipeline completo de procesamiento.

Simula el procesamiento end-to-end con todos los componentes.

Ejecutar desde la raíz del proyecto:
    python scripts/test_pipeline_completo.py
"""

import sys
import time
import tempfile
from pathlib import Path
from datetime import datetime

# Añadir src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from application.use_cases import ProcesarAlbaranUseCase
from application.services import ExtractorDatosService
from infrastructure.persistence.database import Database
from infrastructure.persistence.repositories import (
    SQLiteAlbaranRepository,
    SQLiteClienteRepository,
)
from infrastructure.filesystem import FileSystemService
from infrastructure.logging import LoggerService


# Mock de OCR para pruebas sin Tesseract
class MockPDFProcessor:
    """Procesador de PDF simulado para testing."""

    def pdf_first_page_to_image(self, pdf_path: str):
        """Simula conversión PDF a imagen."""
        return "imagen_simulada"

    def preprocess_image(self, image):
        """Simula preprocesamiento."""
        return image


class MockTesseractOCRService:
    """Servicio OCR simulado para testing."""

    def __init__(self):
        self.fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"

    def extract_text_with_confidence(self, image):
        """Simula extracción OCR."""
        # Cargar texto de prueba
        fixture = self.fixtures_dir / "sample_text_ocr.txt"
        if fixture.exists():
            with open(fixture, 'r', encoding='utf-8') as f:
                texto = f.read()
            return texto, 95.5  # Buena confianza

        # Fallback
        return """
METALCRISMAR, S.L.
ALBARÀ DE LLIURAMENT
Data 23/01/2026
Albarà núm. 71206
        """, 90.0

    def normalize_text(self, texto: str) -> str:
        """Normaliza texto."""
        return texto.strip()


def crear_pdf_prueba(ruta: Path, nombre: str) -> Path:
    """Crea un archivo PDF de prueba."""
    archivo = ruta / nombre
    archivo.write_text(f"PDF simulado: {nombre}")
    return archivo


def test_procesamiento_exitoso():
    """Prueba un procesamiento exitoso."""
    print("=" * 70)
    print("PRUEBA 1: PROCESAMIENTO EXITOSO")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        carpeta_albaranes = base / "albaranes"
        carpeta_errores = base / "albaranes" / "errores"
        archivo_log = base / "logs" / "app.log"

        # Inicializar componentes
        db = Database(":memory:")
        db.connect()
        db.initialize_schema()

        albaran_repo = SQLiteAlbaranRepository(db)
        cliente_repo = SQLiteClienteRepository(db)
        extractor = ExtractorDatosService()
        file_system = FileSystemService(
            carpeta_salida_base=str(carpeta_albaranes),
            carpeta_errores=str(carpeta_errores)
        )
        logger = LoggerService(
            archivo_log=str(archivo_log),
            nivel="DEBUG",
            log_consola=True
        )

        # Mocks de OCR
        pdf_processor = MockPDFProcessor()
        ocr_service = MockTesseractOCRService()

        # Caso de uso
        use_case = ProcesarAlbaranUseCase(
            pdf_processor=pdf_processor,
            ocr_service=ocr_service,
            extractor=extractor,
            albaran_repo=albaran_repo,
            cliente_repo=cliente_repo,
            file_system=file_system,
            logger=logger
        )

        # Crear PDF de prueba
        pdf = crear_pdf_prueba(base, "albaran_test.pdf")

        # Procesar
        print(f"\n📄 Procesando: {pdf.name}\n")
        resultado = use_case.ejecutar(str(pdf))

        # Verificar resultado
        print(f"\n📊 RESULTADO:")
        print(f"   Éxito: {resultado.exito}")
        print(f"   Tiempo: {resultado.tiempo_ms:.2f}ms")

        if resultado.exito:
            print(f"   ✅ Albarán guardado (ID: {resultado.albaran.id})")
            print(f"   ✅ Cliente: {resultado.albaran.cliente.nombre}")
            print(f"   ✅ Número: {resultado.albaran.numero}")
            print(f"   ✅ Fecha: {resultado.albaran.fecha}")
        else:
            print(f"   ❌ Razón: {resultado.razon}")

        # Verificar archivo movido
        archivos_cliente = list(carpeta_albaranes.glob("**/*.pdf"))
        print(f"\n📁 Archivos generados: {len(archivos_cliente)}")
        for archivo in archivos_cliente:
            print(f"   • {archivo.relative_to(carpeta_albaranes)}")

        # Verificar log
        if archivo_log.exists():
            print(f"\n📝 Log generado: {archivo_log}")
            lineas = archivo_log.read_text().split('\n')
            print(f"   Líneas de log: {len(lineas)}")

        db.disconnect()

        assert resultado.exito, "El procesamiento debería ser exitoso"
        assert len(archivos_cliente) == 1, "Debería haber 1 archivo"

        print("\n✅ Prueba exitosa")


def test_procesamiento_duplicado():
    """Prueba detección de duplicados."""
    print("\n" + "=" * 70)
    print("PRUEBA 2: DETECCIÓN DE DUPLICADOS")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        carpeta_albaranes = base / "albaranes"
        carpeta_errores = base / "albaranes" / "errores"

        # Inicializar componentes
        db = Database(":memory:")
        db.connect()
        db.initialize_schema()

        albaran_repo = SQLiteAlbaranRepository(db)
        cliente_repo = SQLiteClienteRepository(db)
        extractor = ExtractorDatosService()
        file_system = FileSystemService(
            carpeta_salida_base=str(carpeta_albaranes),
            carpeta_errores=str(carpeta_errores)
        )
        logger = LoggerService(nivel="INFO", log_consola=True)

        pdf_processor = MockPDFProcessor()
        ocr_service = MockTesseractOCRService()

        use_case = ProcesarAlbaranUseCase(
            pdf_processor=pdf_processor,
            ocr_service=ocr_service,
            extractor=extractor,
            albaran_repo=albaran_repo,
            cliente_repo=cliente_repo,
            file_system=file_system,
            logger=logger
        )

        # Procesar primer archivo
        pdf1 = crear_pdf_prueba(base, "albaran_1.pdf")
        print(f"\n📄 Procesando archivo 1: {pdf1.name}\n")
        resultado1 = use_case.ejecutar(str(pdf1))

        print(f"\n   Resultado 1: {'✅ Éxito' if resultado1.exito else '❌ Error'}")

        # Procesar segundo archivo (mismo albarán - duplicado)
        pdf2 = crear_pdf_prueba(base, "albaran_2.pdf")
        print(f"\n📄 Procesando archivo 2 (duplicado): {pdf2.name}\n")
        resultado2 = use_case.ejecutar(str(pdf2))

        print(f"\n   Resultado 2: {'✅ Éxito' if resultado2.exito else '❌ Error (esperado)'}")
        if not resultado2.exito:
            print(f"   Razón: {resultado2.razon}")

        # Verificar que el duplicado fue a errores
        archivos_error = list(carpeta_errores.glob("*.pdf"))
        print(f"\n📁 Archivos en carpeta de errores: {len(archivos_error)}")
        for archivo in archivos_error:
            print(f"   • {archivo.name}")

        db.disconnect()

        assert resultado1.exito, "Primer archivo debería procesarse"
        assert not resultado2.exito, "Segundo archivo debería fallar por duplicado"
        assert len(archivos_error) == 1, "Debería haber 1 archivo en errores"

        print("\n✅ Prueba exitosa - Duplicado detectado correctamente")


def test_pipeline_completo_multiples():
    """Prueba procesamiento de múltiples archivos."""
    print("\n" + "=" * 70)
    print("PRUEBA 3: PROCESAMIENTO MÚLTIPLE")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        carpeta_albaranes = base / "albaranes"
        carpeta_errores = base / "albaranes" / "errores"

        db = Database(":memory:")
        db.connect()
        db.initialize_schema()

        albaran_repo = SQLiteAlbaranRepository(db)
        cliente_repo = SQLiteClienteRepository(db)
        extractor = ExtractorDatosService()
        file_system = FileSystemService(
            carpeta_salida_base=str(carpeta_albaranes),
            carpeta_errores=str(carpeta_errores)
        )
        logger = LoggerService(nivel="WARNING", log_consola=True)

        pdf_processor = MockPDFProcessor()
        ocr_service = MockTesseractOCRService()

        use_case = ProcesarAlbaranUseCase(
            pdf_processor=pdf_processor,
            ocr_service=ocr_service,
            extractor=extractor,
            albaran_repo=albaran_repo,
            cliente_repo=cliente_repo,
            file_system=file_system,
            logger=logger
        )

        # Procesar 5 archivos
        archivos = [
            "albaran_001.pdf",
            "albaran_002.pdf",
            "albaran_003.pdf",
            "albaran_001.pdf",  # Duplicado
            "albaran_004.pdf",
        ]

        resultados = []
        print(f"\n📄 Procesando {len(archivos)} archivos...\n")

        for nombre in archivos:
            pdf = crear_pdf_prueba(base, nombre)
            resultado = use_case.ejecutar(str(pdf))
            resultados.append(resultado)

            estado = "✅" if resultado.exito else "❌"
            print(f"   {estado} {nombre} - {resultado.tiempo_ms:.2f}ms")

        # Estadísticas
        exitosos = sum(1 for r in resultados if r.exito)
        errores = len(resultados) - exitosos

        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total: {len(resultados)}")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Errores: {errores}")

        # Verificar BD
        total_albaranes = albaran_repo.count()
        total_clientes = cliente_repo.count()

        print(f"\n💾 BASE DE DATOS:")
        print(f"   Albaranes: {total_albaranes}")
        print(f"   Clientes: {total_clientes}")

        db.disconnect()

        print("\n✅ Prueba completada")


def main():
    """Función principal."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           PRUEBAS DEL PIPELINE COMPLETO DE PROCESAMIENTO          ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    try:
        test_procesamiento_exitoso()
        test_procesamiento_duplicado()
        test_pipeline_completo_multiples()

        print("\n" + "=" * 70)
        print("🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ Prueba fallida: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
