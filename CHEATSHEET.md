# 📋 CHEATSHEET - Scanner Sufexa

> Guía de referencia rápida - Un vistazo

---

## ⚡ Generación de Ejecutable Autocontenido

### 🎯 TODO EN UNO (Recomendado)

```bash
python scripts/generar_todo_autocontenido.py
```

**Resultado:** `dist/ScannerSufexa_v1.0_[fecha].zip` ✅

---

### 📝 PASO A PASO (Alternativa)

```bash
# 1. Instalar
pip install -r requirements.txt requirements-dev.txt

# 2. Preparar Tesseract
xcopy "C:\Program Files\Tesseract-OCR\*" tesseract-portable\ /E /I /Y

# 3. Generar
python scripts/build_exe.py

# 4. Comprimir
cd dist
powershell Compress-Archive -Path ScannerSufexa -DestinationPath ScannerSufexa_v1.0.zip
```

---

## 📦 Contenido del Ejecutable

```
ScannerSufexa/
├── ScannerSufexa.exe          → Ejecutable
├── tesseract/                 → OCR incluido
├── config/config.json         → Configuración
├── data/                      → Base de datos y logs
├── README.txt                 → Instrucciones
└── Iniciar_ScannerSufexa.bat  → Launcher
```

**Tamaño:** ~200-300 MB

---

## 👤 Instrucciones Usuario Final

### 1. Extraer ZIP
### 2. Editar config.json
```json
{
  "folders": {
    "scanner_input": "C:\\scan\\entrada",
    "output_base": "C:\\albaranes",
    "errors": "C:\\albaranes\\errores"
  }
}
```
### 3. Ejecutar `Iniciar_ScannerSufexa.bat`

**¡Listo!** ✅

---

## 🔧 Comandos Útiles

| Tarea | Comando |
|-------|---------|
| Ejecutar desde código | `python src\main.py` |
| Verificar Tesseract | `python scripts/preparar_tesseract_portable.py` |
| Generar ejecutable | `python scripts/build_exe.py` |
| TODO automatizado | `python scripts/generar_todo_autocontenido.py` |
| Limpiar build | `rmdir /s /q build dist` |
| Tests | `pytest tests/` |

---

## 🐛 Problemas Comunes

| Síntoma | Causa | Solución |
|---------|-------|----------|
| "Tesseract NO encontrado" | No se preparó portable | `python scripts/preparar_tesseract_portable.py` |
| "PyInstaller no encontrado" | Falta dependencia | `pip install pyinstaller` |
| Build falla | Build corrupto | `rmdir /s /q build dist` → reintentar |
| .exe no funciona | Falta Tesseract en bundle | Verificar `dist/ScannerSufexa/tesseract/` existe |
| OCR no funciona | Faltan archivos de idioma | Copiar `tessdata/spa.traineddata` |

---

## 📁 Estructura del Proyecto

```
ScannerSufexa/
├── src/
│   ├── domain/           → Entidades, Value Objects
│   ├── application/      → Casos de uso
│   ├── infrastructure/   → OCR, DB, FileSystem
│   └── presentation/     → Interfaz PySide6
├── scripts/
│   ├── generar_todo_autocontenido.py  ← TODO EN UNO
│   ├── build_exe.py                   ← Generar .exe
│   └── preparar_tesseract_portable.py ← Preparar OCR
├── config/
├── docs/
├── tests/
└── tesseract-portable/   → Tesseract para incluir
```

---

## ⚙️ Configuración (config.json)

### Mínima

```json
{
  "folders": {
    "scanner_input": "C:\\scan\\entrada",
    "output_base": "C:\\albaranes",
    "errors": "C:\\albaranes\\errores"
  }
}
```

### Completa

```json
{
  "folders": {
    "scanner_input": "C:\\scan\\entrada",
    "output_base": "C:\\albaranes",
    "errors": "C:\\albaranes\\errores"
  },
  "tesseract": {
    "path": "",  // Vacío = usar incluido
    "language": "spa",
    "config": "--psm 6"
  },
  "logging": {
    "level": "INFO",
    "file": "data/logs/app.log"
  }
}
```

---

## 🚀 Flujo de Procesamiento

```
PDF en scanner/
    ↓
Detectar archivo nuevo
    ↓
Aplicar OCR
    ↓
Extraer: cliente, fecha, número
    ↓
Validar (duplicados, formato)
    ↓
Renombrar: CLIENTE_FECHA_NUMERO.pdf
    ↓
Mover a: albaranes/CLIENTE/archivo.pdf
    ↓
Registrar en base de datos
    ↓
Actualizar ranking
```

**Errores** → `albaranes/errores/`

---

## 📊 Datos Extraídos

| Campo | Ejemplo | Formato Salida |
|-------|---------|----------------|
| Cliente | METALCRISMAR, S.L. | METALCRISMAR, S.L |
| Fecha | 23/01/2026 | 23-01-2026 |
| Número | 71206 | 71206 |

**Archivo final:** `METALCRISMAR, S.L_23-01-2026_71206.pdf`

---

## 📚 Documentación

| Archivo | Contenido |
|---------|-----------|
| `README.md` | 📖 Documentación principal |
| `INICIO_RAPIDO.md` | ⚡ Guía rápida 3 pasos |
| `GENERACION_EXE_AUTOCONTENIDO.md` | 📘 Guía completa detallada |
| `INSTRUCCIONES_WINDOWS.md` | 🪟 Específico Windows |
| `CHEATSHEET.md` | 📋 Esta guía |

---

## ✅ Checklist Pre-Distribución

- [ ] Tesseract portable verificado (✅ verde)
- [ ] Build completado sin errores
- [ ] Ejecutable probado localmente
- [ ] Carpeta `tesseract/` incluida en dist/
- [ ] README.txt dice "AUTOCONTENIDO"
- [ ] ZIP creado
- [ ] Tamaño ~200-300 MB
- [ ] Probado en VM Windows limpia
- [ ] Instrucciones para usuario incluidas

---

## 🎯 Versiones

| Componente | Versión |
|------------|---------|
| Python | 3.10+ |
| PySide6 | 6.x |
| Tesseract | 5.x |
| PyInstaller | 6.x |

---

## 💡 Tips Rápidos

1. **Primera generación:** Tarda 5-10 minutos (normal)
2. **Tamaño grande:** Es normal por Tesseract incluido
3. **Prueba en VM:** Siempre antes de distribuir
4. **Config.json:** Solo rutas, Tesseract automático
5. **Logs:** `data/logs/app.log` para debug

---

## 🔗 Enlaces Útiles

- **Tesseract:** https://github.com/UB-Mannheim/tesseract/wiki
- **Python:** https://www.python.org/downloads/
- **PyInstaller:** https://pyinstaller.org/

---

## 📞 Debug Rápido

```bash
# Ver logs
type data\logs\app.log

# Verificar Tesseract en ejecutable
dir dist\ScannerSufexa\tesseract

# Test rápido desde código
python src\main.py

# Limpiar todo
rmdir /s /q build dist tesseract-portable
```

---

**Guarda esta página para referencia rápida** 📌
