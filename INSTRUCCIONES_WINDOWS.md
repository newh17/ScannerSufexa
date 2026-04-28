# 🪟 SCANNER SUFEXA - Instalación en Windows

## 📋 Requisitos Previos

### 1. Python 3.10 o superior
- Descargar desde: https://www.python.org/downloads/
- ✅ **IMPORTANTE**: Marcar "Add Python to PATH" durante instalación

### 2. Tesseract OCR
- Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar en: `C:\Program Files\Tesseract-OCR`
- ✅ **IMPORTANTE**: Instalar paquete de idioma español (spa.traineddata)

---

## 🚀 Instalación Rápida

### Opción A: Generar Ejecutable (.exe)

```cmd
# 1. Abrir PowerShell o CMD en la carpeta del proyecto

# 2. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Generar ejecutable
python scripts\build_exe.py

# 4. El ejecutable estará en: dist\ScannerSufexa\
```

El script de build creará automáticamente:
- ✅ `ScannerSufexa.exe` (ejecutable)
- ✅ Carpetas de configuración
- ✅ Base de datos
- ✅ README de distribución
- ✅ Launcher batch

### Opción B: Ejecutar desde Código Fuente

```cmd
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar
copy config\config.example.json config\config.json
notepad config\config.json

# 3. Ejecutar
python src\main.py
```

---

## ⚙️ Configuración

Editar `config\config.json`:

```json
{
  "folders": {
    "scanner_input": "C:\\scan\\entrada",
    "output_base": "C:\\albaranes",
    "errors": "C:\\albaranes\\errores"
  },
  "tesseract": {
    "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
    "language": "spa",
    "config": "--psm 6"
  }
}
```

### Crear Carpetas Necesarias

```cmd
mkdir C:\scan\entrada
mkdir C:\albaranes
mkdir C:\albaranes\errores
```

O el sistema las creará automáticamente.

---

## 📦 Distribución del Ejecutable

Después de ejecutar `python scripts\build_exe.py`:

1. **Comprimir para distribución**:
   ```cmd
   # La carpeta dist\ScannerSufexa\ contiene todo lo necesario
   # Comprimir en ZIP para distribuir
   ```

2. **En el sistema de destino**:
   - Extraer ZIP
   - Instalar Tesseract OCR
   - Editar `config\config.json`
   - Ejecutar `Iniciar_ScannerSufexa.bat`

---

## 🧪 Pruebas (Opcional)

```cmd
# Ejecutar tests
pytest tests/

# Con cobertura
pytest --cov=src tests/
```

---

## 📊 Estructura del Proyecto

```
ScannerSufexa/
├── src/                          # Código fuente
│   ├── domain/                   # Capa de dominio (DDD)
│   ├── application/              # Casos de uso
│   ├── infrastructure/           # Servicios externos
│   ├── presentation/             # Interfaz gráfica (PySide6)
│   └── main.py                   # Punto de entrada
├── scripts/                      # Scripts de utilidad
│   └── build_exe.py             # ⭐ Script de generación .exe
├── config/                       # Configuración
│   └── config.example.json
├── docs/                         # Documentación
│   ├── generacion_ejecutable.md
│   └── instalador_windows.md
├── requirements.txt              # Dependencias producción
├── requirements-dev.txt          # Dependencias desarrollo
└── INSTRUCCIONES_WINDOWS.md     # Este archivo
```

---

## 🔧 Solución de Problemas

### Error: "Python no reconocido como comando"
- Reinstalar Python y marcar "Add to PATH"
- O añadir manualmente: `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python3XX`

### Error: "PyInstaller no encontrado"
```cmd
pip install pyinstaller
```

### Error: "PySide6 no encontrado"
```cmd
pip install PySide6
```

### Error: "Tesseract no encontrado"
- Verificar instalación en: `C:\Program Files\Tesseract-OCR`
- Verificar ruta en `config.json`

### Error durante el build
```cmd
# Limpiar y reintentar
rmdir /s /q build
rmdir /s /q dist
python scripts\build_exe.py
```

---

## 📚 Documentación Adicional

- **Generación de ejecutable**: `docs/generacion_ejecutable.md`
- **Creación de instalador**: `docs/instalador_windows.md`
- **Instrucciones generales**: `claude.md`

---

## 🎯 Flujo Completo de Distribución

1. **En tu PC Windows**:
   ```cmd
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   python scripts\build_exe.py
   ```

2. **Resultado**: `dist\ScannerSufexa\` (carpeta completa)

3. **Comprimir**: Crear `ScannerSufexa_v1.0.zip`

4. **En PC de destino**:
   - Extraer ZIP
   - Instalar Tesseract
   - Configurar rutas
   - Ejecutar `Iniciar_ScannerSufexa.bat`

---

## ✅ Checklist de Instalación

- [ ] Python 3.10+ instalado
- [ ] Tesseract OCR instalado con idioma español
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] PyInstaller instalado (`pip install -r requirements-dev.txt`)
- [ ] Ejecutable generado (`python scripts\build_exe.py`)
- [ ] Configuración editada (`config\config.json`)
- [ ] Carpetas creadas (`C:\scan`, `C:\albaranes`)
- [ ] Aplicación probada

---

## 💡 Recomendaciones

1. **Primera vez**: Ejecuta desde código fuente para probar
2. **Producción**: Genera ejecutable para distribución
3. **Testing**: Prueba en máquina virtual Windows limpia
4. **Distribución profesional**: Considera crear instalador con Inno Setup (ver `docs/instalador_windows.md`)

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en `data/logs/app.log`
2. Verifica que Tesseract esté correctamente instalado
3. Comprueba permisos de carpetas
4. Consulta documentación en `docs/`

---

**¡Listo para usar en Windows!** 🎉
