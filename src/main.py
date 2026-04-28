"""
Punto de entrada principal de la aplicación Scanner Sufexa.

Este es el script que se ejecuta al iniciar el programa.
"""

import sys
from pathlib import Path

# Verificar que PySide6 esté disponible
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("❌ Error: PySide6 no está instalado")
    print("\nPara instalar PySide6:")
    print("  pip install PySide6")
    sys.exit(1)


def main():
    """Función principal de la aplicación."""
    # Configurar aplicación Qt
    QApplication.setApplicationName("Scanner Sufexa")
    QApplication.setOrganizationName("Scanner Sufexa")
    QApplication.setApplicationVersion("1.0")

    # Habilitar High DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Crear aplicación
    app = QApplication(sys.argv)

    # Importar ventana principal
    try:
        from presentation.ui import MainWindow

        # Crear y mostrar ventana
        window = MainWindow()
        window.show()

        # TODO: Aquí se conectaría el controlador real
        # Por ahora, solo mostramos la ventana
        window.log_info("Sistema iniciado")
        window.log_info("Esperando configuración...")

        # Ejecutar loop de eventos
        return app.exec()

    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
