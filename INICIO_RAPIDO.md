# ⚡ INICIO RÁPIDO - Ejecutable Autocontenido

> **¿Quieres un .exe que funcione sin instalar nada?**
> Sigue estos 3 pasos simples.

---

## 🎯 Resultado Final

Un solo archivo `.zip` que el usuario solo tiene que:
1. Extraer
2. Configurar rutas
3. Ejecutar

**SIN instalar Python, Tesseract ni dependencias.**

---

## 📝 3 Pasos para Generar el .exe

### ⚙️ PASO 1: Instalar Herramientas (Solo Una Vez)

```bash
# En tu PC con Windows:

# 1. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Instalar Tesseract (si no lo tienes)
# Descarga desde: https://github.com/UB-Mannheim/tesseract/wiki
# Instala en: C:\Program Files\Tesseract-OCR
```

✅ **Esto solo lo haces UNA VEZ**

---

### 📦 PASO 2: Preparar Tesseract Portable

```bash
# Opción A - Automática (si ya tienes Tesseract instalado)
xcopy "C:\Program Files\Tesseract-OCR\*" tesseract-portable\ /E /I /Y

# Opción B - Con el script
python scripts/preparar_tesseract_portable.py
# (Sigue las instrucciones en pantalla)
```

**Verifica que funcionó:**
```bash
python scripts/preparar_tesseract_portable.py
```

Debe mostrar: `✅ VERIFICACIÓN EXITOSA`

---

### 🚀 PASO 3: Generar Ejecutable

```bash
python scripts/build_exe.py
```

**Espera 5-10 minutos** ☕

---

## ✅ Resultado

Encontrarás tu ejecutable en:

```
dist/ScannerSufexa/
├── ScannerSufexa.exe          ← Ejecutable principal
├── tesseract/                 ← Tesseract incluido
├── config/
├── data/
├── README.txt
└── Iniciar_ScannerSufexa.bat  ← Lanzador simple
```

---

## 📦 Distribuir

```bash
# Comprimir
cd dist
powershell Compress-Archive -Path ScannerSufexa -DestinationPath ScannerSufexa_v1.0.zip
```

**Entrega `ScannerSufexa_v1.0.zip` al usuario final**

---

## 👤 Instrucciones para el Usuario Final

### Para el usuario que recibe el ZIP:

1. **Extraer** `ScannerSufexa_v1.0.zip`

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

**¡Listo!** 🎉

**NO necesita instalar:**
- ❌ Python
- ❌ Tesseract
- ❌ Dependencias

---

## 🐛 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| "Tesseract portable NO encontrado" | Ejecuta: `python scripts/preparar_tesseract_portable.py` |
| "PyInstaller no encontrado" | Ejecuta: `pip install pyinstaller` |
| Build falla | Limpia: `rmdir /s /q build dist` y reintenta |
| .exe no funciona | Verifica que exista `dist/ScannerSufexa/tesseract/tesseract.exe` |

---

## 📊 Tamaños Aproximados

- **Ejecutable solo:** ~50 MB
- **Con Tesseract:** ~200-300 MB
- **ZIP final:** ~80-120 MB (comprimido)

---

## ✅ Checklist Final

Antes de distribuir, verifica:

- [ ] `python scripts/preparar_tesseract_portable.py` → ✅ VERIFICACIÓN EXITOSA
- [ ] `python scripts/build_exe.py` → ✅ BUILD COMPLETADO
- [ ] Probado en tu PC
- [ ] `dist/ScannerSufexa/tesseract/` existe
- [ ] README.txt dice "EJECUTABLE AUTOCONTENIDO"
- [ ] ZIP creado
- [ ] Probado en PC limpia (sin Python/Tesseract)

---

## 🎯 Comandos Completos (Todo en Uno)

Para copiar y pegar:

```bash
# 1. Instalar (solo primera vez)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Preparar Tesseract
xcopy "C:\Program Files\Tesseract-OCR\*" tesseract-portable\ /E /I /Y
python scripts/preparar_tesseract_portable.py

# 3. Generar ejecutable
python scripts/build_exe.py

# 4. Comprimir para distribución
cd dist
powershell Compress-Archive -Path ScannerSufexa -DestinationPath ScannerSufexa_v1.0.zip -Force
cd ..

# ¡Listo!
```

---

## 💡 Tips

1. **Primera vez:** Prueba en máquina virtual Windows limpia
2. **Versiones:** Nombra el ZIP con fecha: `ScannerSufexa_2026-04-22.zip`
3. **Tamaño:** Es normal que el .exe con Tesseract pese 200-300 MB
4. **Tesseract:** Si actualizas Tesseract, repite PASO 2

---

## 🚀 ¡Todo Listo!

Ya tienes un **ejecutable profesional autocontenido**.

**Archivo de documentación completa:** `GENERACION_EXE_AUTOCONTENIDO.md`
