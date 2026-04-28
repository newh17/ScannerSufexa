"""
Script maestro para generar ejecutable autocontenido completo.

Este script automatiza TODO el proceso:
1. Prepara Tesseract portable
2. Genera ejecutable con PyInstaller
3. Comprime en ZIP para distribución

Uso:
    python scripts/generar_todo_autocontenido.py

Resultado:
    dist/ScannerSufexa_v1.0.zip (listo para distribuir)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


class GeneradorAutocontenido:
    """
    Generador maestro de ejecutable autocontenido.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tesseract_portable = self.project_root / "tesseract-portable"
        self.dist_dir = self.project_root / "dist"
        self.exe_dir = self.dist_dir / "ScannerSufexa"

    def print_banner(self):
        """Muestra banner principal."""
        print("\n" + "=" * 70)
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║      GENERADOR DE EJECUTABLE AUTOCONTENIDO - TODO EN UNO        ║")
        print("║                   SCANNER SUFEXA v1.0                            ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("=" * 70 + "\n")

    def verificar_tesseract_instalado(self):
        """Verifica que Tesseract esté instalado en el sistema."""
        print("🔍 PASO 1/5: Verificando Tesseract en el sistema...\n")

        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR",
            r"C:\Program Files (x86)\Tesseract-OCR",
        ]

        tesseract_encontrado = None
        for path in tesseract_paths:
            tesseract_exe = Path(path) / "tesseract.exe"
            if tesseract_exe.exists():
                tesseract_encontrado = Path(path)
                break

        if tesseract_encontrado:
            print(f"   ✅ Tesseract encontrado en: {tesseract_encontrado}")
            return tesseract_encontrado
        else:
            print("   ❌ Tesseract NO encontrado en el sistema")
            print("\n⚠️  SOLUCIÓN:")
            print("   1. Descarga: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   2. Instala en: C:\\Program Files\\Tesseract-OCR")
            print("   3. Ejecuta este script nuevamente")
            return None

    def preparar_tesseract_portable(self, tesseract_path):
        """Prepara Tesseract portable copiando desde instalación."""
        print("\n🔨 PASO 2/5: Preparando Tesseract portable...\n")

        # Limpiar directorio anterior si existe
        if self.tesseract_portable.exists():
            print(f"   🗑️  Limpiando instalación anterior...")
            shutil.rmtree(self.tesseract_portable)

        # Copiar Tesseract
        print(f"   📦 Copiando Tesseract desde: {tesseract_path}")
        print(f"   📍 Destino: {self.tesseract_portable}")
        print(f"   ⏳ Esto puede tardar un momento...\n")

        try:
            shutil.copytree(tesseract_path, self.tesseract_portable)
            print(f"   ✅ Tesseract portable preparado exitosamente")

            # Verificar archivos críticos
            archivos_criticos = [
                self.tesseract_portable / "tesseract.exe",
                self.tesseract_portable / "tessdata" / "spa.traineddata",
            ]

            todos_ok = True
            for archivo in archivos_criticos:
                if archivo.exists():
                    print(f"   ✅ {archivo.name} verificado")
                else:
                    print(f"   ❌ {archivo.name} NO encontrado")
                    todos_ok = False

            if not todos_ok:
                print("\n   ⚠️  Advertencia: Algunos archivos críticos no están presentes")
                return False

            # Calcular tamaño
            total_size = sum(
                f.stat().st_size
                for f in self.tesseract_portable.rglob('*')
                if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            print(f"\n   📊 Tamaño de Tesseract portable: {size_mb:.2f} MB")

            return True

        except Exception as e:
            print(f"\n   ❌ Error al copiar Tesseract: {e}")
            return False

    def verificar_dependencias_python(self):
        """Verifica que las dependencias de Python estén instaladas."""
        print("\n🔍 PASO 3/5: Verificando dependencias Python...\n")

        dependencias_criticas = {
            'PyInstaller': 'pyinstaller',
            'PySide6': 'PySide6',
            'watchdog': 'watchdog',
            'pytesseract': 'pytesseract',
            'PIL': 'Pillow',
        }

        faltantes = []
        for nombre, paquete in dependencias_criticas.items():
            try:
                if nombre == 'PIL':
                    __import__('PIL')
                else:
                    __import__(nombre)
                print(f"   ✅ {nombre} instalado")
            except ImportError:
                faltantes.append(paquete)
                print(f"   ❌ {nombre} NO instalado")

        if faltantes:
            print(f"\n   ⚠️  Faltan dependencias: {', '.join(faltantes)}")
            print("\n   Para instalar:")
            print(f"   pip install {' '.join(faltantes)}")
            return False

        return True

    def generar_ejecutable(self):
        """Ejecuta el script de build."""
        print("\n🔨 PASO 4/5: Generando ejecutable con PyInstaller...\n")
        print("   ⏳ Esto puede tardar 5-10 minutos, por favor espera...\n")

        build_script = self.project_root / "scripts" / "build_exe.py"

        try:
            # Ejecutar build_exe.py
            result = subprocess.run(
                [sys.executable, str(build_script)],
                cwd=self.project_root,
                check=True,
                capture_output=False,  # Mostrar output en tiempo real
                text=True
            )

            print("\n   ✅ Ejecutable generado exitosamente")
            return True

        except subprocess.CalledProcessError as e:
            print(f"\n   ❌ Error al generar ejecutable: {e}")
            return False

    def comprimir_distribucion(self):
        """Comprime el ejecutable en ZIP para distribución."""
        print("\n📦 PASO 5/5: Comprimiendo para distribución...\n")

        if not self.exe_dir.exists():
            print(f"   ❌ Directorio del ejecutable no encontrado: {self.exe_dir}")
            return None

        # Nombre del ZIP con fecha
        fecha = datetime.now().strftime("%Y-%m-%d")
        zip_name = f"ScannerSufexa_v1.0_{fecha}.zip"
        zip_path = self.dist_dir / zip_name

        # Eliminar ZIP anterior si existe
        if zip_path.exists():
            zip_path.unlink()

        print(f"   📦 Creando: {zip_name}")
        print(f"   ⏳ Comprimiendo...\n")

        try:
            # Usar shutil para crear ZIP
            shutil.make_archive(
                str(zip_path.with_suffix('')),
                'zip',
                self.exe_dir.parent,
                self.exe_dir.name
            )

            if zip_path.exists():
                size_mb = zip_path.stat().st_size / (1024 * 1024)
                print(f"   ✅ ZIP creado exitosamente")
                print(f"   📊 Tamaño: {size_mb:.2f} MB")
                print(f"   📍 Ubicación: {zip_path}")
                return zip_path
            else:
                print(f"   ❌ Error: ZIP no fue creado")
                return None

        except Exception as e:
            print(f"   ❌ Error al comprimir: {e}")
            return None

    def mostrar_resumen_final(self, zip_path):
        """Muestra resumen final del proceso."""
        print("\n" + "=" * 70)
        print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("=" * 70)

        if zip_path:
            print(f"\n📦 ARCHIVO PARA DISTRIBUCIÓN:")
            print(f"   {zip_path}")

            size_mb = zip_path.stat().st_size / (1024 * 1024)
            print(f"\n📊 Tamaño final: {size_mb:.2f} MB")

        print(f"\n✅ CARACTERÍSTICAS DEL EJECUTABLE:")
        print(f"   • Autocontenido (incluye Tesseract OCR)")
        print(f"   • No requiere Python")
        print(f"   • No requiere instalación de Tesseract")
        print(f"   • Listo para usar")

        print(f"\n📋 INSTRUCCIONES PARA EL USUARIO FINAL:")
        print(f"   1. Extraer el ZIP")
        print(f"   2. Editar config\\config.json (rutas de carpetas)")
        print(f"   3. Ejecutar Iniciar_ScannerSufexa.bat")

        print(f"\n💡 RECOMENDACIÓN:")
        print(f"   Prueba el ejecutable en una máquina virtual Windows limpia")
        print(f"   para verificar que funcione sin dependencias.")

        print("\n" + "=" * 70 + "\n")

    def ejecutar(self):
        """Ejecuta el proceso completo."""
        self.print_banner()

        # PASO 1: Verificar Tesseract instalado
        tesseract_path = self.verificar_tesseract_instalado()
        if not tesseract_path:
            print("\n❌ PROCESO ABORTADO: Tesseract no encontrado")
            return 1

        # PASO 2: Preparar Tesseract portable
        if not self.preparar_tesseract_portable(tesseract_path):
            print("\n❌ PROCESO ABORTADO: Error al preparar Tesseract portable")
            return 1

        # PASO 3: Verificar dependencias Python
        if not self.verificar_dependencias_python():
            print("\n❌ PROCESO ABORTADO: Faltan dependencias Python")
            return 1

        # PASO 4: Generar ejecutable
        if not self.generar_ejecutable():
            print("\n❌ PROCESO ABORTADO: Error al generar ejecutable")
            return 1

        # PASO 5: Comprimir
        zip_path = self.comprimir_distribucion()

        # Resumen final
        self.mostrar_resumen_final(zip_path)

        return 0


def main():
    """Función principal."""
    generador = GeneradorAutocontenido()
    return generador.ejecutar()


if __name__ == "__main__":
    sys.exit(main())
