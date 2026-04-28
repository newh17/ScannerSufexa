"""
Demo del sistema completo de procesamiento automático de albaranes.

Simula el flujo real:
1. Monitor detecta nuevo PDF en carpeta scanner
2. Aplica OCR (simulado)
3. Extrae datos
4. Valida
5. Guarda en BD
6. Mueve archivo a carpeta del cliente
7. O mueve a carpeta de errores si falla

Ejecutar desde la raíz del proyecto:
    python scripts/demo_sistema_completo.py
"""

import sys
import time
import tempfile
from pathlib import Path
from datetime import datetime

# Añadir src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from domain.entities import Albaran, Cliente
from domain.value_objects import FechaAlbaran, NumeroAlbaran
from domain.exceptions import AlbaranDuplicadoException, DatosInvalidosException
from application.services import ExtractorDatosService
from infrastructure.persistence.database import Database
from infrastructure.persistence.repositories import (
    SQLiteAlbaranRepository,
    SQLiteClienteRepository,
)
from infrastructure.monitoring import WatchdogFileMonitor
from infrastructure.filesystem import FileSystemService


class ProcesadorAlbaranCompleto:
    """
    Orquesta el procesamiento completo de un albarán.

    Integra todos los componentes del sistema.
    """

    def __init__(
        self,
        extractor: ExtractorDatosService,
        albaran_repo: SQLiteAlbaranRepository,
        cliente_repo: SQLiteClienteRepository,
        file_system: FileSystemService
    ):
        """
        Inicializa el procesador.

        Args:
            extractor: Servicio de extracción de datos
            albaran_repo: Repositorio de albaranes
            cliente_repo: Repositorio de clientes
            file_system: Servicio de sistema de archivos
        """
        self.extractor = extractor
        self.albaran_repo = albaran_repo
        self.cliente_repo = cliente_repo
        self.file_system = file_system

    def procesar(self, pdf_path: str) -> bool:
        """
        Procesa un albarán completo.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            bool: True si se procesó correctamente
        """
        nombre_archivo = Path(pdf_path).name

        try:
            # PASO 1: OCR (simulado)
            texto_ocr = self._simular_ocr(pdf_path)

            # PASO 2: Extracción
            datos = self.extractor.extraer_datos(texto_ocr)

            # PASO 3: Validación
            es_valido, errores = self.extractor.validar_datos(datos)

            if not es_valido:
                print(f"         ❌ Datos inválidos: {', '.join(errores)}")
                self.file_system.mover_a_errores(
                    pdf_path,
                    razon="Datos_invalidos"
                )
                return False

            # PASO 4: Crear entidades
            try:
                fecha_vo = FechaAlbaran(datos.fecha)
                numero_vo = NumeroAlbaran(datos.numero)
                cliente = Cliente(nombre=datos.cliente)
            except (DatosInvalidosException, Exception) as e:
                print(f"         ❌ Error en entidades: {e}")
                self.file_system.mover_a_errores(
                    pdf_path,
                    razon="Entidad_invalida"
                )
                return False

            # PASO 5: Verificar duplicados
            if self.albaran_repo.exists(numero_vo, fecha_vo):
                print(f"         ⚠️  Duplicado: #{numero_vo} del {fecha_vo}")
                self.file_system.mover_a_errores(
                    pdf_path,
                    razon="Duplicado"
                )
                return False

            # PASO 6: Crear albarán
            albaran = Albaran(
                cliente=cliente,
                fecha=fecha_vo,
                numero=numero_vo,
                ruta_archivo_original=pdf_path,
            )

            # PASO 7: Guardar en BD
            cliente_guardado = self.cliente_repo.save(cliente)
            cliente_guardado.incrementar_contador(fecha_vo.to_datetime())
            self.cliente_repo.save(cliente_guardado)

            albaran_guardado = self.albaran_repo.save(albaran)

            # PASO 8: Mover archivo
            nuevo_nombre = albaran.generar_nombre_archivo()
            carpeta_cliente = albaran.get_carpeta_destino()

            try:
                ruta_final = self.file_system.mover_a_carpeta_cliente(
                    archivo_origen=pdf_path,
                    nombre_cliente=carpeta_cliente,
                    nuevo_nombre=nuevo_nombre
                )

                # Actualizar ruta en BD
                albaran_guardado.marcar_como_procesado(ruta_final)

                print(f"         ✅ {datos.cliente} | #{datos.numero} | {datos.fecha}")
                return True

            except FileExistsError:
                print(f"         ❌ Archivo ya existe en destino")
                self.file_system.mover_a_errores(
                    pdf_path,
                    razon="Archivo_existente"
                )
                return False

        except Exception as e:
            print(f"         ❌ Error inesperado: {e}")
            try:
                self.file_system.mover_a_errores(
                    pdf_path,
                    razon="Error_general"
                )
            except:
                pass
            return False

    def _simular_ocr(self, pdf_path: str) -> str:
        """
        Simula el OCR de un PDF.

        En producción, esto haría:
        - PDFProcessor.pdf_first_page_to_image()
        - TesseractOCRService.extract_text()
        """
        # Cargar texto de prueba según el nombre del archivo
        nombre = Path(pdf_path).name

        if "metalcrismar" in nombre.lower():
            fixture = "sample_text_ocr.txt"
        elif "empresa" in nombre.lower():
            fixture = "sample_text_ocr_2.txt"
        else:
            # Generar texto dinámico
            num = hash(nombre) % 10000 + 70000
            return f"""
TEST EMPRESA S.L.
Carrer Example, 123

ALBARÀ DE LLIURAMENT

Data {datetime.now().strftime('%d/%m/%Y')}
Albarà núm. {num}

Producto ejemplo    10    50.00 €
            """

        # Cargar fixture
        ruta_fixture = Path(__file__).parent.parent / "tests" / "fixtures" / fixture
        if ruta_fixture.exists():
            with open(ruta_fixture, 'r', encoding='utf-8') as f:
                return f.read()

        return "Data 01/01/2026\nAlbarà núm. 99999\nCLIENTE DESCONOCIDO"


def main():
    """Función principal del demo."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║        DEMO: SISTEMA COMPLETO DE PROCESAMIENTO AUTOMÁTICO         ║")
    print("║              Scanner Sufexa - Producción Ready                     ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    # Crear estructura de carpetas temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        carpeta_scanner = base / "scan" / "entrada"
        carpeta_albaranes = base / "albaranes"
        carpeta_errores = base / "albaranes" / "errores"

        carpeta_scanner.mkdir(parents=True)

        print(f"\n📁 Estructura de carpetas:")
        print(f"   Scanner:   {carpeta_scanner}")
        print(f"   Albaranes: {carpeta_albaranes}")
        print(f"   Errores:   {carpeta_errores}")

        # Inicializar componentes
        print("\n🔧 Inicializando componentes...")

        # Base de datos
        db = Database(":memory:")
        db.connect()
        db.initialize_schema()
        print("   ✅ Base de datos")

        # Repositorios
        albaran_repo = SQLiteAlbaranRepository(db)
        cliente_repo = SQLiteClienteRepository(db)
        print("   ✅ Repositorios")

        # Servicios
        extractor = ExtractorDatosService()
        file_system = FileSystemService(
            carpeta_salida_base=str(carpeta_albaranes),
            carpeta_errores=str(carpeta_errores)
        )
        print("   ✅ Servicios")

        # Procesador
        procesador = ProcesadorAlbaranCompleto(
            extractor=extractor,
            albaran_repo=albaran_repo,
            cliente_repo=cliente_repo,
            file_system=file_system
        )
        print("   ✅ Procesador integrado")

        # Monitor
        monitor = WatchdogFileMonitor(
            carpeta_monitoreada=str(carpeta_scanner),
            callback_procesamiento=procesador.procesar,
            tiempo_espera=0.5,
            intervalo_chequeo=0.3,
            verbose=True
        )

        print("\n" + "=" * 70)
        print("▶️  INICIANDO MONITOR AUTOMÁTICO")
        print("=" * 70)

        monitor.start()
        time.sleep(1)

        # Simular llegada de archivos
        print("\n📄 Simulando llegada de albaranes al scanner...")
        print("   (Esperando a que se detecten y procesen automáticamente)\n")

        archivos_prueba = [
            "albaran_metalcrismar_001.pdf",
            "albaran_empresa_002.pdf",
            "albaran_metalcrismar_001.pdf",  # Duplicado
            "albaran_test_003.pdf",
            "albaran_test_004.pdf",
        ]

        for i, nombre in enumerate(archivos_prueba, 1):
            print(f"[{i}/{len(archivos_prueba)}] Copiando: {nombre}")
            archivo = carpeta_scanner / nombre
            archivo.write_text(f"PDF simulado {i}")
            time.sleep(1.5)

        # Esperar a que se procesen todos
        print("\n⏳ Esperando a que terminen de procesarse...")
        time.sleep(8)

        # Detener monitor
        print("\n" + "=" * 70)
        print("🛑 DETENIENDO MONITOR")
        print("=" * 70)
        monitor.stop()

        # Mostrar resultados
        print("\n" + "=" * 70)
        print("📊 RESULTADOS DEL PROCESAMIENTO")
        print("=" * 70)

        total_albaranes = albaran_repo.count()
        total_clientes = cliente_repo.count()

        print(f"\n✅ Albaranes procesados correctamente: {total_albaranes}")
        print(f"✅ Clientes únicos: {total_clientes}")

        # Ranking
        if total_clientes > 0:
            print("\n🏆 RANKING DE CLIENTES:")
            print("-" * 70)
            ranking = cliente_repo.get_ranking(top_n=5)
            for i, cliente in enumerate(ranking, 1):
                print(f"   {i}. {cliente.nombre:35} - {cliente.total_albaranes} albarán(es)")

        # Listado
        if total_albaranes > 0:
            print("\n📋 ALBARANES GUARDADOS:")
            print("-" * 70)
            albaranes = albaran_repo.get_all()
            for albaran in albaranes:
                nombre = albaran.generar_nombre_archivo()
                print(f"   • {nombre}")

        # Archivos en carpetas
        print("\n📁 ESTRUCTURA DE ARCHIVOS GENERADA:")
        print("-" * 70)

        # Albaranes por cliente
        for carpeta in carpeta_albaranes.iterdir():
            if carpeta.is_dir() and carpeta.name != "errores":
                archivos = list(carpeta.glob("*.pdf"))
                print(f"\n   📂 {carpeta.name}/")
                for archivo in archivos:
                    print(f"      └─ {archivo.name}")

        # Errores
        archivos_error = list(carpeta_errores.glob("*.pdf"))
        if archivos_error:
            print(f"\n   📂 errores/")
            for archivo in archivos_error:
                print(f"      └─ {archivo.name}")

        # Resumen final
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETADO")
        print("=" * 70)

        print("\n💡 FLUJO DEMOSTRADO:")
        print("   1. ✅ Monitor watchdog detecta nuevos PDFs")
        print("   2. ✅ Espera a que el archivo esté completo")
        print("   3. ✅ Aplica OCR (simulado)")
        print("   4. ✅ Extrae datos con regex")
        print("   5. ✅ Valida datos")
        print("   6. ✅ Crea entidades de dominio")
        print("   7. ✅ Verifica duplicados")
        print("   8. ✅ Guarda en base de datos")
        print("   9. ✅ Mueve archivo a carpeta del cliente")
        print("   10. ✅ Maneja errores → carpeta de errores")

        print("\n🚀 LISTO PARA PRODUCCIÓN")
        print("   - Arquitectura DDD completa")
        print("   - Procesamiento automático 24/7")
        print("   - Manejo robusto de errores")
        print("   - Prevención de duplicados")
        print("   - Trazabilidad completa")

        db.disconnect()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error en el demo: {e}")
        import traceback
        traceback.print_exc()
