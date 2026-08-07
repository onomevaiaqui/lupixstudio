from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.project.creator import create_project
from lupix_studio.project.loader import LoadedProject, load_project
from lupix_studio.ui.new_project_dialog import NewProjectDialog
from lupix_studio.ui.project_tree import ProjectTree
from lupix_studio.ui.workspace import WorkspaceWidget


class MainWindow(QMainWindow):
    """Janela principal do Lupix Studio."""

    def __init__(self) -> None:
        super().__init__()

        self.current_project: LoadedProject | None = None

        self.setWindowTitle("Lupix Studio")
        self.resize(1440, 900)

        self._create_menu()
        self._create_workspace()
        self._create_project_dock()
        self._create_inspector_dock()
        self._create_bottom_dock()
        self._create_status_bar()

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        edit_menu = self.menuBar().addMenu("Editar")
        project_menu = self.menuBar().addMenu("Projeto")
        help_menu = self.menuBar().addMenu("Ajuda")

        new_action = QAction("Novo Projeto", self)
        new_action.triggered.connect(self._on_new_project)

        open_action = QAction("Abrir Projeto", self)
        open_action.triggered.connect(self._on_open_project)

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        edit_menu.addAction(QAction("Desfazer", self))
        edit_menu.addAction(QAction("Refazer", self))

        project_menu.addAction(QAction("Executar", self))
        project_menu.addAction(QAction("Exportar", self))

        help_menu.addAction(QAction("Sobre", self))

    def _create_workspace(self) -> None:
        self.workspace = WorkspaceWidget()

        self.workspace.start_page.new_project_requested.connect(
            self._on_new_project
        )
        self.workspace.start_page.open_project_requested.connect(
            self._on_open_project
        )

        self.setCentralWidget(self.workspace)

    def _create_project_dock(self) -> None:
        self.project_dock = QDockWidget("Projeto", self)

        self.project_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.project_tree = ProjectTree()

        self.project_dock.setWidget(self.project_tree)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.project_dock,
        )

    def _create_inspector_dock(self) -> None:
        dock = QDockWidget("Inspector", self)

        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        container = QWidget()
        layout = QVBoxLayout(container)

        self.inspector_title = QLabel(
            "Nenhum objeto selecionado"
        )

        self.inspector_title.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        layout.addWidget(self.inspector_title)
        layout.addStretch()

        dock.setMinimumWidth(260)
        dock.setWidget(container)

        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            dock,
        )

    def _create_bottom_dock(self) -> None:
        dock = QDockWidget("Saída", self)

        tabs = QTabWidget()

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlainText(
            "Lupix Studio pronto."
        )

        self.problems = QTextEdit()
        self.problems.setReadOnly(True)

        tabs.addTab(self.console, "Console")
        tabs.addTab(self.problems, "Problemas")

        dock.setWidget(tabs)
        dock.setMinimumHeight(160)

        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            dock,
        )

    def _create_status_bar(self) -> None:
        status = QStatusBar()
        status.showMessage("Pronto")
        self.setStatusBar(status)

    def _on_new_project(self) -> None:
        dialog = NewProjectDialog(self)

        if not dialog.exec():
            return

        config = dialog.project_config()

        if not config.name:
            QMessageBox.warning(
                self,
                "Novo Projeto",
                "Informe um nome para o projeto.",
            )
            return

        try:
            create_project(config)
            project = load_project(config.project_dir)
        except (OSError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Erro ao criar projeto",
                str(error),
            )
            return

        self._open_project(project)

    def _on_open_project(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Abrir Projeto Lupix",
            str(Path.home()),
        )

        if not directory:
            return

        try:
            project = load_project(Path(directory))
        except (OSError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Erro ao abrir projeto",
                str(error),
            )
            return

        self._open_project(project)

    def _open_project(
        self,
        project: LoadedProject,
    ) -> None:
        self.current_project = project

        self.project_tree.load_project(
            project.root
        )

        self.workspace.show_project(
            project.name
        )

        self.setWindowTitle(
            f"{project.name} - Lupix Studio"
        )

        self.statusBar().showMessage(
            f"Projeto aberto: {project.name}"
        )

        self.console.append(
            f"Projeto aberto: {project.root}"
        )