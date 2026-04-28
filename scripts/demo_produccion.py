"""
Demo de Sistema en Modo Producción.

Demuestra el sistema completo funcionando con:
- Monitor automático watchdog
- Pipeline completo de procesamiento
- Logging estructurado
- Manejo de errores
- Estadísticas en tiempo real

Ejecutar desde la raíz del proyecto:
    python scripts/demo_produccion.py
"""

import sys
import time
import tempfile
from pathlib import Path

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
from infrastructure.monitoring import WatchdogFileMonitor
from infrastructure.filesystem import FileSystemService
from infrastructure.logging import LoggerService


# Mock de OCR para el demo
class MockPDFProcessor:
    """Procesador de PDF simulado."""

    def pdf_first_page_to_image(self, pdf_path: str):
        return "imagen"

    def preprocess_image(self, image):
        return image


class MockTesseractOCRService:
    """Servicio OCR simulado."""

    def __init__(self):
        self.fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
        self.counter = 0

    def extract_text_with_confidence(self, image):
        """Simula OCR con diferentes resultados."""
        self.counter += 1

        if self.counter % 3 == 0:
            # Cada tercer archivo: texto de empresa ejemplo
            fixture = self.fixtures_dir / "sample_text_ocr_2.txt"
            if fixture.exists():
                with open(fixture, 'r', encoding='utf-8') as f:
                    return f.read(), 92.3
            return "EMPRESA TEST S.A.\nData 20/04/2026\nAlbarà núm. 82000", 90.0

        # Por defecto: METALCRISMAR
        fixture = self.fixtures_dir / "sample_text_ocr.txt"
        if fixture.exists():
            with open(fixture, 'r', encoding='utf-8') as f:
                texto = f.read()
            # Modificar número para evitar duplicados
            num = 71200 + self.counter
            texto = texto.replace("71206", str(num))
            return texto, 95.5

        return "METALCRISMAR, S.L.\nData 23/01/2026\nAlbarà núm. 71206", 90.0

    def normalize_text(self, texto: str) -> str:
        return texto.strip()


class SistemaProduccion:
    """
    Sistema de producción completo.

    Integra todos los componentes para funcionamiento real.
    """

    def __init__(self, carpeta_scanner: str, carpeta_albaranes: str):
        """
        Inicializa el sistema.

        Args:
            carpeta_scanner: Carpeta monitoreada para nuevos PDFs
            carpeta_albaranes: Carpeta base para guardar albaranes
        """
        self.carpeta_scanner = Path(carpeta_scanner)
        self.carpeta_albaranes = Path(carpeta_albaranes)
        self.carpeta_errores = self.carpeta_albaranes / "errores"
        self.archivo_bd = self.carpeta_albaranes / "database" / "albaranes.db"
        self.archivo_log = self.carpeta_albaranes / "logs" / "app.log"

        # Crear carpetas
        self.carpeta_scanner.mkdir(parents=True, exist_ok=True)

        # Componentes
        self.db = None
        self.monitor = None
        self.logger = None
        self.use_case = None

    def inicializar(self):
        """Inicializa todos los componentes."""
        print("🔧 Inicializando sistema de producción...")

        # Logger
        self.logger = LoggerService(
            nombre_logger="ScannerSufexa",
            archivo_log=str(self.archivo_log),
            nivel="INFO",
            log_consola=True
        )
        print(f"   ✅ Logger configurado")
        print(f"      Log: {self.archivo_log}")

        # Base de datos
        self.db = Database(str(self.archivo_bd))
        self.db.connect()
        self.db.initialize_schema()
        print(f"   ✅ Base de datos inicializada")
        print(f"      BD: {self.archivo_bd}")

        # Repositorios
        albaran_repo = SQLiteAlbaranRepository(self.db)
        cliente_repo = SQLiteClienteRepository(self.db)
        print(f"   ✅ Repositorios creados")

        # Servicios
        extractor = ExtractorDatosService()
        file_system = FileSystemService(
            carpeta_salida_base=str(self.carpeta_albaranes),
            carpeta_errores=str(self.carpeta_errores)
        )
        pdf_processor = MockPDFProcessor()
        ocr_service = MockTesseractOCRService()
        print(f"   ✅ Servicios inicializados")

        # Caso de uso
        self.use_case = ProcesarAlbaranUseCase(
            pdf_processor=pdf_processor,
            ocr_service=ocr_service,
            extractor=extractor,
            albaran_repo=albaran_repo,
            cliente_repo=cliente_repo,
            file_system=file_system,
            logger=self.logger
        )
        print(f"   ✅ Caso de uso configurado")

        # Monitor
        self.monitor = WatchdogFileMonitor(
            carpeta_monitoreada=str(self.carpeta_scanner),
            callback_procesamiento=lambda path: self.use_case.ejecutar(path).exito,
            tiempo_espera=0.5,
            intervalo_chequeo=0.3,
            verbose=False  # Usamos nuestro logger
        )
        print(f"   ✅ Monitor configurado")
        print(f"      Carpeta: {self.carpeta_scanner}")

        self.logger.info("✅ Sistema inicializado completamente")

    def iniciar(self):
        """Inicia el sistema."""
        self.logger.log_monitor_inicio(str(self.carpeta_scanner))
        self.logger.separador()
        self.monitor.start()

    def detener(self):
        """Detiene el sistema."""
        self.logger.separador()
        self.logger.log_monitor_detenido()
        self.monitor.stop()

    def cerrar(self):
        """Cierra la base de datos."""
        if self.db:
            self.db.disconnect()

    def mostrar_estadisticas(self, albaran_repo, cliente_repo):
        """Muestra estadísticas del sistema."""
        total_albaranes = albaran_repo.count()
        total_clientes = cliente_repo.count()

        self.logger.separador()
        self.logger.info("📊 ESTADÍSTICAS FINALES")
        self.logger.log_estadisticas(
            total=self.monitor.archivos_procesados + self.monitor.archivos_con_error,
            exitosos=self.monitor.archivos_procesados,
            errores=self.monitor.archivos_con_error
        )
        self.logger.info(f"   Albaranes en BD: {total_albaranes}")
        self.logger.info(f"   Clientes únicos: {total_clientes}")

        # Ranking
        if total_clientes > 0:
            self.logger.info("\n🏆 TOP CLIENTES:")
            ranking = cliente_repo.get_ranking(top_n=5)
            for i, cliente in enumerate(ranking, 1):
                self.logger.info(
                    f"   {i}. {cliente.nombre[:40]:40} - {cliente.total_albaranes} albarán(es)"
                )

        self.logger.separador()


def simular_llegada_archivos(carpeta: Path, num_archivos: int = 5):
    """Simula la llegada de archivos al scanner."""
    print(f"\n📄 Simulando llegada de {num_archivos} albaranes...")
    print("   (Los archivos se detectarán y procesarán automáticamente)\n")

    for i in range(num_archivos):
        nombre = f"albaran_{i+1:03d}.pdf"
        archivo = carpeta / nombre
        archivo.write_text(f"PDF simulado {i+1}")
        print(f"   [{i+1}/{num_archivos}] Escaneado: {nombre}")
        time.sleep(1.2)

    print(f"\n   ✅ {num_archivos} archivos escaneados")
    print("   ⏳ Esperando a que terminen de procesarse...\n")


def main():
    """Función principal del demo."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║              DEMO: SISTEMA DE PRODUCCIÓN COMPLETO                  ║")
    print("║                    Scanner Sufexa v1.0                             ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        carpeta_scanner = base / "scan" / "entrada"
        carpeta_albaranes = base / "albaranes"

        print(f"📁 Estructura temporal:")
        print(f"   Scanner:   {carpeta_scanner}")
        print(f"   Albaranes: {carpeta_albaranes}")
        print()

        # Crear sistema
        sistema = SistemaProduccion(
            carpeta_scanner=str(carpeta_scanner),
            carpeta_albaranes=str(carpeta_albaranes)
        )

        try:
            # Inicializar
            sistema.inicializar()

            print()
            print("=" * 70)
            print("▶️  INICIANDO SISTEMA")
            print("=" * 70)
            print()

            # Iniciar monitor
            sistema.iniciar()
            time.sleep(1)

            # Simular llegada de archivos
            simular_llegada_archivos(carpeta_scanner, num_archivos=6)

            # Esperar procesamiento
            time.sleep(8)

            # Detener
            print("\n" + "=" * 70)
            print("🛑 DETENIENDO SISTEMA")
            print("=" * 70)
            print()

            # Estadísticas (antes de cerrar BD)
            albaran_repo = SQLiteAlbaranRepository(sistema.db)
            cliente_repo = SQLiteClienteRepository(sistema.db)
            sistema.mostrar_estadisticas(albaran_repo, cliente_repo)

            sistema.detener()
            sistema.cerrar()

            # Mostrar estructura generada
            print("\n📂 ESTRUCTURA DE ARCHIVOS GENERADA:")
            print("-" * 70)

            for carpeta in carpeta_albaranes.iterdir():
                if carpeta.is_dir() and carpeta.name not in ["database", "logs"]:
                    archivos = list(carpeta.glob("*.pdf"))
                    if archivos:
                        print(f"\n   📂 {carpeta.name}/")
                        for archivo in archivos:
                            tamano = archivo.stat().st_size
                            print(f"      └─ {archivo.name} ({tamano} bytes)")

            # Mostrar log
            if sistema.archivo_log.exists():
                print(f"\n📝 LOG GENERADO:")
                print(f"   {sistema.archivo_log}")
                lineas = sistema.archivo_log.read_text().split('\n')
                print(f"   Líneas: {len(lineas)}")
                print(f"   Tamaño: {sistema.archivo_log.stat().st_size} bytes")

            print("\n" + "=" * 70)
            print("✅ DEMO COMPLETADO")
            print("=" * 70)

            print("\n💡 SISTEMA LISTO PARA PRODUCCIÓN:")
            print("   ✅ Procesamiento automático 24/7")
            print("   ✅ Pipeline completo: PDF → OCR → BD → Archivo")
            print("   ✅ Prevención de duplicados")
            print("   ✅ Manejo robusto de errores")
            print("   ✅ Logging completo y trazable")
            print("   ✅ Estadísticas en tiempo real")
            print("   ✅ Organización automática por cliente")
            print("\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Sistema interrumpido por el usuario")
            sistema.detener()
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sistema.detener()


if __name__ == "__main__":
    main()
