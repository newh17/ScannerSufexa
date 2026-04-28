# PROYECTO: Automatización de Albaranes (Windows + OCR + DDD)

## CONTEXTO GENERAL

Quiero desarrollar una aplicación de escritorio para Windows, preparada para producción real, que procese automáticamente PDFs escaneados de albaranes.

La aplicación debe:
- Monitorizar una carpeta de entrada (scanner)
- Procesar automáticamente PDFs nuevos
- Aplicar OCR
- Extraer datos (cliente, fecha, número)
- Renombrar el archivo
- Guardarlo en la carpeta del cliente
- Registrar todo en base de datos
- Generar ranking de clientes

⚠️ IMPORTANTE:
- SOLO soporta un formato concreto de albarán
- No es genérico
- Código profesional, mantenible, arquitectura DDD
- Preparado para generar .exe

---

## FORMATO DEL ALBARÁN

Campos a extraer:

- Cliente: METALCRISMAR, S.L.
- Fecha: campo "Data" → 23/01/2026
- Número: campo "Albarà núm." → 71206

---

## FORMATO DE ARCHIVO

Nombre final:
CLIENTE_FECHA_NUMERO.pdf

Ejemplo:
METALCRISMAR, S.L_23-01-2026_71206.pdf

---

## CARPETAS

Entrada (scanner):
C:\scan\entrada\

Salida:
C:\albaranes\CLIENTE\archivo.pdf

Errores:
C:\albaranes\errores\

---

## TECNOLOGÍAS

- Python
- PySide6 (GUI)
- Tesseract OCR
- SQLite
- watchdog (monitor carpeta)
- PyInstaller (.exe)

---

# 🔥 FORMA DE TRABAJO (MUY IMPORTANTE)

Trabajaremos en FASES.

❌ NO generes todo de golpe  
❌ NO hagas código monolítico  
❌ NO simplifiques  

✔️ Responde SOLO a la fase actual  
✔️ Piensa como programador senior  
✔️ Justifica decisiones técnicas  

---

# 🧩 FASE 1 — ARQUITECTURA

OBJETIVO:
Diseñar la arquitectura completa del sistema usando DDD.

QUIERO:
- Explicación clara de las capas:
  - Domain
  - Application
  - Infrastructure
  - Presentation
- Entidades y Value Objects
- Casos de uso
- Flujo completo desde PDF → sistema
- Decisiones técnicas justificadas

⚠️ NO escribir código aún

---

# 🧩 FASE 2 — ESTRUCTURA DEL PROYECTO

OBJETIVO:
Definir estructura real de carpetas y módulos.

QUIERO:
- Árbol de directorios completo
- Separación clara por capas DDD
- Nombres de archivos realistas
- Preparado para escalar

⚠️ Aún sin implementar lógica

---

# 🧩 FASE 3 — DOMAIN + BASE DE DATOS

OBJETIVO:
Implementar núcleo del dominio.

QUIERO:
- Entidades:
  - Albaran
  - Cliente
- Value Objects:
  - Fecha
  - NumeroAlbaran
- Interfaces de repositorio
- Modelo SQLite
- Prevención de duplicados

✔️ Código limpio y modular

---

# 🧩 FASE 4 — OCR + EXTRACCIÓN

OBJETIVO:
Procesar PDFs y extraer datos.

QUIERO:
- Conversión PDF → imagen
- Integración Tesseract
- Normalización texto
- Extracción:
  - Cliente
  - Fecha
  - Número
- Regex + heurísticas específicas
- Manejo errores OCR

---

# 🧩 FASE 5 — WATCHER (CARPETA SCANNER)

OBJETIVO:
Automatización total.

QUIERO:
- Monitor de carpeta con watchdog
- Detección de nuevos PDFs
- Espera a archivo completo
- Cola de procesamiento
- Manejo de errores

---

# 🧩 FASE 6 — PROCESAMIENTO COMPLETO

OBJETIVO:
Pipeline completo.

QUIERO:
- Integración:
  OCR → extracción → validación → guardado
- Renombrado seguro
- Creación carpetas cliente
- Manejo de errores (/errores/)
- Logs

---

# 🧩 FASE 7 — INTERFAZ (PySide6)

OBJETIVO:
Interfaz profesional.

QUIERO:
- Estado del sistema
- Lista de documentos
- Errores
- Ranking clientes
- Configuración rutas

---

# 🧩 FASE 8 — GENERACIÓN .EXE

OBJETIVO:
App instalable.

QUIERO:
- PyInstaller config
- Comando exacto
- Incluir Tesseract
- Dependencias
- Ejecutable final

---

# 🧩 FASE 9 — MEJORAS

OBJETIVO:
Evolución futura.

QUIERO:
- Ideas realistas de mejora
- Escalabilidad
- Mejoras OCR
- Posible IA

---

# 🚀 INSTRUCCIÓN DE INICIO

Empieza por FASE 1.

NO avances a la siguiente fase hasta que te lo indique.
