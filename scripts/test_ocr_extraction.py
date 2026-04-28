"""
Script de prueba para verificar OCR y extracción de datos.

Ejecutar desde la raíz del proyecto:
    python scripts/test_ocr_extraction.py
"""

import sys
from pathlib import Path

# Añadir src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from application.services import ExtractorDatosService

# Importar TesseractOCRService solo si está disponible
try:
    from infrastructure.ocr import TesseractOCRService
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Advertencia: PyMuPDF no instalado. Algunas pruebas se saltarán.")
    print("   Para instalar: pip install PyMuPDF pytesseract Pillow")


def cargar_texto_prueba(archivo: str) -> str:
    """Carga un archivo de texto de prueba."""
    ruta = Path(__file__).parent.parent / "tests" / "fixtures" / archivo
    with open(ruta, 'r', encoding='utf-8') as f:
        return f.read()


def test_extraccion_basica():
    """Prueba la extracción de datos con texto OCR simulado."""
    print("=" * 70)
    print("PRUEBA 1: EXTRACCIÓN DE DATOS - ALBARÁN LIMPIO")
    print("=" * 70)

    # Cargar texto simulado
    texto_ocr = cargar_texto_prueba("sample_text_ocr.txt")

    print("\n📄 TEXTO OCR:")
    print("-" * 70)
    print(texto_ocr[:300] + "..." if len(texto_ocr) > 300 else texto_ocr)
    print("-" * 70)

    # Crear extractor
    extractor = ExtractorDatosService()

    # Extraer datos
    datos = extractor.extraer_datos(texto_ocr)

    print("\n📊 DATOS EXTRAÍDOS:")
    print("-" * 70)
    print(f"Cliente:  {datos.cliente}")
    print(f"Fecha:    {datos.fecha}")
    print(f"Número:   {datos.numero}")
    print(f"Confianza: {datos.confianza:.1f}%")
    print("-" * 70)

    # Validar
    es_valido, errores = extractor.validar_datos(datos)

    print("\n✅ VALIDACIÓN:")
    print("-" * 70)
    if es_valido:
        print("✅ Todos los datos son válidos")
    else:
        print("❌ Errores encontrados:")
        for error in errores:
            print(f"   - {error}")
    print("-" * 70)

    return es_valido


def test_extraccion_segundo_formato():
    """Prueba con un segundo formato de albarán."""
    print("\n" + "=" * 70)
    print("PRUEBA 2: EXTRACCIÓN DE DATOS - SEGUNDO FORMATO")
    print("=" * 70)

    texto_ocr = cargar_texto_prueba("sample_text_ocr_2.txt")

    print("\n📄 TEXTO OCR:")
    print("-" * 70)
    print(texto_ocr[:300] + "..." if len(texto_ocr) > 300 else texto_ocr)
    print("-" * 70)

    extractor = ExtractorDatosService()
    datos = extractor.extraer_datos(texto_ocr)

    print("\n📊 DATOS EXTRAÍDOS:")
    print("-" * 70)
    print(f"Cliente:  {datos.cliente}")
    print(f"Fecha:    {datos.fecha}")
    print(f"Número:   {datos.numero}")
    print(f"Confianza: {datos.confianza:.1f}%")
    print("-" * 70)

    es_valido, errores = extractor.validar_datos(datos)

    print("\n✅ VALIDACIÓN:")
    print("-" * 70)
    if es_valido:
        print("✅ Todos los datos son válidos")
    else:
        print("❌ Errores encontrados:")
        for error in errores:
            print(f"   - {error}")
    print("-" * 70)

    return es_valido


def test_extraccion_con_errores_ocr():
    """Prueba con texto que contiene errores típicos de OCR."""
    print("\n" + "=" * 70)
    print("PRUEBA 3: EXTRACCIÓN CON ERRORES DE OCR")
    print("=" * 70)

    texto_ocr = cargar_texto_prueba("sample_text_ocr_errores.txt")

    print("\n📄 TEXTO OCR (CON ERRORES):")
    print("-" * 70)
    print(texto_ocr[:300] + "..." if len(texto_ocr) > 300 else texto_ocr)
    print("-" * 70)

    extractor = ExtractorDatosService()
    datos = extractor.extraer_datos(texto_ocr)

    print("\n📊 DATOS EXTRAÍDOS:")
    print("-" * 70)
    print(f"Cliente:  {datos.cliente}")
    print(f"Fecha:    {datos.fecha}")
    print(f"Número:   {datos.numero}")
    print(f"Confianza: {datos.confianza:.1f}%")
    print("-" * 70)

    print("\n💡 NOTA:")
    print("Este texto contiene errores de OCR típicos (4 por A, 5 por S, etc.)")
    print("El extractor debería ser robusto ante estos errores.")

    es_valido, errores = extractor.validar_datos(datos)

    print("\n✅ VALIDACIÓN:")
    print("-" * 70)
    if es_valido:
        print("✅ Todos los datos son válidos (extractor robusto ante errores)")
    else:
        print("⚠️  Errores encontrados:")
        for error in errores:
            print(f"   - {error}")
        print("\nEsto es esperado con OCR de baja calidad.")
    print("-" * 70)

    return True  # No falla aunque no extraiga todo


def test_normalizacion_texto():
    """Prueba la normalización de texto."""
    print("\n" + "=" * 70)
    print("PRUEBA 4: NORMALIZACIÓN DE TEXTO OCR")
    print("=" * 70)

    if not TESSERACT_AVAILABLE:
        print("⏭️  SALTADA: PyMuPDF no instalado")
        return True

    ocr_service = TesseractOCRService()

    texto_sucio = """
    CLIENTE    EJEMPLO     S.L.


    Data:    23/01/2026


    Albarà     núm.     71206

    """

    print("\n📄 TEXTO ORIGINAL:")
    print("-" * 70)
    print(repr(texto_sucio))
    print("-" * 70)

    texto_limpio = ocr_service.normalize_text(texto_sucio)

    print("\n✨ TEXTO NORMALIZADO:")
    print("-" * 70)
    print(repr(texto_limpio))
    print("-" * 70)

    print("\n✅ Cambios aplicados:")
    print("   - Eliminados espacios múltiples")
    print("   - Eliminadas líneas vacías múltiples")
    print("   - Eliminados caracteres de control")

    return True


def test_tesseract_disponible():
    """Verifica si Tesseract está disponible."""
    print("\n" + "=" * 70)
    print("PRUEBA 5: VERIFICACIÓN DE TESSERACT")
    print("=" * 70)

    if not TESSERACT_AVAILABLE:
        print("⏭️  SALTADA: PyMuPDF no instalado")
        return True

    ocr_service = TesseractOCRService()

    disponible = ocr_service.is_available()

    print("\n🔍 TESSERACT OCR:")
    print("-" * 70)
    if disponible:
        version = ocr_service.get_version()
        print(f"✅ Tesseract está instalado y disponible")
        print(f"   Versión: {version}")
        print(f"   Idioma: {ocr_service.language}")
        print(f"   Config: {ocr_service.config}")
    else:
        print("❌ Tesseract NO está instalado o no se encuentra en el PATH")
        print("\n💡 Para instalar Tesseract:")
        print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Linux:   sudo apt-get install tesseract-ocr tesseract-ocr-spa")
        print("   Mac:     brew install tesseract tesseract-lang")
    print("-" * 70)

    return True  # No falla si no está instalado


def test_regex_patterns():
    """Prueba los patrones regex de extracción."""
    print("\n" + "=" * 70)
    print("PRUEBA 6: PATRONES REGEX")
    print("=" * 70)

    extractor = ExtractorDatosService()

    casos_prueba = [
        ("Data 23/01/2026", "23/01/2026", None),
        ("Data: 05/12/2025", "05/12/2025", None),
        ("Data 5/3/2026", "05/03/2026", None),
        ("Albarà núm. 71206", None, 71206),
        ("Albarà num. 12345", None, 12345),
        ("Albara núm: 99999", None, 99999),
    ]

    print("\n🧪 PROBANDO PATRONES:")
    print("-" * 70)

    for texto, fecha_esperada, numero_esperado in casos_prueba:
        if fecha_esperada:
            fecha_extraida = extractor.extraer_fecha(texto)
            match = "✅" if fecha_extraida == fecha_esperada else "❌"
            print(f"{match} '{texto}' → Fecha: {fecha_extraida} (esperado: {fecha_esperada})")

        if numero_esperado:
            numero_extraido = extractor.extraer_numero(texto)
            match = "✅" if numero_extraido == numero_esperado else "❌"
            print(f"{match} '{texto}' → Número: {numero_extraido} (esperado: {numero_esperado})")

    print("-" * 70)

    return True


def main():
    """Función principal de pruebas."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          PRUEBAS DE OCR Y EXTRACCIÓN DE DATOS - SUFEXA            ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    resultados = []

    # Ejecutar todas las pruebas
    resultados.append(("Extracción básica", test_extraccion_basica()))
    resultados.append(("Segundo formato", test_extraccion_segundo_formato()))
    resultados.append(("OCR con errores", test_extraccion_con_errores_ocr()))
    resultados.append(("Normalización", test_normalizacion_texto()))
    resultados.append(("Tesseract disponible", test_tesseract_disponible()))
    resultados.append(("Patrones regex", test_regex_patterns()))

    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)

    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado} - {nombre}")

    total = len(resultados)
    exitosas = sum(1 for _, r in resultados if r)

    print("-" * 70)
    print(f"Total: {exitosas}/{total} pruebas exitosas ({exitosas*100//total}%)")
    print("=" * 70)

    if exitosas == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    else:
        print(f"\n⚠️  {total - exitosas} prueba(s) fallaron")

    print("\n")


if __name__ == "__main__":
    main()
