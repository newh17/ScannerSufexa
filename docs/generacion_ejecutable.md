# Generación de Ejecutable (.exe) - Scanner Sufexa

## 📋 Requisitos Previos

### Sistema Operativo
- **Windows 10/11** (para generar .exe de Windows)
- Python 3.10 o superior

### Dependencias Python
```bash
pip install pyinstaller
pip install -r requirements.txt
```

## 🔨 Generar Ejecutable

### Método Automático (Recomendado)

Ejecuta el script de build automatizado:

```bash
python scripts/build_exe.py
```

Este script:
1. ✅ Verifica que PyInstaller esté instalado
2. ✅ Limpia builds anteriores
3. ✅ Crea el archivo .spec con configuración optimizada
4. ✅ Ejecuta PyInstaller
5. ✅ Crea estructura de carpetas
6. ✅ Genera README de distribución
7. ✅ Crea launcher batch

### Método Manual

Si prefieres hacerlo manualmente:

```bash
# 1. Crear archivo .spec (si no existe)
pyi-makespec --onedir --windowed --name ScannerSufexa src/main.py

# 2. Editar scanner_sufexa.spec (ver configuración abajo)

# 3. Generar ejecutable
pyinstaller --clean --noconfirm scanner_sufexa.spec
```

## ⚙ Configuración de PyInstaller (.spec)

El archivo `scanner_sufexa.spec` contiene la configuración completa:

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],                    # Punto de entrada
    pathex=[],
    binaries=[],
    datas=[
        ('config/config.example.json', 'config'),  # Incluir config
    ],
    hiddenimports=[
        # PySide6
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        # Watchdog
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        # OCR
        'pytesseract',
        'PIL',
        'PIL.Image',
        # Base de datos
        'sqlite3',
    ],
    excludes=[
        # Excluir librerías innecesarias para reducir tamaño
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
)

exe = EXE(
    ...,
    name='ScannerSufexa',
    debug=False,
    console=False,                      # Sin ventana de consola (GUI)
    icon='docs/icon.ico',               # Icono personalizado (opcional)
)
```

## 📦 Estructura del Ejecutable Generado

```
dist/ScannerSufexa/
├── ScannerSufexa.exe              # Ejecutable principal (~50-80 MB)
├── _internal/                     # Librerías y dependencias
│   ├── PySide6/
│   ├── PIL/
│   ├── sqlite3.dll
│   └── [otras librerías...]
├── config/
│   └── config.json                # Configuración
├── data/
│   ├── database/                  # Base de datos SQLite
│   └── logs/                      # Archivos de log
├── README.txt                     # Instrucciones
└── Iniciar_ScannerSufexa.bat     # Launcher batch
```

## 📊 Tamaño del Ejecutable

- **Sin comprimir**: ~150-200 MB (incluye todas las librerías)
- **Comprimido (.zip)**: ~50-70 MB
- **Con UPX**: ~100-120 MB

### Reducir Tamaño

Para reducir el tamaño del ejecutable:

1. **Usar UPX**:
```python
# En .spec
exe = EXE(
    ...,
    upx=True,  # Habilitar compresión UPX
)
```

2. **Excluir módulos innecesarios**:
```python
excludes=[
    'matplotlib', 'numpy', 'pandas', 'scipy',
    'IPython', 'jupyter', 'tornado', 'zmq',
]
```

3. **Modo onefile** (menos recomendado para esta app):
```bash
pyinstaller --onefile src/main.py
```

## 🔧 Inclusión de Tesseract

### Opción 1: Tesseract Externo (Recomendado)

El usuario instala Tesseract por separado:
- ✅ Menor tamaño del ejecutable
- ✅ Actualizaciones independientes
- ✅ Instalación estándar de Windows

**Instrucciones en README.txt**:
```
1. Descargar Tesseract desde:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Instalar en: C:\Program Files\Tesseract-OCR

3. Configurar ruta en config.json:
   "tesseract": {
     "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
   }
```

### Opción 2: Tesseract Incluido

Incluir Tesseract en el ejecutable:

```python
# En .spec
datas=[
    ('C:/Program Files/Tesseract-OCR/tesseract.exe', 'tesseract'),
    ('C:/Program Files/Tesseract-OCR/tessdata', 'tesseract/tessdata'),
],
```

⚠️ **Advertencia**: Esto aumenta el tamaño ~100 MB adicionales.

## 🚀 Distribución

### Crear Paquete de Distribución

1. **Comprimir carpeta**:
```bash
# Windows (PowerShell)
Compress-Archive -Path dist/ScannerSufexa -DestinationPath ScannerSufexa_v1.0.zip

# O usar 7-Zip, WinRAR, etc.
```

2. **Contenido del paquete**:
```
ScannerSufexa_v1.0.zip
└── ScannerSufexa/
    ├── ScannerSufexa.exe
    ├── _internal/
    ├── config/
    ├── data/
    ├── README.txt
    └── Iniciar_ScannerSufexa.bat
```

### Instalación en Sistema de Destino

1. Extraer `ScannerSufexa_v1.0.zip`
2. Instalar Tesseract OCR
3. Editar `config/config.json`
4. Ejecutar `Iniciar_ScannerSufexa.bat`

## 🐛 Solución de Problemas

### Error: "Failed to execute script"

**Causa**: Falta una dependencia o módulo.

**Solución**:
1. Revisar `hiddenimports` en .spec
2. Agregar el módulo faltante
3. Re-generar ejecutable

### Error: "DLL load failed"

**Causa**: Falta una librería de sistema.

**Solución**:
1. Instalar Visual C++ Redistributable
2. Incluir DLL en `binaries` del .spec

### Ejecutable muy lento al iniciar

**Causa**: Modo onefile descomprime todo al inicio.

**Solución**: Usar modo onedir (recomendado).

### No se encuentra archivo de configuración

**Causa**: Rutas relativas incorrectas.

**Solución**:
```python
# Obtener ruta del ejecutable
if getattr(sys, 'frozen', False):
    # Ejecutable
    base_path = Path(sys._MEIPASS)
else:
    # Desarrollo
    base_path = Path(__file__).parent
```

## 📝 Checklist de Build

Antes de distribuir, verificar:

- [ ] Ejecutable se abre sin errores
- [ ] Interfaz gráfica funciona correctamente
- [ ] Configuración se carga/guarda correctamente
- [ ] Base de datos se crea correctamente
- [ ] Logs se escriben correctamente
- [ ] README.txt está incluido
- [ ] config.json de ejemplo está incluido
- [ ] Tamaño del paquete es razonable (<100 MB comprimido)
- [ ] Tesseract funciona (si está incluido)
- [ ] No hay errores en el log

## 🔐 Firma Digital (Opcional)

Para producción profesional:

```bash
# Con signtool (Windows SDK)
signtool sign /f certificado.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 ScannerSufexa.exe
```

## 📋 Versiones

Mantener registro de versiones:

```
v1.0.0 (2026-04-20)
- Release inicial
- Procesamiento automático de albaranes
- Interfaz gráfica completa
- Base de datos SQLite
```

## 💡 Consejos

1. **Testear en máquina limpia**: Probar el ejecutable en un Windows sin Python instalado
2. **Incluir dependencias visuales**: Verificar que todas las librerías Qt estén incluidas
3. **Comprimir para distribución**: Usar .zip o instalador (NSIS, InnoSetup)
4. **Documentar requisitos**: Listar claramente lo que el usuario debe instalar
5. **Crear instalador**: Para distribución profesional, usar InnoSetup o WiX

## 🔗 Referencias

- PyInstaller: https://pyinstaller.org/
- PySide6: https://doc.qt.io/qtforpython/
- Tesseract: https://github.com/tesseract-ocr/tesseract
- UPX: https://upx.github.io/
