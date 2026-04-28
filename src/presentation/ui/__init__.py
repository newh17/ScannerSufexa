"""
Interfaz de usuario con PySide6.
"""

# Los imports de PySide6 pueden fallar si no está instalado
try:
    from .main_window import MainWindow
    PYSIDE6_AVAILABLE = True
except ImportError:
    MainWindow = None
    PYSIDE6_AVAILABLE = False

__all__ = [
    "MainWindow",
    "PYSIDE6_AVAILABLE",
]
