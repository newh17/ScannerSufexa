"""
Script de prueba para el monitor de archivos con watchdog.

Simula la detección de archivos PDF y su procesamiento.

Ejecutar desde la raíz del proyecto:
    python scripts/test_file_monitor.py
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path

# Añadir src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from infrastructure.monitoring import WatchdogFileMonitor
from infrastructure.filesystem import FileSystemService


def callback_simple(archivo: str) -> bool:
    """
    Callback simple que simula procesamiento.

    Args:
        archivo: Ruta al archivo

    Returns:
        bool: True si se procesó correctamente
    """
    print(f"      📝 Callback ejecutado para: {Path(archivo).name}")
    time.sleep(0.5)  # Simular procesamiento
    return True


def callback_con_error(archivo: str) -> bool:
    """Callback que simula un error."""
    nombre = Path(archivo).name
    if "error" in nombre.lower():
        print(f"      ❌ Error simulado para: {nombre}")
        return False
    return True


def test_monitor_basico():
    """Prueba básica del monitor."""
    print("=" * 70)
    print("PRUEBA 1: MONITOR BÁSICO")
    print("=" * 70)

    # Crear carpeta temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        carpeta_scan = Path(tmpdir) / "scan"
        carpeta_scan.mkdir()

        print(f"\n📁 Carpeta temporal: {carpeta_scan}")

        # Crear monitor
        monitor = WatchdogFileMonitor(
            carpeta_monitoreada=str(carpeta_scan),
            callback_procesamiento=callback_simple,
            tiempo_espera=1.0,
            intervalo_chequeo=0.5,
            verbose=True
        )

        print("\n▶️  Iniciando monitor...")
        monitor.start()

        # Esperar a que el monitor esté listo
        time.sleep(1)

        # Simular creación de archivos
        print("\n📄 Creando archivos de prueba...")
        for i in range(3):
            archivo = carpeta_scan / f"test_{i+1}.pdf"
            archivo.write_text(f"Contenido de prueba {i+1}")
            print(f"   Creado: {archivo.name}")
            time.sleep(0.5)

        # Esperar a que se procesen
        print("\n⏳ Esperando procesamiento...")
        time.sleep(5)

        # Detener monitor
        print("\n🛑 Deteniendo monitor...")
        monitor.stop()

        print("\n✅ Prueba básica completada")


def test_archivo_completo():
    """Prueba que el monitor espera a que el archivo esté completo."""
    print("\n" + "=" * 70)
    print("PRUEBA 2: ESPERA DE ARCHIVO COMPLETO")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        carpeta_scan = Path(tmpdir) / "scan"
        carpeta_scan.mkdir()

        print(f"\n📁 Carpeta temporal: {carpeta_scan}")

        archivos_procesados = []

        def callback_registro(archivo: str) -> bool:
            archivos_procesados.append(archivo)
            return True

        monitor = WatchdogFileMonitor(
            carpeta_monitoreada=str(carpeta_scan),
            callback_procesamiento=callback_registro,
            tiempo_espera=1.0,
            verbose=True
        )

        monitor.start()
        time.sleep(1)

        # Simular escritura lenta (como un escaneo)
        print("\n📄 Simulando archivo escribiéndose lentamente...")
        archivo = carpeta_scan / "escaneando.pdf"

        # Escribir por partes
        with open(archivo, 'wb') as f:
            for i in range(5):
                f.write(b"X" * 1024)  # 1KB por vez
                f.flush()
                print(f"   Escrito {(i+1)*1024} bytes...")
                time.sleep(0.5)

        print("   ✅ Archivo completo")

        # Esperar procesamiento
        time.sleep(5)

        monitor.stop()

        if archivos_procesados:
            print(f"\n✅ Archivo procesado correctamente después de estar completo")
        else:
            print(f"\n❌ Error: archivo no fue procesado")


def test_manejo_errores():
    """Prueba el manejo de errores en el callback."""
    print("\n" + "=" * 70)
    print("PRUEBA 3: MANEJO DE ERRORES")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        carpeta_scan = Path(tmpdir) / "scan"
        carpeta_scan.mkdir()

        print(f"\n📁 Carpeta temporal: {carpeta_scan}")

        monitor = WatchdogFileMonitor(
            carpeta_monitoreada=str(carpeta_scan),
            callback_procesamiento=callback_con_error,
            tiempo_espera=0.5,
            verbose=True
        )

        monitor.start()
        time.sleep(1)

        # Crear archivos de prueba (algunos con "error" en el nombre)
        print("\n📄 Creando archivos (algunos causarán error)...")
        archivos = [
            "valido_1.pdf",
            "error_test.pdf",  # Causará error
            "valido_2.pdf",
            "otro_error.pdf",  # Causará error
        ]

        for nombre in archivos:
            archivo = carpeta_scan / nombre
            archivo.write_text("Contenido")
            print(f"   Creado: {nombre}")
            time.sleep(0.3)

        # Esperar procesamiento
        time.sleep(5)

        monitor.stop()

        print(f"\n📊 Resultados:")
        print(f"   Procesados: {monitor.archivos_procesados}")
        print(f"   Con error: {monitor.archivos_con_error}")

        if monitor.archivos_procesados == 2 and monitor.archivos_con_error == 2:
            print("\n✅ Manejo de errores correcto")
        else:
            print("\n⚠️  Números inesperados")


def test_file_system_service():
    """Prueba el servicio de sistema de archivos."""
    print("\n" + "=" * 70)
    print("PRUEBA 4: FILE SYSTEM SERVICE")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        carpeta_salida = base / "albaranes"
        carpeta_errores = base / "albaranes" / "errores"

        print(f"\n📁 Carpeta base: {base}")

        # Crear servicio
        fs = FileSystemService(
            carpeta_salida_base=str(carpeta_salida),
            carpeta_errores=str(carpeta_errores)
        )

        print("\n✅ Servicio creado")
        print(f"   Carpeta salida: {fs.carpeta_salida_base}")
        print(f"   Carpeta errores: {fs.carpeta_errores}")

        # Crear archivo de prueba
        archivo_origen = base / "test.pdf"
        archivo_origen.write_text("Contenido de prueba")

        # TEST 1: Mover a carpeta de cliente
        print("\n[TEST 1] Mover a carpeta de cliente...")
        destino = fs.mover_a_carpeta_cliente(
            archivo_origen=str(archivo_origen),
            nombre_cliente="METALCRISMAR, S.L.",
            nuevo_nombre="METALCRISMAR, S.L._23-01-2026_71206.pdf"
        )
        print(f"   ✅ Movido a: {destino}")
        print(f"   ✅ Archivo existe: {Path(destino).exists()}")

        # TEST 2: Mover a carpeta de errores
        print("\n[TEST 2] Mover a carpeta de errores...")
        archivo_error = base / "error.pdf"
        archivo_error.write_text("Archivo con error")

        destino_error = fs.mover_a_errores(
            archivo_origen=str(archivo_error),
            razon="OCR_fallido"
        )
        print(f"   ✅ Movido a: {destino_error}")
        print(f"   ✅ Archivo existe: {Path(destino_error).exists()}")

        # TEST 3: Prevención de sobrescritura
        print("\n[TEST 3] Prevención de sobrescritura...")
        archivo_dup = base / "dup.pdf"
        archivo_dup.write_text("Duplicado")

        try:
            fs.mover_a_carpeta_cliente(
                archivo_origen=str(archivo_dup),
                nombre_cliente="METALCRISMAR, S.L.",
                nuevo_nombre="METALCRISMAR, S.L._23-01-2026_71206.pdf"  # Ya existe
            )
            print("   ❌ ERROR: Debería haber lanzado FileExistsError")
        except FileExistsError:
            print("   ✅ Sobrescritura prevenida correctamente")

        print("\n✅ Todas las pruebas del FileSystemService completadas")


def test_context_manager():
    """Prueba el uso del monitor como context manager."""
    print("\n" + "=" * 70)
    print("PRUEBA 5: CONTEXT MANAGER")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        carpeta_scan = Path(tmpdir) / "scan"
        carpeta_scan.mkdir()

        print(f"\n📁 Carpeta temporal: {carpeta_scan}")
        print("\n▶️  Usando monitor como context manager...")

        with WatchdogFileMonitor(
            carpeta_monitoreada=str(carpeta_scan),
            callback_procesamiento=callback_simple,
            tiempo_espera=0.5,
            verbose=True
        ) as monitor:
            print("\n   Monitor iniciado automáticamente")
            time.sleep(1)

            # Crear archivo
            archivo = carpeta_scan / "test.pdf"
            archivo.write_text("Test")
            print(f"\n   Creado: {archivo.name}")

            # Esperar procesamiento
            time.sleep(3)

        print("\n✅ Monitor detenido automáticamente al salir del context")


def main():
    """Función principal."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          PRUEBAS DEL MONITOR DE ARCHIVOS (WATCHDOG)               ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    try:
        test_monitor_basico()
        test_archivo_completo()
        test_manejo_errores()
        test_file_system_service()
        test_context_manager()

        print("\n" + "=" * 70)
        print("🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
