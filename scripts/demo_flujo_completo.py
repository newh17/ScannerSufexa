"""
Demo del flujo completo de procesamiento (simulado).

Muestra cómo se integran todos los componentes:
- PDF → Imagen (simulado)
- Imagen → OCR → Texto (simulado)
- Texto → Extracción de datos
- Datos → Validación
- Validación → Creación de entidades de dominio
- Entidades → Guardado en BD

Ejecutar desde la raíz del proyecto:
    python scripts/demo_flujo_completo.py
"""

import sys
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


def simular_ocr(archivo_pdf: str) -> str:
    """
    Simula el proceso de OCR sobre un PDF.

    En producción, esto haría:
    1. PDF → Imagen (PDFProcessor)
    2. Imagen → OCR (TesseractOCRService)

    Args:
        archivo_pdf: Ruta al PDF (no usado en simulación)

    Returns:
        str: Texto simulado como si viniera del OCR
    """
    # En este demo, cargamos texto de prueba
    ruta_fixture = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_text_ocr.txt"
    with open(ruta_fixture, 'r', encoding='utf-8') as f:
        return f.read()


def procesar_albaran_completo(
    pdf_path: str,
    albaran_repo: SQLiteAlbaranRepository,
    cliente_repo: SQLiteClienteRepository,
    extractor: ExtractorDatosService
) -> bool:
    """
    Procesa un albarán completo desde PDF hasta BD.

    Args:
        pdf_path: Ruta al PDF
        albaran_repo: Repositorio de albaranes
        cliente_repo: Repositorio de clientes
        extractor: Servicio de extracción

    Returns:
        bool: True si se procesó correctamente
    """
    print(f"\n{'='*70}")
    print(f"📄 PROCESANDO: {pdf_path}")
    print(f"{'='*70}")

    try:
        # PASO 1: OCR
        print("\n[1/6] 🔍 Aplicando OCR al PDF...")
        texto_ocr = simular_ocr(pdf_path)
        print(f"      ✅ Texto extraído: {len(texto_ocr)} caracteres")

        # PASO 2: Extracción de datos
        print("\n[2/6] 📊 Extrayendo datos del texto OCR...")
        datos = extractor.extraer_datos(texto_ocr)
        print(f"      ✅ Cliente: {datos.cliente}")
        print(f"      ✅ Fecha:   {datos.fecha}")
        print(f"      ✅ Número:  {datos.numero}")
        print(f"      ✅ Confianza: {datos.confianza:.1f}%")

        # PASO 3: Validación
        print("\n[3/6] ✔️  Validando datos extraídos...")
        es_valido, errores = extractor.validar_datos(datos)

        if not es_valido:
            print(f"      ❌ Datos inválidos:")
            for error in errores:
                print(f"         - {error}")
            return False

        print(f"      ✅ Datos válidos")

        # PASO 4: Crear entidades de dominio
        print("\n[4/6] 🏗️  Creando entidades de dominio...")

        try:
            fecha_vo = FechaAlbaran(datos.fecha)
            numero_vo = NumeroAlbaran(datos.numero)
            cliente_entidad = Cliente(nombre=datos.cliente)

            print(f"      ✅ Value Objects creados")
            print(f"      ✅ Cliente creado: {cliente_entidad}")

        except (DatosInvalidosException, Exception) as e:
            print(f"      ❌ Error al crear entidades: {e}")
            return False

        # PASO 5: Verificar duplicados y guardar
        print("\n[5/6] 💾 Guardando en base de datos...")

        try:
            # Verificar si ya existe
            if albaran_repo.exists(numero_vo, fecha_vo):
                print(f"      ⚠️  Albarán duplicado (#{numero_vo} del {fecha_vo})")
                return False

            # Crear albarán
            albaran = Albaran(
                cliente=cliente_entidad,
                fecha=fecha_vo,
                numero=numero_vo,
                ruta_archivo_original=pdf_path,
            )

            # Guardar cliente (o actualizar si existe)
            cliente_guardado = cliente_repo.save(cliente_entidad)
            cliente_guardado.incrementar_contador(fecha_vo.to_datetime())
            cliente_repo.save(cliente_guardado)

            # Guardar albarán
            albaran_guardado = albaran_repo.save(albaran)

            print(f"      ✅ Cliente guardado (ID: {cliente_guardado.id})")
            print(f"      ✅ Albarán guardado (ID: {albaran_guardado.id})")

        except AlbaranDuplicadoException as e:
            print(f"      ⚠️  {e}")
            return False
        except Exception as e:
            print(f"      ❌ Error al guardar: {e}")
            return False

        # PASO 6: Generar nombre y simular movimiento
        print("\n[6/6] 📁 Generando nombre de archivo...")

        nombre_archivo = albaran.generar_nombre_archivo()
        carpeta_destino = albaran.get_carpeta_destino()

        print(f"      ✅ Nombre: {nombre_archivo}")
        print(f"      ✅ Carpeta: C:\\albaranes\\{carpeta_destino}\\")

        # En producción, aquí se movería el archivo
        # FileSystemService.mover_archivo(pdf_path, ruta_destino)

        print(f"\n{'='*70}")
        print(f"✅ ALBARÁN PROCESADO EXITOSAMENTE")
        print(f"{'='*70}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal del demo."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║               DEMO: FLUJO COMPLETO DE PROCESAMIENTO                ║")
    print("║                    Scanner Sufexa - DDD + OCR                      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    # Crear BD en memoria
    print("\n🔧 Inicializando sistema...")
    db = Database(":memory:")
    db.connect()
    db.initialize_schema()
    print("   ✅ Base de datos inicializada")

    # Crear repositorios
    albaran_repo = SQLiteAlbaranRepository(db)
    cliente_repo = SQLiteClienteRepository(db)
    print("   ✅ Repositorios creados")

    # Crear servicios
    extractor = ExtractorDatosService()
    print("   ✅ Servicios de extracción listos")

    # Procesar varios albaranes
    pdfs_a_procesar = [
        "C:\\scan\\entrada\\albaran_001.pdf",
        "C:\\scan\\entrada\\albaran_002.pdf",
        "C:\\scan\\entrada\\albaran_001.pdf",  # Duplicado (debería fallar)
    ]

    resultados = []

    for pdf_path in pdfs_a_procesar:
        exito = procesar_albaran_completo(
            pdf_path,
            albaran_repo,
            cliente_repo,
            extractor
        )
        resultados.append((pdf_path, exito))

    # Mostrar resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DEL PROCESAMIENTO")
    print("="*70)

    for pdf, exito in resultados:
        estado = "✅ ÉXITO" if exito else "❌ FALLO"
        nombre_corto = Path(pdf).name
        print(f"{estado} - {nombre_corto}")

    # Estadísticas
    print("\n" + "="*70)
    print("📈 ESTADÍSTICAS DE LA BASE DE DATOS")
    print("="*70)

    total_albaranes = albaran_repo.count()
    total_clientes = cliente_repo.count()

    print(f"Total de albaranes procesados: {total_albaranes}")
    print(f"Total de clientes únicos: {total_clientes}")

    # Ranking
    print("\n🏆 RANKING DE CLIENTES:")
    print("-"*70)
    ranking = cliente_repo.get_ranking(top_n=5)
    for i, cliente in enumerate(ranking, 1):
        print(f"   {i}. {cliente.nombre:35} - {cliente.total_albaranes} albarán(es)")

    # Listado de albaranes
    print("\n📋 ALBARANES PROCESADOS:")
    print("-"*70)
    albaranes = albaran_repo.get_all()
    for albaran in albaranes:
        nombre_archivo = albaran.generar_nombre_archivo()
        print(f"   • {nombre_archivo}")

    print("\n" + "="*70)
    print("✅ DEMO COMPLETADO")
    print("="*70)

    print("\n💡 NOTA:")
    print("   Este demo simula el proceso completo sin necesitar:")
    print("   - Tesseract instalado")
    print("   - PDFs reales")
    print("   - Archivos en disco")
    print("\n   En producción, el flujo sería idéntico pero con:")
    print("   - PDFProcessor para convertir PDF → imagen")
    print("   - TesseractOCRService para OCR real")
    print("   - FileSystemService para mover archivos")
    print("   - WatchdogFileMonitor para detección automática")

    db.disconnect()


if __name__ == "__main__":
    main()
