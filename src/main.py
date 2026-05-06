"""
Punto de entrada principal de la aplicación Scanner Sufexa.
"""

import sys

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except ImportError:
    print("❌ Error: PySide6 no está instalado")
    sys.exit(1)


def main():
    QApplication.setApplicationName("Scanner Sufexa")
    QApplication.setOrganizationName("Scanner Sufexa")
    QApplication.setApplicationVersion("1.0")
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    try:
        from presentation.ui import MainWindow
        from presentation.controllers import AppController

        window = MainWindow()
        controller = AppController(window)

        # Detener el monitor limpiamente al cerrar la ventana
        app.aboutToQuit.connect(controller.cerrar)

        window.show()
        return app.exec()

    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
