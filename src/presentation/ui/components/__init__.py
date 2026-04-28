"""
Componentes reutilizables de la interfaz.
"""

try:
    from .albaran_table_widget import AlbaranTableWidget
    from .ranking_widget import RankingWidget
    from .error_log_widget import ErrorLogWidget
    from .status_widget import StatusWidget
    from .config_dialog import ConfigDialog
    COMPONENTS_AVAILABLE = True
except ImportError:
    AlbaranTableWidget = None
    RankingWidget = None
    ErrorLogWidget = None
    StatusWidget = None
    ConfigDialog = None
    COMPONENTS_AVAILABLE = False

__all__ = [
    "AlbaranTableWidget",
    "RankingWidget",
    "ErrorLogWidget",
    "StatusWidget",
    "ConfigDialog",
    "COMPONENTS_AVAILABLE",
]
