from lupix_studio import __version__
from lupix_studio.ui.main_window import MainWindow
from lupix_studio.ui.project_tree import ProjectTree
from lupix_studio.ui.workspace import WorkspaceWidget


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_main_window_class_exists() -> None:
    assert MainWindow.__name__ == "MainWindow"


def test_workspace_class_exists() -> None:
    assert WorkspaceWidget.__name__ == "WorkspaceWidget"


def test_project_tree_class_exists() -> None:
    assert ProjectTree.__name__ == "ProjectTree"