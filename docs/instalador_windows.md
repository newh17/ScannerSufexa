# Crear Instalador de Windows - Scanner Sufexa

## 🎯 Objetivo

Crear un instalador profesional (.msi o .exe) para facilitar la instalación en Windows.

## 🛠 Herramientas Recomendadas

### Opción 1: Inno Setup (Recomendado)

**Ventajas:**
- ✅ Gratuito y open source
- ✅ Fácil de usar con interfaz gráfica
- ✅ Instaladores pequeños
- ✅ Ampliamente usado y confiable

**Descargar**: https://jrsoftware.org/isdl.php

### Opción 2: NSIS

**Ventajas:**
- ✅ Gratuito y open source
- ✅ Muy personalizable
- ✅ Instaladores muy pequeños

**Descargar**: https://nsis.sourceforge.io/

### Opción 3: WiX Toolset

**Ventajas:**
- ✅ Formato .msi nativo de Windows
- ✅ Integración con Visual Studio
- ✅ Muy profesional

**Descargar**: https://wixtoolset.org/

## 📝 Crear Instalador con Inno Setup

### 1. Preparar el Build

Primero, genera el ejecutable:

```bash
python scripts/build_exe.py
```

Esto creará: `dist/ScannerSufexa/`

### 2. Crear Script de Inno Setup

Crear archivo `installer.iss`:

```ini
; Script de Inno Setup para Scanner Sufexa

[Setup]
; Información de la aplicación
AppName=Scanner Sufexa
AppVersion=1.0
AppPublisher=Scanner Sufexa
AppPublisherURL=https://scannersufexa.com
DefaultDirName={autopf}\ScannerSufexa
DefaultGroupName=Scanner Sufexa
OutputDir=.\installer_output
OutputBaseFilename=ScannerSufexa_Setup_v1.0
Compression=lzma2/max
SolidCompression=yes

; Icono del instalador
SetupIconFile=docs\icon.ico

; Requisitos
MinVersion=6.1sp1
ArchitecturesInstallIn64BitMode=x64

; Licencia
LicenseFile=LICENSE

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en escritorio"; GroupDescription: "Iconos adicionales:"
Name: "quicklaunchicon"; Description: "Crear icono en inicio rápido"; GroupDescription: "Iconos adicionales:"

[Files]
; Copiar todos los archivos del ejecutable
Source: "dist\ScannerSufexa\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Iconos del menú inicio
Name: "{group}\Scanner Sufexa"; Filename: "{app}\ScannerSufexa.exe"
Name: "{group}\Configuración"; Filename: "{app}\config\config.json"
Name: "{group}\Logs"; Filename: "{app}\data\logs"
Name: "{group}\Desinstalar Scanner Sufexa"; Filename: "{uninstallexe}"

; Icono de escritorio
Name: "{autodesktop}\Scanner Sufexa"; Filename: "{app}\ScannerSufexa.exe"; Tasks: desktopicon

[Run]
; Ejecutar después de instalar (opcional)
Filename: "{app}\ScannerSufexa.exe"; Description: "Ejecutar Scanner Sufexa"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Eliminar logs y base de datos al desinstalar (opcional)
Type: filesandordirs; Name: "{app}\data\logs"
Type: filesandordirs; Name: "{app}\data\database"

[Code]
// Verificar que Tesseract esté instalado
function InitializeSetup(): Boolean;
var
  TesseractPath: String;
begin
  Result := True;

  TesseractPath := 'C:\Program Files\Tesseract-OCR\tesseract.exe';

  if not FileExists(TesseractPath) then
  begin
    if MsgBox('Tesseract OCR no está instalado.' + #13#10 +
              'Scanner Sufexa requiere Tesseract para funcionar.' + #13#10 + #13#10 +
              '¿Desea continuar de todas formas?',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

// Crear carpetas necesarias en el primer uso
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Crear carpetas por defecto
    if not DirExists('C:\scan\entrada') then
      CreateDir('C:\scan\entrada');

    if not DirExists('C:\albaranes') then
      CreateDir('C:\albaranes');

    if not DirExists('C:\albaranes\errores') then
      CreateDir('C:\albaranes\errores');
  end;
end;
```

### 3. Compilar Instalador

1. Abrir Inno Setup Compiler
2. Abrir `installer.iss`
3. Build > Compile
4. El instalador se generará en `installer_output/`

Resultado: `ScannerSufexa_Setup_v1.0.exe`

## 📦 Estructura del Instalador

El instalador:

1. **Verifica requisitos**:
   - Windows 10/11
   - Tesseract instalado (opcional, con advertencia)

2. **Instala archivos** en:
   - `C:\Program Files\ScannerSufexa\`

3. **Crea iconos**:
   - Menú Inicio > Scanner Sufexa
   - Escritorio (opcional)
   - Inicio rápido (opcional)

4. **Crea carpetas**:
   - `C:\scan\entrada`
   - `C:\albaranes`
   - `C:\albaranes\errores`

5. **Configura desinstalador**:
   - Panel de Control > Programas
   - Opción de mantener o eliminar datos

## 🔧 Personalización Avanzada

### Incluir Tesseract en el Instalador

```ini
[Files]
; Incluir Tesseract portable
Source: "tesseract\*"; DestDir: "{app}\tesseract"; Flags: ignoreversion recursesubdirs

[Code]
// Actualizar config.json para usar Tesseract incluido
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigFile := ExpandConstant('{app}\config\config.json');

    // Leer config
    LoadStringFromFile(ConfigFile, ConfigContent);

    // Reemplazar ruta de Tesseract
    StringChangeEx(ConfigContent,
      '"path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"',
      '"path": "' + ExpandConstant('{app}') + '\\tesseract\\tesseract.exe"',
      True);

    // Guardar config
    SaveStringToFile(ConfigFile, ConfigContent, False);
  end;
end;
```

### Asistente de Configuración Inicial

```ini
[Code]
var
  ConfigPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  // Página personalizada para configurar rutas
  ConfigPage := CreateInputDirPage(
    wpSelectDir,
    'Configuración de Carpetas',
    'Seleccione las carpetas del sistema',
    'Scanner Sufexa necesita tres carpetas para funcionar:',
    False,
    ''
  );

  ConfigPage.Add('Carpeta Scanner (entrada):');
  ConfigPage.Add('Carpeta Albaranes (salida):');
  ConfigPage.Add('Carpeta Errores:');

  // Valores por defecto
  ConfigPage.Values[0] := 'C:\scan\entrada';
  ConfigPage.Values[1] := 'C:\albaranes';
  ConfigPage.Values[2] := 'C:\albaranes\errores';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear carpetas seleccionadas
    CreateDir(ConfigPage.Values[0]);
    CreateDir(ConfigPage.Values[1]);
    CreateDir(ConfigPage.Values[2]);

    // Actualizar config.json con las rutas seleccionadas
    ConfigFile := ExpandConstant('{app}\config\config.json');
    LoadStringFromFile(ConfigFile, ConfigContent);

    StringChangeEx(ConfigContent,
      '"scanner_input": "C:\\scan\\entrada"',
      '"scanner_input": "' + ConfigPage.Values[0] + '"',
      True);

    // ... (similar para otras rutas)

    SaveStringToFile(ConfigFile, ConfigContent, False);
  end;
end;
```

## ✅ Checklist de Instalador

Antes de distribuir el instalador:

- [ ] Ejecutable compilado correctamente
- [ ] Icono incluido y visible
- [ ] Licencia incluida
- [ ] README incluido
- [ ] Instalador firmado digitalmente (opcional)
- [ ] Testado en Windows limpio
- [ ] Tesseract incluido o instrucciones claras
- [ ] Desinstalador funciona correctamente
- [ ] No hay errores durante instalación
- [ ] Aplicación se ejecuta después de instalar
- [ ] Carpetas creadas correctamente
- [ ] Configuración por defecto funciona

## 📊 Tamaño del Instalador

- **Sin Tesseract**: 50-70 MB
- **Con Tesseract**: 150-170 MB

## 🚀 Distribución

Una vez creado el instalador:

1. **Firmar digitalmente** (recomendado):
```bash
signtool sign /f certificado.pfx /p password /tr http://timestamp.digicert.com ScannerSufexa_Setup_v1.0.exe
```

2. **Crear checksum** (para verificación):
```bash
certutil -hashfile ScannerSufexa_Setup_v1.0.exe SHA256 > checksum.txt
```

3. **Subir a servidor** o distribuir

## 💡 Consejos

1. **Testear en máquina virtual**: Probar instalación en Windows limpio
2. **Crear instalador silencioso**: Útil para instalaciones masivas
3. **Incluir desinstalador limpio**: Eliminar todos los archivos creados
4. **Documentar dependencias**: Listar claramente qué se necesita
5. **Versionar instaladores**: Mantener registro de cada versión

## 🔗 Referencias

- Inno Setup Docs: https://jrsoftware.org/ishelp/
- Ejemplos de Scripts: https://jrsoftware.org/ishelp/index.php?topic=scriptsamples
- Firma Digital: https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool
