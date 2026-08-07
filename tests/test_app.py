from lupix_studio import __version__
from lupix_studio.ui.main_window import MainWindow


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_main_window_class_exists() -> None:
    assert MainWindow.__name__ == "MainWindow"