from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QTreeWidgetItem,
)

from lupix_studio.assets.importer import import_png
from lupix_studio.assets.registry import AssetRegistry
from lupix_studio.project.creator import create_project
from lupix_studio.project.loader import LoadedProject, load_project
from lupix_studio.project.validator import validate_project
from lupix_studio.scene.creator import create_scene
from lupix_studio.scene.model import SceneResource
from lupix_studio.scene.serializer import SceneSerializer
from lupix_studio.settings.recent_projects import RecentProjectsManager
from lupix_studio.ui.asset_browser import AssetBrowser
from lupix_studio.ui.asset_inspector import (
    AssetInspector,
    load_asset_record,
)
from lupix_studio.ui.asset_preview_dialog import AssetPreviewDialog
from lupix_studio.ui.entity_inspector import EntityInspector
from lupix_studio.ui.new_project_dialog import NewProjectDialog
from lupix_studio.ui.new_scene_dialog import NewSceneDialog
from lupix_studio.ui.project_tree import ProjectTree
from lupix_studio.ui.scene_tree import SceneTree
from lupix_studio.ui.workspace import WorkspaceWidget


class MainWindow(QMainWindow):
    """Janela principal do Lupix Studio."""

    def __init__(self) -> None:
        super().__init__()

        self.current_project: LoadedProject | None = None
        self.current_scene_path: Path | None = None
        self.current_scene: SceneResource | None = None

        self.recent_projects = RecentProjectsManager()
        self.scene_serializer = SceneSerializer()

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
        scene_menu = self.menuBar().addMenu("Cena")
        assets_menu = self.menuBar().addMenu("Assets")
        help_menu = self.menuBar().addMenu("Ajuda")

        new_project_action = QAction(
            "Novo Projeto",
            self,
        )
        new_project_action.triggered.connect(
            self._on_new_project
        )

        open_project_action = QAction(
            "Abrir Projeto",
            self,
        )
        open_project_action.triggered.connect(
            self._on_open_project
        )

        exit_action = QAction(
            "Sair",
            self,
        )
        exit_action.triggered.connect(
            self.close
        )

        validate_action = QAction(
            "Validar Projeto",
            self,
        )
        validate_action.triggered.connect(
            self._validate_current_project
        )

        new_scene_action = QAction(
            "Nova Cena",
            self,
        )
        new_scene_action.triggered.connect(
            self._on_new_scene
        )

        save_scene_action = QAction(
            "Salvar Cena",
            self,
        )
        save_scene_action.triggered.connect(
            self._save_current_scene
        )

        project_view_action = QAction(
            "Voltar ao Projeto",
            self,
        )
        project_view_action.triggered.connect(
            self._show_project_view
        )

        import_sprite_action = QAction(
            "Importar PNG como Sprite",
            self,
        )
        import_sprite_action.triggered.connect(
            lambda: self._import_png(
                "sprites"
            )
        )

        import_tileset_action = QAction(
            "Importar PNG como TileSet",
            self,
        )
        import_tileset_action.triggered.connect(
            lambda: self._import_png(
                "tilesets"
            )
        )

        file_menu.addAction(
            new_project_action
        )
        file_menu.addAction(
            open_project_action
        )
        file_menu.addSeparator()
        file_menu.addAction(
            exit_action
        )

        edit_menu.addAction(
            QAction("Desfazer", self)
        )
        edit_menu.addAction(
            QAction("Refazer", self)
        )

        project_menu.addAction(
            validate_action
        )
        project_menu.addSeparator()
        project_menu.addAction(
            QAction("Executar", self)
        )
        project_menu.addAction(
            QAction("Exportar", self)
        )

        scene_menu.addAction(
            new_scene_action
        )
        scene_menu.addAction(
            save_scene_action
        )
        scene_menu.addSeparator()
        scene_menu.addAction(
            project_view_action
        )

        assets_menu.addAction(
            import_sprite_action
        )
        assets_menu.addAction(
            import_tileset_action
        )

        help_menu.addAction(
            QAction("Sobre", self)
        )

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

        self.workspace.scene_viewport.entity_selected.connect(
            self._on_viewport_entity_selected
        )

        self.workspace.scene_viewport.entity_moved.connect(
            self._on_viewport_entity_moved
        )

        self.setCentralWidget(
            self.workspace
        )

    def _create_project_dock(self) -> None:
        self.project_dock = QDockWidget(
            "Projeto",
            self,
        )

        self.left_stack = QStackedWidget()

        self.project_tree = ProjectTree()

        self.project_tree.itemDoubleClicked.connect(
            self._on_project_item_double_clicked
        )

        self.scene_tree = SceneTree()

        self.scene_tree.entity_selected.connect(
            self._on_scene_tree_entity_selected
        )

        self.scene_tree.scene_changed.connect(
            self._on_scene_changed
        )

        self.left_stack.addWidget(
            self.project_tree
        )

        self.left_stack.addWidget(
            self.scene_tree
        )

        self.project_dock.setWidget(
            self.left_stack
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

        self.inspector_stack = QStackedWidget()

        self.asset_inspector = AssetInspector()
        self.entity_inspector = EntityInspector()

        self.entity_inspector.entity_changed.connect(
            self._on_entity_inspector_changed
        )

        self.inspector_stack.addWidget(
            self.asset_inspector
        )

        self.inspector_stack.addWidget(
            self.entity_inspector
        )

        self.inspector_dock.setMinimumWidth(
            280
        )

        self.inspector_dock.setWidget(
            self.inspector_stack
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
        self.console.setReadOnly(
            True
        )
        self.console.setPlainText(
            "Lupix Studio pronto."
        )

        self.problems = QTextEdit()
        self.problems.setReadOnly(
            True
        )

        self.asset_browser = AssetBrowser()

        self.asset_browser.asset_selected.connect(
            self._show_asset_in_inspector
        )

        self.asset_browser.asset_activated.connect(
            self._activate_asset
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

        dock.setWidget(
            tabs
        )

        dock.setMinimumHeight(
            180
        )

        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            dock,
        )

    def _create_status_bar(self) -> None:
        status = QStatusBar()
        status.showMessage(
            "Pronto"
        )
        self.setStatusBar(
            status
        )

    def _on_new_project(self) -> None:
        dialog = NewProjectDialog(
            self
        )

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
            create_project(
                config
            )

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

        self._open_project(
            project
        )

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

        self._open_project(
            project
        )

    def _on_recent_project(
        self,
        path: Path,
    ) -> None:
        try:
            project = load_project(
                path
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

            self._refresh_recent_projects()
            return

        self._open_project(
            project
        )

    def _open_project(
        self,
        project: LoadedProject,
    ) -> None:
        self.current_project = project
        self.current_scene_path = None
        self.current_scene = None

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
        self.entity_inspector.clear_entity()

        self.scene_tree.set_scene(
            None
        )

        self._show_project_hierarchy()

        self.inspector_stack.setCurrentWidget(
            self.asset_inspector
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

        self._validate_current_project()

    def _on_new_scene(self) -> None:
        if self.current_project is None:
            QMessageBox.warning(
                self,
                "Nova Cena",
                "Abra um projeto primeiro.",
            )
            return

        dialog = NewSceneDialog(
            self,
            default_width=self.current_project.width,
            default_height=self.current_project.height,
        )

        if not dialog.exec():
            return

        try:
            path = create_scene(
                project_root=self.current_project.root,
                name=dialog.scene_name(),
                width=dialog.scene_width(),
                height=dialog.scene_height(),
            )

            resource = self.scene_serializer.load(
                path
            )

        except (
            OSError,
            ValueError,
            TypeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Erro ao criar cena",
                str(error),
            )
            return

        self.project_tree.load_project(
            self.current_project.root
        )

        self._open_scene(
            path,
            resource,
        )

    def _open_scene(
        self,
        path: Path,
        resource: SceneResource,
    ) -> None:
        self.current_scene_path = path.resolve()
        self.current_scene = resource

        self.scene_tree.set_scene(
            resource
        )

        self.entity_inspector.clear_entity()

        self.inspector_stack.setCurrentWidget(
            self.entity_inspector
        )

        self._show_scene_hierarchy()

        self.workspace.show_scene(
            self.current_scene_path,
            resource,
        )

        self.statusBar().showMessage(
            f"Cena aberta: {resource.name}"
        )

        if self.current_project is not None:
            self.setWindowTitle(
                f"{resource.name} - "
                f"{self.current_project.name} - "
                "Lupix Studio"
            )

    def _open_scene_file(
        self,
        path: Path,
    ) -> None:
        try:
            resource = self.scene_serializer.load(
                path
            )

        except (
            OSError,
            ValueError,
            TypeError,
        ) as error:
            QMessageBox.critical(
                self,
                "Erro ao abrir cena",
                str(error),
            )
            return

        self._open_scene(
            path,
            resource,
        )

    def _on_project_item_double_clicked(
        self,
        item: QTreeWidgetItem,
        column: int,
    ) -> None:
        del column

        value = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if not value:
            return

        path = Path(
            str(value)
        )

        if (
            path.is_file()
            and path.suffix.lower() == ".scene"
        ):
            self._open_scene_file(
                path
            )

    def _show_project_view(self) -> None:
        if self.current_project is None:
            return

        self._show_project_hierarchy()

        self.inspector_stack.setCurrentWidget(
            self.asset_inspector
        )

        self.workspace.show_project(
            self.current_project.name
        )

    def _show_project_hierarchy(self) -> None:
        self.left_stack.setCurrentWidget(
            self.project_tree
        )

        self.project_dock.setWindowTitle(
            "Projeto"
        )

    def _show_scene_hierarchy(self) -> None:
        self.left_stack.setCurrentWidget(
            self.scene_tree
        )

        self.project_dock.setWindowTitle(
            "Hierarquia"
        )

    def _on_scene_changed(self) -> None:
        if self.current_scene is None:
            return

        self.workspace.scene_viewport.refresh_entities()
        self._save_current_scene()

    def _save_current_scene(self) -> None:
        if (
            self.current_scene is None
            or self.current_scene_path is None
        ):
            return

        try:
            self.scene_serializer.save(
                self.current_scene,
                self.current_scene_path,
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "Erro ao salvar cena",
                str(error),
            )

    def _on_scene_tree_entity_selected(
        self,
        entity_id: str,
    ) -> None:
        if self.current_scene is None:
            return

        entity = self.current_scene.entity(
            entity_id
        )

        if entity is None:
            return

        self.workspace.scene_viewport.select_entity(
            entity_id
        )

        self.entity_inspector.show_entity(
            entity
        )

        self.inspector_stack.setCurrentWidget(
            self.entity_inspector
        )

    def _on_viewport_entity_selected(
        self,
        entity_id: str,
    ) -> None:
        if self.current_scene is None:
            return

        self.scene_tree.select_entity(
            entity_id
        )

        entity = self.current_scene.entity(
            entity_id
        )

        if entity is not None:
            self.entity_inspector.show_entity(
                entity
            )

    def _on_viewport_entity_moved(
        self,
        entity_id: str,
    ) -> None:
        if self.current_scene is None:
            return

        entity = self.current_scene.entity(
            entity_id
        )

        if entity is None:
            return

        self.entity_inspector.show_entity(
            entity
        )

        self._save_current_scene()

    def _on_entity_inspector_changed(
        self,
    ) -> None:
        entity = self.entity_inspector.entity

        if entity is None:
            return

        self.workspace.scene_viewport.refresh_entity(
            entity.id
        )

        self._save_current_scene()

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
            return

        self.asset_inspector.show_record(
            record
        )

        self.inspector_stack.setCurrentWidget(
            self.asset_inspector
        )

    def _activate_asset(
        self,
        path: Path,
    ) -> None:
        if self.current_project is None:
            return

        registry = AssetRegistry(
            self.current_project.root
        )

        record = registry.find_by_path(
            path
        )

        if record is None:
            return

        if record.type == "tilesets":
            self.workspace.show_tileset(
                self.current_project.root,
                record,
            )
            return

        dialog = AssetPreviewDialog(
            path,
            self,
        )

        dialog.exec()

    def _validate_current_project(
        self,
    ) -> None:
        self.problems.clear()

        if self.current_project is None:
            return

        issues = validate_project(
            self.current_project
        )

        if not issues:
            self.problems.append(
                "Projeto válido para desenvolvimento Lupi."
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

    def _refresh_recent_projects(
        self,
    ) -> None:
        projects = self.recent_projects.load()

        self.workspace.start_page.set_recent_projects(
            projects
        )