"""
Script para descargar y preparar Tesseract OCR portable para empaquetar.

Este script descarga Tesseract portable y lo prepara para incluirlo
en el ejecutable, haciendo que la aplicación sea completamente autocontenida.

Uso:
    python scripts/preparar_tesseract_portable.py

El script creará: tesseract-portable/
"""

import os
import sys
import zipfile
import urllib.request
from pathlib import Path
import shutil


class TesseractPortablePreparator:
    """
    Prepara Tesseract OCR portable para empaquetado.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tesseract_dir = self.project_root / "tesseract-portable"

        # URLs para Tesseract portable (versión sin instalador)
        # Usaremos UB Mannheim portable build
        self.tesseract_version = "5.5.0.20241111"
        self.tesseract_base_url = "https://digi.bib.uni-mannheim.de/tesseract"

    def limpiar_directorio(self):
        """Limpia instalación anterior si existe."""
        if self.tesseract_dir.exists():
            print(f"🗑️  Limpiando directorio anterior: {self.tesseract_dir}")
            shutil.rmtree(self.tesseract_dir)

        self.tesseract_dir.mkdir(exist_ok=True)
        print(f"✅ Directorio creado: {self.tesseract_dir}")

    def descargar_tesseract_portable(self):
        """
        Descarga Tesseract portable desde fuente confiable.

        NOTA: Como no hay un portable oficial simple, este script
        proporciona instrucciones para preparar manualmente.
        """
        print("\n" + "=" * 70)
        print("📦 PREPARACIÓN MANUAL DE TESSERACT PORTABLE")
        print("=" * 70)

        print("""
⚠️  INSTRUCCIONES MANUALES:

Debido a que Tesseract no tiene una versión portable oficial lista,
necesitas preparar los archivos manualmente:

OPCIÓN 1 - Desde instalación existente (RECOMENDADO):
---------------------------------------------------
1. Instala Tesseract normalmente desde:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Copia TODA la carpeta de instalación:
   C:\\Program Files\\Tesseract-OCR\\

   A esta ubicación:
   {tesseract_dir}

3. La estructura final debe ser:
   {tesseract_dir}/
   ├── tesseract.exe
   ├── tessdata/
   │   ├── spa.traineddata
   │   └── [otros archivos de idioma]
   └── [DLLs y otros archivos]


OPCIÓN 2 - Descarga manual portable:
-----------------------------------
1. Descarga desde: https://github.com/UB-Mannheim/tesseract/wiki

2. Extrae los archivos necesarios a:
   {tesseract_dir}

3. Asegúrate de incluir:
   - tesseract.exe
   - tessdata/ (carpeta con idiomas)
   - Todas las DLLs necesarias


ARCHIVOS MÍNIMOS REQUERIDOS:
----------------------------
✅ tesseract.exe
✅ tessdata/spa.traineddata (español)
✅ tessdata/spa.traineddata (inglés, útil como fallback)
✅ Todas las DLLs en la carpeta (leptonica, etc.)


VERIFICACIÓN:
------------
Después de copiar, ejecuta este script nuevamente para verificar.
""".format(tesseract_dir=self.tesseract_dir))

    def verificar_instalacion(self):
        """Verifica que Tesseract portable esté correctamente preparado."""
        print("\n🔍 Verificando instalación de Tesseract portable...\n")

        errores = []
        advertencias = []

        # Verificar tesseract.exe
        tesseract_exe = self.tesseract_dir / "tesseract.exe"
        if tesseract_exe.exists():
            print(f"✅ tesseract.exe encontrado")
        else:
            errores.append(f"❌ tesseract.exe NO encontrado en {tesseract_exe}")

        # Verificar carpeta tessdata
        tessdata_dir = self.tesseract_dir / "tessdata"
        if tessdata_dir.exists():
            print(f"✅ Carpeta tessdata/ encontrada")

            # Verificar idioma español
            spa_file = tessdata_dir / "spa.traineddata"
            if spa_file.exists():
                print(f"✅ Idioma español (spa.traineddata) encontrado")
            else:
                errores.append(f"❌ spa.traineddata NO encontrado")

            # Verificar inglés (útil como fallback)
            eng_file = tessdata_dir / "eng.traineddata"
            if eng_file.exists():
                print(f"✅ Idioma inglés (eng.traineddata) encontrado")
            else:
                advertencias.append(f"⚠️  eng.traineddata no encontrado (opcional pero recomendado)")

        else:
            errores.append(f"❌ Carpeta tessdata/ NO encontrada")

        # Verificar DLLs comunes
        dlls_comunes = [
            "leptonica-1.84.1.dll",
            "libgif-7.dll",
            "libjpeg-62.dll",
            "libpng16-16.dll",
            "libtiff-6.dll",
            "libwebp-7.dll",
            "zlib1.dll",
        ]

        dlls_encontradas = 0
        for dll in dlls_comunes:
            if (self.tesseract_dir / dll).exists():
                dlls_encontradas += 1

        if dlls_encontradas >= 4:
            print(f"✅ DLLs encontradas ({dlls_encontradas}/{len(dlls_comunes)})")
        else:
            advertencias.append(
                f"⚠️  Solo {dlls_encontradas}/{len(dlls_comunes)} DLLs encontradas. "
                "Puede que falten dependencias."
            )

        # Calcular tamaño total
        try:
            total_size = sum(
                f.stat().st_size
                for f in self.tesseract_dir.rglob('*')
                if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            print(f"\n📊 Tamaño total: {size_mb:.2f} MB")
        except:
            pass

        # Mostrar resumen
        print("\n" + "=" * 70)
        if errores:
            print("❌ VERIFICACIÓN FALLIDA\n")
            for error in errores:
                print(error)
            if advertencias:
                print()
                for adv in advertencias:
                    print(adv)
            print("\n⚠️  Sigue las instrucciones anteriores para preparar Tesseract")
            return False
        else:
            print("✅ VERIFICACIÓN EXITOSA")
            if advertencias:
                print()
                for adv in advertencias:
                    print(adv)
            print("\n🎉 Tesseract portable está listo para empaquetarse")
            print(f"📁 Ubicación: {self.tesseract_dir}")
            print("\nPuedes ejecutar ahora:")
            print("  python scripts/build_exe.py")
            return True

    def preparar(self):
        """Ejecuta el proceso completo de preparación."""
        print("\n╔════════════════════════════════════════════════════════════════════╗")
        print("║         PREPARACIÓN DE TESSERACT PORTABLE PARA EMPAQUETADO        ║")
        print("╚════════════════════════════════════════════════════════════════════╝")

        # Si el directorio no existe, crear y mostrar instrucciones
        if not self.tesseract_dir.exists():
            self.limpiar_directorio()
            self.descargar_tesseract_portable()
            return 1

        # Si existe, verificar
        if self.verificar_instalacion():
            return 0
        else:
            return 1


def main():
    """Función principal."""
    preparador = TesseractPortablePreparator()
    return preparador.preparar()


if __name__ == "__main__":
    sys.exit(main())
