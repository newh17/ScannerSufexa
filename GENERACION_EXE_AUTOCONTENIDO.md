# 🚀 Generación de Ejecutable Autocontenido

## ¿Qué es un Ejecutable Autocontenido?

Un ejecutable autocontenido es un .exe que **incluye TODO lo necesario** para funcionar:
- ✅ Todas las librerías Python
- ✅ Tesseract OCR completo
- ✅ Archivos de idioma para OCR
- ✅ DLLs y dependencias

**El usuario final NO necesita instalar nada** (ni Python, ni Tesseract, ni dependencias).

---

## 📋 Requisitos Previos (Solo para Desarrollo)

Esto solo lo necesitas **TÚ** para generar el .exe, **NO el usuario final**:

1. **Windows con Python 3.10+**
2. **Tesseract instalado** (para copiar los archivos)
3. **Dependencias del proyecto**

---

## 🎯 Proceso Completo (Paso a Paso)

### PASO 1: Instalar Dependencias

```cmd
# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar PyInstaller (necesario para generar .exe)
pip install -r requirements-dev.txt
```

---

### PASO 2: Preparar Tesseract Portable

#### Opción A - Desde Instalación Existente (RECOMENDADO)

Si ya tienes Tesseract instalado en tu PC:

```cmd
# Ejecutar script de preparación
python scripts/preparar_tesseract_portable.py
```

El script te mostrará instrucciones para:
1. Copiar tu instalación de Tesseract a `tesseract-portable/`
2. Verificar que todos los archivos estén presentes

**Pasos manuales:**
```cmd
# Copiar Tesseract instalado a la carpeta del proyecto
xcopy "C:\Program Files\Tesseract-OCR\*" tesseract-portable\ /E /I /Y

# Verificar que esté correcto
python scripts/preparar_tesseract_portable.py
```

#### Opción B - Descarga Manual

Si NO tienes Tesseract instalado:

1. Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar temporalmente en tu PC
3. Seguir Opción A

---

### PASO 3: Verificar Estructura

Después de preparar Tesseract, tu proyecto debe verse así:

```
ScannerSufexa/
├── tesseract-portable/       ⭐ NUEVO - Tesseract portable
│   ├── tesseract.exe
│   ├── tessdata/
│   │   ├── spa.traineddata
│   │   └── eng.traineddata
│   └── [DLLs...]
├── src/
├── scripts/
└── ...
```

Verifica ejecutando:
```cmd
python scripts/preparar_tesseract_portable.py
```

Debe mostrar: **✅ VERIFICACIÓN EXITOSA**

---

### PASO 4: Generar el Ejecutable

```cmd
python scripts/build_exe.py
```

El script:
1. ✅ Verifica dependencias Python
2. ✅ Verifica Tesseract portable
3. ✅ Genera archivo .spec
4. ✅ Ejecuta PyInstaller
5. ✅ Incluye Tesseract en el bundle
6. ✅ Crea estructura de carpetas
7. ✅ Genera README y launcher

**Tiempo estimado:** 5-10 minutos (según tu PC)

---

### PASO 5: Resultado

El ejecutable estará en:
```
dist/ScannerSufexa/
├── ScannerSufexa.exe          ⭐ EJECUTABLE PRINCIPAL
├── tesseract/                 ⭐ Tesseract embebido
│   ├── tesseract.exe
│   ├── tessdata/
│   └── [DLLs...]
├── config/
│   └── config.json
├── data/
│   ├── database/
│   └── logs/
├── README.txt
├── Iniciar_ScannerSufexa.bat
└── [librerías Python empaquetadas...]
```

**Tamaño aproximado:** 200-300 MB (incluye Tesseract + Python + librerías)

---

## 📦 Distribución

### Crear ZIP para Distribución

```cmd
# Comprimir la carpeta completa
cd dist
powershell Compress-Archive -Path ScannerSufexa -DestinationPath ScannerSufexa_v1.0.zip
```

### Entregar al Usuario Final

El usuario final solo necesita:

1. **Extraer el ZIP**
2. **Editar config.json** (rutas de carpetas)
3. **Ejecutar Iniciar_ScannerSufexa.bat**

**NO necesita instalar:**
- ❌ Python
- ❌ Tesseract
- ❌ Ninguna dependencia

---

## 🔧 Solución de Problemas

### Error: "Tesseract portable NO encontrado"

**Causa:** No se ejecutó el PASO 2

**Solución:**
```cmd
python scripts/preparar_tesseract_portable.py
# Seguir las instrucciones
```

---

### Error: "PyInstaller no encontrado"

**Causa:** No se instalaron las dependencias de desarrollo

**Solución:**
```cmd
pip install -r requirements-dev.txt
```

---

### Error durante PyInstaller

**Causa:** Build anterior corrupto

**Solución:**
```cmd
# Limpiar y reintentar
rmdir /s /q build
rmdir /s /q dist
python scripts/build_exe.py
```

---

### Ejecutable generado pero Tesseract no funciona

**Verificar:**
1. ¿Tesseract portable tiene `tesseract.exe`?
2. ¿Existe `tessdata/spa.traineddata`?
3. ¿Están todas las DLLs (leptonica, libjpeg, etc.)?

**Solución:**
```cmd
# Re-verificar Tesseract
python scripts/preparar_tesseract_portable.py

# Si falla, copiar manualmente desde instalación
xcopy "C:\Program Files\Tesseract-OCR\*" tesseract-portable\ /E /I /Y
```

---

## 📊 Comparación

### Antes (Ejecutable Normal)

**El usuario necesita:**
- ✅ Extraer ZIP
- ❌ Instalar Python
- ❌ Instalar Tesseract
- ❌ Configurar PATH
- ❌ Instalar dependencias
- ✅ Configurar config.json
- ✅ Ejecutar .exe

**Complejidad:** ALTA 😰

---

### Ahora (Ejecutable Autocontenido)

**El usuario necesita:**
- ✅ Extraer ZIP
- ✅ Configurar config.json
- ✅ Ejecutar .exe

**Complejidad:** BAJA 😊

---

## 🎯 Checklist Completo

Antes de distribuir, verifica:

- [ ] Tesseract portable preparado (`python scripts/preparar_tesseract_portable.py`)
- [ ] Verificación exitosa (✅ mensaje verde)
- [ ] Build ejecutado (`python scripts/build_exe.py`)
- [ ] Sin errores durante el build
- [ ] Ejecutable probado en tu PC
- [ ] README.txt generado dice "EJECUTABLE AUTOCONTENIDO"
- [ ] Carpeta `tesseract/` existe en dist/ScannerSufexa/
- [ ] Probado en PC limpia (sin Tesseract ni Python instalado)
- [ ] ZIP creado para distribución
- [ ] Instrucciones claras para el usuario final

---

## 💡 Recomendaciones Finales

1. **Prueba en máquina virtual Windows limpia** antes de distribuir
2. **Documenta las rutas** que el usuario debe configurar
3. **Incluye ejemplos** de config.json en el README
4. **Tamaño del ZIP:** ~200-300 MB (normal con Tesseract incluido)

---

## 🎉 ¡Listo!

Ahora tienes un **ejecutable profesional autocontenido** que funciona en cualquier PC con Windows sin necesidad de instalar nada.

**¿Preguntas?** Revisa los logs en caso de errores o consulta la documentación completa.
