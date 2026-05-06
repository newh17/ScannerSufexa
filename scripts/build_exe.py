"""
Script para generar ejecutable de Windows con PyInstaller.

Este script automatiza la creación del .exe incluyendo:
- Todas las dependencias Python
- Archivos de configuración
- Base de datos inicial
- Recursos de la interfaz

Uso:
    python scripts/build_exe.py

El ejecutable se generará en dist/ScannerSufexa/
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class BuildExecutable:
    """
    Constructor del ejecutable.

    Gestiona todo el proceso de build con PyInstaller.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.spec_file = self.project_root / "scanner_sufexa.spec"
        self.tesseract_portable_dir = self.project_root / "tesseract-portable"

    def verificar_tesseract_portable(self):
        """Verifica que Tesseract portable esté preparado."""
        print("\n🔍 Verificando Tesseract portable...")

        if not self.tesseract_portable_dir.exists():
            print(f"   ❌ Tesseract portable NO encontrado en: {self.tesseract_portable_dir}")
            print("\n📋 Para preparar Tesseract portable:")
            print("   python scripts/preparar_tesseract_portable.py")
            print("\n⚠️  Sin Tesseract, el ejecutable NO será autocontenido")
            print("   Los usuarios tendrán que instalar Tesseract por separado")
            return False

        # Verificar archivos críticos
        tesseract_exe = self.tesseract_portable_dir / "tesseract.exe"
        tessdata_dir = self.tesseract_portable_dir / "tessdata"
        spa_data = tessdata_dir / "spa.traineddata"

        if tesseract_exe.exists() and tessdata_dir.exists() and spa_data.exists():
            print(f"   ✅ Tesseract portable encontrado y verificado")

            # Calcular tamaño
            try:
                total_size = sum(
                    f.stat().st_size
                    for f in self.tesseract_portable_dir.rglob('*')
                    if f.is_file()
                )
                size_mb = total_size / (1024 * 1024)
                print(f"   📊 Tamaño: {size_mb:.2f} MB (se añadirá al ejecutable)")
            except:
                pass

            return True
        else:
            print(f"   ⚠️  Tesseract incompleto (falta tesseract.exe o archivos de idioma)")
            return False

    def verificar_dependencias(self):
        """Verifica que PyInstaller esté instalado."""
        print("🔍 Verificando dependencias Python...")

        try:
            import PyInstaller
            print(f"   ✅ PyInstaller {PyInstaller.__version__} instalado")
        except ImportError:
            print("   ❌ PyInstaller no está instalado")
            print("\n📦 Para instalar PyInstaller:")
            print("   pip install pyinstaller")
            sys.exit(1)

        # Verificar otras dependencias críticas
        dependencias = [
            'PySide6',
            'watchdog',
            'pytesseract',
            'PIL',
        ]

        faltantes = []
        for dep in dependencias:
            try:
                __import__(dep)
                print(f"   ✅ {dep} instalado")
            except ImportError:
                faltantes.append(dep)
                print(f"   ⚠️  {dep} no instalado (se incluirá si está en requirements.txt)")

        if faltantes:
            print(f"\n💡 Dependencias faltantes: {', '.join(faltantes)}")
            print("   El ejecutable las incluirá si están en requirements.txt")

    def limpiar_directorios(self):
        """Limpia directorios de builds anteriores."""
        print("\n🗑️  Limpiando directorios anteriores...")

        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print("   ✅ dist/ eliminado")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print("   ✅ build/ eliminado")

    def crear_spec_file(self):
        """Crea el archivo .spec de PyInstaller."""
        print("\n📝 Creando archivo de configuración (.spec)...")

        # Verificar si Tesseract portable existe
        incluir_tesseract = self.tesseract_portable_dir.exists()

        # Construir datas dinámicamente
        datas_list = [
            "('config/config.example.json', 'config'),",
        ]

        if incluir_tesseract:
            # Incluir TODA la carpeta de Tesseract portable
            datas_list.append(
                f"('{self.tesseract_portable_dir}', 'tesseract'),"
            )
            print(f"   ✅ Tesseract portable se incluirá en el ejecutable")
        else:
            print(f"   ⚠️  Tesseract NO se incluirá (ejecutable no será autocontenido)")

        datas_str = "\n        ".join(datas_list)

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Punto de entrada
a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        # Archivos de datos a incluir
        {datas_str}
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'pytesseract',
        'PIL',
        'PIL.Image',
        'sqlite3',
        'presentation',
        'presentation.ui',
        'presentation.ui.components',
        'presentation.controllers',
        'application',
        'application.use_cases',
        'application.services',
        'domain',
        'domain.entities',
        'domain.value_objects',
        'domain.repositories',
        'domain.exceptions',
        'infrastructure',
        'infrastructure.ocr',
        'infrastructure.filesystem',
        'infrastructure.persistence',
        'infrastructure.persistence.repositories',
        'infrastructure.persistence.models',
        'infrastructure.monitoring',
        'infrastructure.logging',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ScannerSufexa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # DEBUG: activado para ver errores de arranque
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='docs/icon.ico' if os.path.exists('docs/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScannerSufexa',
)
'''

        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)

        print(f"   ✅ Archivo {self.spec_file.name} creado")

    def ejecutar_pyinstaller(self):
        """Ejecuta PyInstaller con el archivo .spec."""
        print("\n🔨 Ejecutando PyInstaller...")
        print("   (Esto puede tardar varios minutos...)\n")

        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(self.spec_file)
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )

            print("   ✅ PyInstaller completado exitosamente")

            # Mostrar últimas líneas del output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                print("\n   📋 Últimas líneas del build:")
                for line in lines[-5:]:
                    print(f"      {line}")

        except subprocess.CalledProcessError as e:
            print(f"\n   ❌ Error al ejecutar PyInstaller:")
            print(e.stderr)
            sys.exit(1)

    def crear_estructura_adicional(self):
        """Crea estructura de carpetas adicionales en dist."""
        print("\n📁 Creando estructura de carpetas...")

        exe_dir = self.dist_dir / "ScannerSufexa"

        # Carpetas necesarias
        carpetas = [
            exe_dir / "data" / "database",
            exe_dir / "data" / "logs",
            exe_dir / "config",
        ]

        for carpeta in carpetas:
            carpeta.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {carpeta.relative_to(self.dist_dir)}")

        # Copiar config de ejemplo
        config_ejemplo = self.project_root / "config" / "config.example.json"
        if config_ejemplo.exists():
            shutil.copy(
                config_ejemplo,
                exe_dir / "config" / "config.json"
            )
            print(f"   ✅ config.json copiado")

    def crear_readme_distribucion(self, tesseract_incluido=False):
        """Crea README para la distribución."""
        print("\n📄 Creando README de distribución...")

        exe_dir = self.dist_dir / "ScannerSufexa"
        readme_path = exe_dir / "README.txt"

        if tesseract_incluido:
            instalacion_tesseract = """
1. ¡TODO INCLUIDO! ✅

   Este ejecutable es AUTOCONTENIDO y ya incluye Tesseract OCR.
   NO necesitas instalar nada adicional.

   Tesseract está embebido en la carpeta tesseract/ junto al ejecutable.

2. CONFIGURACIÓN INICIAL"""
        else:
            instalacion_tesseract = """
1. TESSERACT OCR (REQUERIDO) ⚠️

   Descarga e instala Tesseract OCR para Windows:
   https://github.com/UB-Mannheim/tesseract/wiki

   Instalación recomendada:
   - Ejecutar instalador tesseract-ocr-w64-setup-5.x.x.exe
   - Instalar en: C:\\Program Files\\Tesseract-OCR
   - Marcar "Add to PATH" durante instalación
   - Idioma: Instalar paquete de idioma español (spa.traineddata)

2. CONFIGURACIÓN INICIAL"""

        readme_content = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    SCANNER SUFEXA v1.0                           ║
║            Sistema de Procesamiento de Albaranes                 ║
║              {'🎉 EJECUTABLE AUTOCONTENIDO 🎉' if tesseract_incluido else '     REQUIERE TESSERACT OCR     '}           ║
╚══════════════════════════════════════════════════════════════════╝

INSTALACIÓN
===========

{instalacion_tesseract}

   Editar el archivo: config/config.json

   Configurar las siguientes rutas:
   - folders.scanner_input: Carpeta donde el scanner guarda los PDFs
   - folders.output_base: Carpeta donde se organizarán los albaranes
   - folders.errors: Carpeta para archivos con error
   - tesseract.path: Ruta al ejecutable de Tesseract

   Ejemplo:
   {{
     "folders": {{
       "scanner_input": "C:\\\\scan\\\\entrada",
       "output_base": "C:\\\\albaranes",
       "errors": "C:\\\\albaranes\\\\errores"
     }}{'' if tesseract_incluido else ''',
     "tesseract": {
       "path": "C:\\\\Program Files\\\\Tesseract-OCR\\\\tesseract.exe"
     }'''}
   }}

   {'NOTA: No necesitas configurar "tesseract.path" si usas el Tesseract incluido.' if tesseract_incluido else 'NOTA: Configura "tesseract.path" con la ruta donde instalaste Tesseract.'}

3. CREAR CARPETAS

   El sistema creará automáticamente las carpetas necesarias,
   pero puedes crearlas manualmente:

   - C:\\scan\\entrada
   - C:\\albaranes
   - C:\\albaranes\\errores

USO
===

1. Ejecutar: ScannerSufexa.exe

2. La interfaz mostrará:
   - Estado del sistema
   - Albaranes procesados
   - Ranking de clientes
   - Log de eventos

3. Configurar las rutas (menú Archivo > Configuración)

4. Iniciar el monitor (botón ▶ Iniciar)

5. El sistema procesará automáticamente los PDFs que aparezcan
   en la carpeta de entrada

ESTRUCTURA DE ARCHIVOS
=======================

ScannerSufexa/
├── ScannerSufexa.exe          Ejecutable principal
├── config/
│   └── config.json            Configuración
├── data/
│   ├── database/              Base de datos SQLite
│   └── logs/                  Archivos de log
└── README.txt                 Este archivo

SOLUCIÓN DE PROBLEMAS
======================

ERROR: "Tesseract no encontrado"
- Verifica que Tesseract esté instalado
- Verifica la ruta en config.json
- Añade Tesseract al PATH de Windows

ERROR: "No se puede crear la carpeta"
- Verifica permisos de escritura
- Ejecuta como Administrador si es necesario

ERROR: "Base de datos bloqueada"
- Cierra otras instancias de la aplicación
- Verifica que no haya archivos .db-lock

LOGS
====

Los logs se guardan en: data/logs/app.log

Para ver logs detallados:
1. Editar config.json
2. Cambiar logging.level a "DEBUG"
3. Reiniciar la aplicación

SOPORTE
=======

Para reportar problemas o solicitar ayuda:
- Revisa la documentación en docs/
- Incluye el archivo de log al reportar errores

© 2026 Scanner Sufexa
"""

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"   ✅ {readme_path.name} creado")

    def crear_batch_launcher(self):
        """Crea un archivo .bat para lanzar la aplicación."""
        print("\n📝 Creando launcher batch...")

        exe_dir = self.dist_dir / "ScannerSufexa"
        bat_path = exe_dir / "Iniciar_ScannerSufexa.bat"

        # Verificar si Tesseract está incluido
        tesseract_incluido = (exe_dir / "tesseract" / "tesseract.exe").exists()

        if tesseract_incluido:
            verificacion_tesseract = """REM Tesseract incluido en la aplicación
if exist "%~dp0tesseract\\tesseract.exe" (
    echo ✅ Tesseract OCR: Incluido
) else (
    echo ⚠️  ADVERTENCIA: Tesseract embebido no encontrado
    echo    La aplicación intentará usar Tesseract del sistema
    echo.
)"""
        else:
            verificacion_tesseract = """REM Verificar que Tesseract existe en el sistema
if exist "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" (
    echo ✅ Tesseract OCR: Encontrado en el sistema
) else (
    echo ⚠️  ADVERTENCIA: Tesseract no encontrado
    echo    Instala Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    pause
)"""

        bat_content = f"""@echo off
title Scanner Sufexa v1.0
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    SCANNER SUFEXA v1.0                           ║
echo ║              {'EJECUTABLE AUTOCONTENIDO' if tesseract_incluido else '  REQUIERE TESSERACT OCR  '}                      ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo Iniciando aplicación...
echo.

{verificacion_tesseract}

echo.
REM Lanzar aplicación
start "" "%~dp0ScannerSufexa.exe"

echo ✅ Aplicación iniciada
echo.
echo Puedes cerrar esta ventana
timeout /t 3 >nul
"""

        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)

        print(f"   ✅ {bat_path.name} creado")

    def mostrar_resumen(self, tesseract_incluido=False):
        """Muestra resumen del build."""
        print("\n" + "=" * 70)
        print("✅ BUILD COMPLETADO EXITOSAMENTE")
        if tesseract_incluido:
            print("🎉 EJECUTABLE AUTOCONTENIDO CON TESSERACT INCLUIDO")
        print("=" * 70)

        exe_dir = self.dist_dir / "ScannerSufexa"
        exe_file = exe_dir / "ScannerSufexa.exe"

        print(f"\n📦 Ejecutable generado en:")
        print(f"   {exe_dir}")

        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"\n📊 Tamaño del ejecutable: {size_mb:.2f} MB")

        # Calcular tamaño total de la distribución
        try:
            total_size = sum(
                f.stat().st_size
                for f in exe_dir.rglob('*')
                if f.is_file()
            )
            total_mb = total_size / (1024 * 1024)
            print(f"📊 Tamaño total de la distribución: {total_mb:.2f} MB")
        except:
            pass

        print(f"\n📁 Estructura generada:")
        print(f"   ├── ScannerSufexa.exe")
        if tesseract_incluido:
            print(f"   ├── tesseract/              ✅ Tesseract OCR incluido")
            print(f"   │   ├── tesseract.exe")
            print(f"   │   ├── tessdata/")
            print(f"   │   └── [DLLs...]")
        print(f"   ├── config/")
        print(f"   │   └── config.json")
        print(f"   ├── data/")
        print(f"   │   ├── database/")
        print(f"   │   └── logs/")
        print(f"   ├── README.txt")
        print(f"   ├── Iniciar_ScannerSufexa.bat")
        print(f"   └── [librerías y dependencias...]")

        print(f"\n🚀 PRÓXIMOS PASOS:")
        if tesseract_incluido:
            print(f"   1. ✅ Tesseract ya está incluido (no instalar)")
            print(f"   2. Editar config/config.json con las rutas de carpetas")
            print(f"   3. Crear las carpetas necesarias (scanner, albaranes, errores)")
            print(f"   4. Ejecutar: Iniciar_ScannerSufexa.bat")
        else:
            print(f"   1. ⚠️  Instalar Tesseract OCR en el sistema de destino")
            print(f"   2. Editar config/config.json con las rutas correctas")
            print(f"   3. Crear las carpetas necesarias (scanner, albaranes, errores)")
            print(f"   4. Ejecutar: Iniciar_ScannerSufexa.bat")

        print(f"\n💡 DISTRIBUCIÓN:")
        print(f"   Para distribuir, comprime la carpeta completa:")
        print(f"   {exe_dir}")
        if tesseract_incluido:
            print(f"\n   ✅ El archivo ZIP será AUTOCONTENIDO")
            print(f"   Los usuarios solo necesitarán:")
            print(f"     1. Extraer el ZIP")
            print(f"     2. Configurar rutas de carpetas")
            print(f"     3. Ejecutar el .exe")
        else:
            print(f"\n   ⚠️  Los usuarios necesitarán instalar Tesseract por separado")

    def build(self):
        """Ejecuta todo el proceso de build."""
        print("\n╔════════════════════════════════════════════════════════════════════╗")
        print("║           BUILD EJECUTABLE - SCANNER SUFEXA v1.0                   ║")
        print("║                (EJECUTABLE AUTOCONTENIDO)                          ║")
        print("╚════════════════════════════════════════════════════════════════════╝")

        try:
            self.verificar_dependencias()
            tesseract_ok = self.verificar_tesseract_portable()

            if not tesseract_ok:
                print("\n⚠️  ADVERTENCIA:")
                print("   El ejecutable se generará SIN Tesseract embebido.")
                print("   Los usuarios tendrán que instalar Tesseract por separado.")
                respuesta = input("\n¿Continuar de todas formas? (s/N): ")
                if respuesta.lower() != 's':
                    print("\n❌ Build cancelado")
                    print("\nPara preparar Tesseract portable:")
                    print("  python scripts/preparar_tesseract_portable.py")
                    return 1

            self.limpiar_directorios()
            self.crear_spec_file()
            self.ejecutar_pyinstaller()
            self.crear_estructura_adicional()
            self.crear_readme_distribucion(tesseract_incluido=tesseract_ok)
            self.crear_batch_launcher()
            self.mostrar_resumen(tesseract_incluido=tesseract_ok)

            print("\n" + "=" * 70)
            print("🎉 ¡BUILD EXITOSO!")
            print("=" * 70 + "\n")

            return 0

        except Exception as e:
            print(f"\n❌ Error durante el build: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Función principal."""
    builder = BuildExecutable()
    return builder.build()


if __name__ == "__main__":
    sys.exit(main())
