# 🖨️ Scanner Sufexa - Sistema Automatizado de Procesamiento de Albaranes

> **Aplicación de escritorio para Windows que procesa automáticamente PDFs escaneados de albaranes usando OCR.**

## ✨ Características

- 📁 **Monitorización automática** de carpeta de entrada
- 🔍 **OCR integrado** con Tesseract (incluido en el ejecutable)
- 📋 **Extracción inteligente** de datos (cliente, fecha, número)
- 🗂️ **Organización automática** por cliente
- 💾 **Base de datos SQLite** con historial completo
- 📊 **Ranking de clientes** por volumen de albaranes
- 🎨 **Interfaz gráfica** profesional con PySide6
- 🏗️ **Arquitectura DDD** (Domain-Driven Design)

---

## 🚀 Inicio Rápido - Ejecutable Autocontenido

### ⚡ Opción 1: Automatizado (RECOMENDADO)

```bash
# Un solo comando para hacer TODO:
python scripts/generar_todo_autocontenido.py
```

Este script:
1. ✅ Prepara Tesseract portable
2. ✅ Genera ejecutable con PyInstaller
3. ✅ Comprime en ZIP listo para distribuir

**Requisitos previos:**
- Windows con Python 3.10+
- Tesseract instalado (C:\Program Files\Tesseract-OCR)
- Dependencias: `pip install -r requirements.txt requirements-dev.txt`

---

### 📝 Opción 2: Paso a Paso

```bash
# 1. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Preparar Tesseract portable
xcopy "C:\Program Files\Tesseract-OCR\*" tesseract-portable\ /E /I /Y

# 3. Generar ejecutable
python scripts/build_exe.py

# 4. Comprimir
cd dist
powershell Compress-Archive -Path ScannerSufexa -DestinationPath ScannerSufexa_v1.0.zip
```

**Documentación completa:** Ver [`INICIO_RAPIDO.md`](INICIO_RAPIDO.md)

---

## 📦 Resultado Final

Después de generar el ejecutable:

```
dist/ScannerSufexa_v1.0_2026-04-22.zip
```

**Contenido del ZIP:**
```
ScannerSufexa/
├── ScannerSufexa.exe          ← Ejecutable principal
├── tesseract/                 ← Tesseract OCR incluido
│   ├── tesseract.exe
│   ├── tessdata/
│   └── [DLLs...]
├── config/
│   └── config.json
├── data/
├── README.txt
└── Iniciar_ScannerSufexa.bat
```

**Tamaño:** ~200-300 MB (incluye Tesseract completo)

---

## 👤 Instrucciones para el Usuario Final

El usuario que recibe el .zip solo necesita:

1. **Extraer** el ZIP
2. **Editar** `config\config.json`:
   ```json
   {
     "folders": {
       "scanner_input": "C:\\scan\\entrada",
       "output_base": "C:\\albaranes",
       "errors": "C:\\albaranes\\errores"
     }
   }
   ```
3. **Ejecutar** `Iniciar_ScannerSufexa.bat`

**NO necesita instalar:**
- ❌ Python
- ❌ Tesseract OCR
- ❌ Dependencias

**Todo está incluido en el ejecutable** ✅

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [`INICIO_RAPIDO.md`](INICIO_RAPIDO.md) | ⚡ Guía rápida visual de 3 pasos |
| [`GENERACION_EXE_AUTOCONTENIDO.md`](GENERACION_EXE_AUTOCONTENIDO.md) | 📖 Guía completa detallada |
| [`INSTRUCCIONES_WINDOWS.md`](INSTRUCCIONES_WINDOWS.md) | 🪟 Instrucciones específicas de Windows |
| [`claude.md`](claude.md) | 🏗️ Arquitectura y diseño del proyecto |

---

## 🏗️ Arquitectura

Proyecto desarrollado siguiendo **Domain-Driven Design (DDD)**:

```
src/
├── domain/              # Entidades, Value Objects, Interfaces
├── application/         # Casos de uso
├── infrastructure/      # OCR, Base de datos, Filesystem
└── presentation/        # Interfaz gráfica (PySide6)
```

**Tecnologías:**
- Python 3.10+
- PySide6 (GUI)
- Tesseract OCR
- SQLite
- watchdog (monitorización de carpetas)
- PyInstaller (empaquetado)

---

## 🔧 Desarrollo

### Ejecutar desde Código Fuente

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar
copy config\config.example.json config\config.json

# Ejecutar
python src\main.py
```

### Tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

---

## 📊 Flujo de Trabajo

1. **Scanner** guarda PDF en carpeta de entrada
2. **Watcher** detecta nuevo archivo
3. **OCR** extrae texto del PDF
4. **Extractor** identifica: cliente, fecha, número
5. **Validador** verifica datos y previene duplicados
6. **FileSystem** renombra y mueve a carpeta del cliente
7. **Base de datos** registra el albaránr
8. **Interfaz** muestra actualización en tiempo real

---

## 🎯 Formato de Albarán Soportado

Este sistema está diseñado para un **formato específico** de albarán:

**Campos extraídos:**
- **Cliente:** METALCRISMAR, S.L.
- **Fecha:** Campo "Data" → 23/01/2026
- **Número:** Campo "Albarà núm." → 71206

**Formato de salida:**
```
METALCRISMAR, S.L_23-01-2026_71206.pdf
```

⚠️ **IMPORTANTE:** No es un sistema genérico. Está optimizado para un formato concreto de albarán.

---

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| "Tesseract portable NO encontrado" | Ejecuta: `python scripts/preparar_tesseract_portable.py` |
| "PyInstaller no encontrado" | Ejecuta: `pip install pyinstaller` |
| Build falla | Limpia: `rmdir /s /q build dist` y reintenta |
| Ejecutable no funciona | Verifica que `dist/ScannerSufexa/tesseract/` existe |

**Ver logs:** `data/logs/app.log`

---

## 📋 Checklist de Distribución

Antes de entregar el ejecutable:

- [ ] Tesseract portable preparado
- [ ] Build ejecutado sin errores
- [ ] Ejecutable probado localmente
- [ ] README.txt dice "EJECUTABLE AUTOCONTENIDO"
- [ ] Carpeta `tesseract/` incluida
- [ ] ZIP creado
- [ ] Probado en PC limpia (sin Python/Tesseract)
- [ ] Instrucciones claras para usuario final

---

## 💡 Mejoras Futuras

- [ ] Soporte para múltiples formatos de albarán
- [ ] Configuración de campos extraíbles por UI
- [ ] IA para mejorar precisión de extracción
- [ ] API REST para integración
- [ ] Instalador MSI profesional
- [ ] Firma digital del ejecutable

---

## 📝 Licencia

Proyecto propietario - Scanner Sufexa © 2026

---

## 🆘 Soporte

Para problemas o preguntas:
1. Revisa la documentación en `docs/`
2. Consulta los logs en `data/logs/app.log`
3. Verifica que Tesseract esté correctamente incluido

---

## 🎉 ¡Listo para Usar!

Con el **ejecutable autocontenido**, distribuir la aplicación es tan simple como:

1. Generar el .zip
2. Enviarlo al usuario
3. El usuario lo extrae y ejecuta

**Sin complicaciones. Sin instalaciones. Sin dependencias.**

**Es así de simple.** 🚀
