# Interfaz de Usuario - Scanner Sufexa

## 📱 Ventana Principal

La interfaz gráfica está construida con PySide6 (Qt for Python) y proporciona una experiencia profesional e intuitiva.

### Componentes Principales

#### 1. Panel de Estado (Superior Izquierdo)
- **Estado del Monitor**: Indicador visual (●) verde/rojo
- **Carpeta Monitoreada**: Muestra la carpeta activa
- **Estadísticas en Tiempo Real**:
  - ✅ Procesados: Número de albaranes exitosos
  - ❌ Errores: Número de archivos con error
  - 📈 Tasa de Éxito: Porcentaje de éxito
- **Botones de Control**:
  - ▶ Iniciar: Inicia el monitor automático
  - ⬛ Detener: Detiene el monitor

#### 2. Ranking de Clientes (Superior Derecho)
- Tabla con top clientes por número de albaranes
- Medallas para los top 3:
  - 🥇 Primer lugar
  - 🥈 Segundo lugar
  - 🥉 Tercer lugar
- Actualización automática

#### 3. Tabs Inferiores

##### Tab "📄 Albaranes"
Tabla con todos los albaranes procesados:
- **ID**: Identificador único
- **Cliente**: Nombre del cliente
- **Número**: Número del albarán
- **Fecha**: Fecha del documento
- **Procesado**: Timestamp de procesamiento

Características:
- Colores alternados para mejor lectura
- Scroll automático al agregar nuevos
- Ordenamiento por fecha (más reciente arriba)

##### Tab "📋 Log"
Consola de eventos en tiempo real:
- **Formato**: `[HH:MM:SS] NIVEL Mensaje`
- **Niveles con colores**:
  - 🔵 INFO: Azul - Información general
  - 🟠 WARNING: Naranja - Advertencias
  - 🔴 ERROR: Rojo - Errores
  - 🟢 SUCCESS: Verde - Operaciones exitosas
  - ⚪ DEBUG: Gris - Depuración
- **Botón Limpiar**: Limpia el log
- **Auto-scroll**: Se desplaza automáticamente al último evento
- **Estilo terminal**: Fondo oscuro, fuente monoespaciada

### Barra de Menú

#### Archivo
- **⚙ Configuración (Ctrl+,)**: Abre diálogo de configuración de rutas
- **Salir (Ctrl+Q)**: Cierra la aplicación

#### Monitor
- **▶ Iniciar (Ctrl+S)**: Inicia el monitor
- **⬛ Detener (Ctrl+D)**: Detiene el monitor
- **🔄 Refrescar (F5)**: Actualiza datos

#### Ayuda
- **Acerca de...**: Información de la aplicación

## ⚙ Diálogo de Configuración

Permite configurar las rutas del sistema:

1. **Carpeta Scanner**: Carpeta donde se depositan los PDFs escaneados
2. **Carpeta Albaranes**: Carpeta base donde se organizan los albaranes por cliente
3. **Carpeta Errores**: Carpeta donde se mueven los archivos con error

Cada campo tiene un botón "📁 Buscar" para seleccionar la carpeta mediante explorador.

## 🎨 Diseño

### Paleta de Colores
- **Primario**: #007bff (Azul)
- **Éxito**: #28a745 (Verde)
- **Error**: #dc3545 (Rojo)
- **Advertencia**: #f39c12 (Naranja)
- **Fondo**: #f5f5f5 (Gris claro)
- **Texto**: #333333 (Gris oscuro)

### Tipografía
- **General**: 11pt
- **Títulos**: 16px, negrita
- **Log**: Courier New, 10pt (monoespaciada)

### Elementos Visuales
- Bordes redondeados en botones (4px)
- Sombras sutiles en paneles
- Colores alternados en tablas
- Iconos emoji para mejor UX
- Transiciones suaves en hover

## 🔄 Actualización en Tiempo Real

La interfaz se actualiza automáticamente cuando:
- Se procesa un nuevo albarán → Aparece en la tabla
- Cambian las estadísticas → Se actualizan los números
- Ocurre un evento → Se añade al log
- Se actualiza el ranking → Se reordena la tabla

## ⌨ Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl + S` | Iniciar monitor |
| `Ctrl + D` | Detener monitor |
| `Ctrl + ,` | Abrir configuración |
| `Ctrl + Q` | Salir |
| `F5` | Refrescar datos |

## 💡 Casos de Uso

### Inicio Típico
1. Abrir la aplicación
2. Verificar configuración (Archivo > Configuración)
3. Clic en "▶ Iniciar"
4. El sistema comienza a monitorear automáticamente
5. Los albaranes aparecen en la tabla conforme se procesan

### Monitoreo
- Observar el log en tiempo real para ver eventos
- Revisar la tasa de éxito en el panel de estado
- Consultar el ranking para ver clientes más activos
- Filtrar por la tabla de albaranes si se busca uno específico

### Solución de Problemas
1. Si hay errores, revisar el log (tab "📋 Log")
2. Los archivos con error aparecen con nivel ERROR (rojo)
3. Los duplicados aparecen como WARNING (naranja)
4. Detalles completos en los mensajes del log

## 🚀 Ventajas de la Interfaz

✅ **Profesional**: Diseño moderno y limpio
✅ **Intuitiva**: Controles claros y organizados
✅ **Informativa**: Toda la información relevante a la vista
✅ **Responsive**: Se adapta al tamaño de la ventana
✅ **En Tiempo Real**: Actualizaciones instantáneas
✅ **Accesible**: Atajos de teclado para poder usuarios
✅ **Visual**: Uso de colores e iconos para mejor UX
