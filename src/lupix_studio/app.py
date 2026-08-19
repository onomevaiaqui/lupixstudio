import logging
import sys

from PySide6.QtWidgets import QApplication

from lupix_studio.core.logging import configure_logging
from lupix_studio.settings.manager import SettingsManager
from lupix_studio.ui.main_window import MainWindow
from lupix_studio.ui.styles import (
    install_checkbox_style,
)
from lupix_studio.ui.theme.dark import DARK_STYLESHEET


def create_application() -> QApplication:
    """Cria ou retorna a aplicação Qt."""
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    install_checkbox_style(
        app
    )

    app.setApplicationName("Lupix Studio")
    app.setOrganizationName("Lupix")

    return app


def main() -> int:
    """Ponto de entrada do Lupix Studio."""
    configure_logging()
    logger = logging.getLogger("lupix_studio")

    settings = SettingsManager().load()

    logger.info("Lupix Studio iniciando")
    logger.info("Tema: %s", settings.theme)
    logger.info("Idioma: %s", settings.language)

    app = create_application()

    app.setStyleSheet(DARK_STYLESHEET)

    window = MainWindow()
    window.showMaximized()

    exit_code = app.exec()

    logger.info("Lupix Studio encerrado")

    return exit_code