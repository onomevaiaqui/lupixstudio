from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QTextEdit,
)

from lupix_studio.assets.importer import import_png
from lupix_studio.project.creator import create_project
from lupix_studio.project.loader import LoadedProject, load_project
from lupix_studio.project.validator import validate_project
from lupix_studio.settings.recent_projects import RecentProjectsManager
from lupix_studio.ui.asset_browser import AssetBrowser
from lupix_studio.ui.asset_inspector import (
    AssetInspector,
    load_asset_record,
)
from lupix_studio.ui.asset_preview_dialog import AssetPreviewDialog
from lupix_studio.ui.new_project_dialog import NewProjectDialog
from lupix_studio.ui.project_tree import ProjectTree
from lupix_studio.ui.workspace import WorkspaceWidget


class MainWindow(QMainWindow):
    """Janela principal do Lupix Studio."""

    def __init__(self) -> None:
        super().__init__()

        self.current_project: LoadedProject | None = None
        self.recent_projects = RecentProjectsManager()

        self.setWindowTitle("Lupix Studio")
        self.resize(1440, 900)

        self._create_menu()
        self._create_workspace()
        self._create_project_dock()
        self._create_inspector_dock()
        self._create_bottom_dock()
        self._create_status_bar()

        self._refresh_recent_projects()

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        edit_menu = self.menuBar().addMenu("Editar")
        project_menu = self.menuBar().addMenu("Projeto")
        assets_menu = self.menuBar().addMenu("Assets")
        help_menu = self.menuBar().addMenu("Ajuda")

        new_action = QAction("Novo Projeto", self)
        new_action.triggered.connect(self._on_new_project)

        open_action = QAction("Abrir Projeto", self)
        open_action.triggered.connect(self._on_open_project)

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)

        validate_action = QAction(
            "Validar Projeto",
            self,
        )
        validate_action.triggered.connect(
            self._validate_current_project
        )

        import_sprite_action = QAction(
            "Importar PNG como Sprite",
            self,
        )
        import_sprite_action.triggered.connect(
            lambda: self._import_png("sprites")
        )

        import_tileset_action = QAction(
            "Importar PNG como TileSet",
            self,
        )
        import_tileset_action.triggered.connect(
            lambda: self._import_png("tilesets")
        )

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        edit_menu.addAction(QAction("Desfazer", self))
        edit_menu.addAction(QAction("Refazer", self))

        project_menu.addAction(validate_action)
        project_menu.addSeparator()
        project_menu.addAction(QAction("Executar", self))
        project_menu.addAction(QAction("Exportar", self))

        assets_menu.addAction(import_sprite_action)
        assets_menu.addAction(import_tileset_action)

        help_menu.addAction(QAction("Sobre", self))

    def _create_workspace(self) -> None:
        self.workspace = WorkspaceWidget()

        self.workspace.start_page.new_project_requested.connect(
            self._on_new_project
        )

        self.workspace.start_page.open_project_requested.connect(
            self._on_open_project
        )

        self.workspace.start_page.recent_project_requested.connect(
            self._on_recent_project
        )

        self.setCentralWidget(self.workspace)

    def _create_project_dock(self) -> None:
        self.project_dock = QDockWidget(
            "Projeto",
            self,
        )

        self.project_tree = ProjectTree()

        self.project_dock.setWidget(
            self.project_tree
        )

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.project_dock,
        )

    def _create_inspector_dock(self) -> None:
        self.inspector_dock = QDockWidget(
            "Inspector",
            self,
        )

        self.asset_inspector = AssetInspector()

        self.inspector_dock.setMinimumWidth(280)
        self.inspector_dock.setWidget(
            self.asset_inspector
        )

        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.inspector_dock,
        )

    def _create_bottom_dock(self) -> None:
        dock = QDockWidget(
            "Saída",
            self,
        )

        tabs = QTabWidget()

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlainText(
            "Lupix Studio pronto."
        )

        self.problems = QTextEdit()
        self.problems.setReadOnly(True)

        self.asset_browser = AssetBrowser()

        self.asset_browser.asset_selected.connect(
            self._show_asset_in_inspector
        )

        self.asset_browser.asset_activated.connect(
            self._show_asset_preview
        )

        tabs.addTab(
            self.console,
            "Console",
        )

        tabs.addTab(
            self.problems,
            "Problemas",
        )

        tabs.addTab(
            self.asset_browser,
            "Assets",
        )

        dock.setWidget(tabs)
        dock.setMinimumHeight(180)

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
            project = load_project(
                config.project_dir
            )
        except (
            OSError,
            ValueError,
            TypeError,
        ) as error:
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
            project = load_project(
                Path(directory)
            )
        except (
            OSError,
            ValueError,
            TypeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Erro ao abrir projeto",
                str(error),
            )
            return

        self._open_project(project)

    def _on_recent_project(
        self,
        path: Path,
    ) -> None:
        try:
            project = load_project(path)
        except (
            OSError,
            ValueError,
            TypeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Erro ao abrir projeto",
                str(error),
            )

            self._refresh_recent_projects()
            return

        self._open_project(project)

    def _open_project(
        self,
        project: LoadedProject,
    ) -> None:
        self.current_project = project

        self.recent_projects.add(
            project.root
        )

        self._refresh_recent_projects()

        self.project_tree.load_project(
            project.root
        )

        self.asset_browser.load_project(
            project.root
        )

        self.asset_inspector.clear_asset()

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

        self._validate_current_project()

    def _import_png(
        self,
        asset_type: str,
    ) -> None:
        if self.current_project is None:
            QMessageBox.warning(
                self,
                "Importar Asset",
                "Abra um projeto primeiro.",
            )
            return

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Importar PNG",
            str(Path.home()),
            "PNG (*.png)",
        )

        if not filename:
            return

        try:
            imported = import_png(
                Path(filename),
                self.current_project.root,
                asset_type,
            )
        except (
            OSError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Erro ao importar",
                str(error),
            )
            return

        self.project_tree.load_project(
            self.current_project.root
        )

        self.asset_browser.refresh()

        self.console.append(
            f"Asset importado: {imported.destination}"
        )

        for issue in imported.issues:
            prefix = (
                "ERRO"
                if issue.level == "error"
                else "AVISO"
            )

            self.problems.append(
                f"[{prefix}] "
                f"{imported.destination.name}: "
                f"{issue.message}"
            )

        self.statusBar().showMessage(
            f"Asset importado: {imported.destination.name}"
        )

    def _show_asset_in_inspector(
        self,
        path: Path,
    ) -> None:
        if self.current_project is None:
            return

        record = load_asset_record(
            self.current_project.root,
            path,
        )

        if record is None:
            self.asset_inspector.clear_asset()
            return

        self.asset_inspector.show_record(
            record
        )

    def _show_asset_preview(
        self,
        path: Path,
    ) -> None:
        dialog = AssetPreviewDialog(
            path,
            self,
        )

        dialog.exec()

    def _validate_current_project(self) -> None:
        self.problems.clear()

        if self.current_project is None:
            self.problems.append(
                "Nenhum projeto aberto."
            )
            return

        issues = validate_project(
            self.current_project
        )

        if not issues:
            self.problems.append(
                "Projeto válido para desenvolvimento Lupi."
            )

            self.statusBar().showMessage(
                "Projeto válido"
            )
            return

        for issue in issues:
            prefix = (
                "ERRO"
                if issue.level == "error"
                else "AVISO"
            )

            self.problems.append(
                f"[{prefix}] {issue.message}"
            )

    def _refresh_recent_projects(self) -> None:
        projects = self.recent_projects.load()

        self.workspace.start_page.set_recent_projects(
            projects
        )