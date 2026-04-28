"""
Demo de la interfaz gráfica.

Muestra la ventana principal con datos simulados.

NOTA: Requiere PySide6 instalado:
    pip install PySide6

Ejecutar desde la raíz del proyecto:
    python scripts/demo_interfaz.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Añadir src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Verificar PySide6
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("❌ Error: PySide6 no está instalado")
    print("\n📦 Para instalar PySide6:")
    print("   pip install PySide6")
    print("\n💡 O instala todas las dependencias:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

from presentation.ui import MainWindow


class DemoController:
    """Controlador de demo que simula datos."""

    def __init__(self, window: MainWindow):
        self.window = window
        self.procesados = 0
        self.errores = 0
        self.setup_timers()

    def setup_timers(self):
        """Configura timers para simular procesamiento."""
        # Timer para simular albaranes cada 3 segundos
        self.timer_albaranes = QTimer()
        self.timer_albaranes.timeout.connect(self.simular_albaran)
        self.timer_albaranes.setInterval(3000)

        # Timer para actualizar ranking cada 5 segundos
        self.timer_ranking = QTimer()
        self.timer_ranking.timeout.connect(self.actualizar_ranking)
        self.timer_ranking.setInterval(5000)

    def iniciar_monitor(self):
        """Simula inicio del monitor."""
        self.window.actualizar_estado_monitor(True)
        self.window.actualizar_carpeta("C:\\scan\\entrada")
        self.window.log_success("Monitor iniciado correctamente")
        self.timer_albaranes.start()
        self.timer_ranking.start()

    def detener_monitor(self):
        """Simula detención del monitor."""
        self.window.actualizar_estado_monitor(False)
        self.window.log_warning("Monitor detenido")
        self.timer_albaranes.stop()
        self.timer_ranking.stop()

    def simular_albaran(self):
        """Simula el procesamiento de un albarán."""
        import random

        clientes = [
            "METALCRISMAR, S.L.",
            "EMPRESA EJEMPLO S.A.",
            "TEST INDUSTRIAS S.L.U.",
            "COMERCIAL XYZ S.L.",
            "DISTRIBUCIONES ABC S.A.",
        ]

        # 80% de éxito, 20% de error
        if random.random() < 0.8:
            # Éxito
            self.procesados += 1
            id_albaran = self.procesados
            cliente = random.choice(clientes)
            numero = 70000 + id_albaran
            fecha = "23/01/2026"
            fecha_proc = datetime.now() - timedelta(seconds=random.randint(0, 60))

            self.window.agregar_albaran(
                id_albaran, cliente, numero, fecha, fecha_proc
            )
            self.window.log_success(
                f"Procesado: {cliente} | #{numero} | {fecha}"
            )
        else:
            # Error
            self.errores += 1
            razon = random.choice([
                "Duplicado",
                "OCR fallido",
                "Datos inválidos",
                "Archivo corrupto"
            ])
            self.window.log_error(f"Error: {razon}")

        # Actualizar estadísticas
        self.window.actualizar_estadisticas(self.procesados, self.errores)

    def actualizar_ranking(self):
        """Actualiza el ranking con datos simulados."""
        ranking = [
            ("METALCRISMAR, S.L.", 45),
            ("EMPRESA EJEMPLO S.A.", 32),
            ("TEST INDUSTRIAS S.L.U.", 28),
            ("COMERCIAL XYZ S.L.", 15),
            ("DISTRIBUCIONES ABC S.A.", 12),
            ("SUMINISTROS DEL NORTE S.L.", 8),
            ("TECNOLOGÍA AVANZADA S.A.", 5),
        ]

        self.window.actualizar_ranking(ranking)

    def cargar_datos_iniciales(self):
        """Carga datos iniciales en la interfaz."""
        self.window.log_info("Sistema iniciado")
        self.window.log_info("Base de datos conectada")
        self.window.log_info("Esperando configuración...")

        # Ranking inicial
        self.actualizar_ranking()

        # Algunos albaranes de ejemplo
        clientes_ejemplo = [
            "METALCRISMAR, S.L.",
            "EMPRESA EJEMPLO S.A.",
            "TEST INDUSTRIAS S.L.U.",
        ]

        fecha_base = datetime.now() - timedelta(hours=2)

        for i, cliente in enumerate(clientes_ejemplo, 1):
            self.procesados += 1
            self.window.agregar_albaran(
                i,
                cliente,
                70000 + i,
                "23/01/2026",
                fecha_base + timedelta(minutes=i*5)
            )

        self.window.actualizar_estadisticas(self.procesados, self.errores)


def main():
    """Función principal."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║              DEMO: INTERFAZ GRÁFICA - Scanner Sufexa              ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")

    # Crear aplicación
    app = QApplication(sys.argv)

    # Crear ventana
    window = MainWindow()

    # Crear controlador de demo
    controller = DemoController(window)

    # Conectar señales
    window.start_monitor.connect(controller.iniciar_monitor)
    window.stop_monitor.connect(controller.detener_monitor)
    window.config_changed.connect(
        lambda cfg: window.log_info(f"Configuración actualizada: {cfg['scanner']}")
    )
    window.refresh_requested.connect(
        lambda: window.log_info("Refrescando datos...")
    )

    # Cargar datos iniciales
    controller.cargar_datos_iniciales()

    # Mostrar ventana
    window.show()

    print("✅ Interfaz iniciada")
    print("\n💡 CONTROLES:")
    print("   - Clic en '▶ Iniciar' para simular procesamiento automático")
    print("   - Menú 'Archivo > Configuración' para cambiar rutas")
    print("   - Tabs inferiores para ver albaranes y logs")
    print("   - F5 para refrescar")
    print("\n🎨 CARACTERÍSTICAS:")
    print("   ✅ Interfaz profesional con PySide6")
    print("   ✅ Estado del sistema en tiempo real")
    print("   ✅ Tabla de albaranes procesados")
    print("   ✅ Ranking de clientes con medallas")
    print("   ✅ Log de eventos con colores")
    print("   ✅ Diálogo de configuración")
    print("\n")

    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
