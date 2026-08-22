from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRecord
from lupix_studio.scene.model import (
    SceneEntity,
    SceneResource,
)
from lupix_studio.ui.animation_editor import (
    AnimationEditor,
)
from lupix_studio.ui.flowchart_editor import FlowchartEditor
from lupix_studio.ui.play_preview import PlayPreview
from lupix_studio.ui.scene_viewport import SceneViewport
from lupix_studio.ui.start_page import StartPage
from lupix_studio.ui.tilemap_editor import TileMapEditor
from lupix_studio.ui.tileset_editor import TileSetEditor


class ProjectPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.title = QLabel(
            "Projeto"
        )

        self.title.setObjectName(
            "ViewportTitle"
        )

        self.title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.subtitle = QLabel(
            "Nenhuma cena aberta"
        )

        self.subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout = QVBoxLayout(
            self
        )

        layout.addStretch()

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.subtitle
        )

        layout.addStretch()

    def set_project_name(
        self,
        name: str,
    ) -> None:
        self.title.setText(
            name
        )


class WorkspaceWidget(QWidget):
    tilemap_back_requested = Signal()

    animation_back_requested = Signal()

    animation_changed = Signal(
        str
    )

    play_stop_requested = Signal()
    flow_back_requested = Signal()
    flow_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.stack = QStackedWidget()

        # =========================================================
        # PÁGINAS
        # =========================================================

        self.start_page = StartPage()

        self.project_page = (
            ProjectPage()
        )

        self.scene_viewport = (
            SceneViewport()
        )

        self.tileset_editor = (
            TileSetEditor()
        )

        self.tilemap_editor = (
            TileMapEditor()
        )

        self.animation_editor = (
            AnimationEditor()
        )

        self.play_preview = (
            PlayPreview()
        )
        self.flow_editor = FlowchartEditor()
        self.script_editor: QWidget | None = None

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setObjectName("MainEditorTabs")
        self.editor_tabs.addTab(self.scene_viewport, "Editor")
        self.editor_tabs.addTab(self.flow_editor, "Flowchart")

        # =========================================================
        # STACK
        # =========================================================

        self.stack.addWidget(
            self.start_page
        )

        self.stack.addWidget(
            self.project_page
        )

        self.stack.addWidget(
            self.editor_tabs
        )

        self.stack.addWidget(
            self.tileset_editor
        )

        self.stack.addWidget(
            self.tilemap_editor
        )

        self.stack.addWidget(
            self.animation_editor
        )

        self.stack.addWidget(
            self.play_preview
        )

        # =========================================================
        # LAYOUT
        # =========================================================

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.addWidget(
            self.stack
        )

        # =========================================================
        # TILEMAP
        # =========================================================

        self.tilemap_editor.back_requested.connect(
            self.tilemap_back_requested.emit
        )

        # =========================================================
        # ANIMATION EDITOR
        # =========================================================

        self.animation_editor.back_requested.connect(
            self.animation_back_requested.emit
        )

        self.animation_editor.animation_changed.connect(
            self.animation_changed.emit
        )

        # =========================================================
        # PLAY
        # =========================================================

        self.play_preview.stop_requested.connect(
            self.play_stop_requested.emit
        )
        self.flow_editor.back_requested.connect(self.flow_back_requested.emit)
        self.flow_editor.flow_changed.connect(self.flow_changed.emit)

        self.show_start_page()

    def set_script_editor(self, editor: QWidget) -> None:
        self.script_editor = editor

    def configure_development_mode(self, mode: str) -> None:
        # Recria somente as abas centrais; os editores continuam vivos.
        while self.editor_tabs.count():
            self.editor_tabs.removeTab(0)

        self.editor_tabs.addTab(self.scene_viewport, "Editor")

        if mode in {"blueprint", "blueprint_script"}:
            self.editor_tabs.addTab(self.flow_editor, "Flowchart")

        if mode in {"script", "blueprint_script"} and self.script_editor is not None:
            self.editor_tabs.addTab(self.script_editor, "Script")

    def set_flow_entity(self, entity: SceneEntity) -> None:
        self.flow_editor.open_flow(entity)

    def show_script(self) -> None:
        if self.script_editor is None:
            return
        index = self.editor_tabs.indexOf(self.script_editor)
        if index < 0:
            return
        self.editor_tabs.setCurrentIndex(index)
        self.stack.setCurrentWidget(self.editor_tabs)

    # =============================================================
    # START
    # =============================================================

    def show_start_page(
        self,
    ) -> None:
        self.stack.setCurrentWidget(
            self.start_page
        )

    # =============================================================
    # PROJECT
    # =============================================================

    def show_project(
        self,
        name: str,
    ) -> None:
        self.project_page.set_project_name(
            name
        )

        self.stack.setCurrentWidget(
            self.project_page
        )

    # =============================================================
    # SCENE
    # =============================================================

    def show_scene(
        self,
        project_root: Path,
        resource: SceneResource,
    ) -> None:
        self.scene_viewport.open_scene(
            project_root,
            resource,
        )
        self.flow_editor.set_project_root(project_root)

        self.editor_tabs.setCurrentWidget(self.scene_viewport)
        self.stack.setCurrentWidget(self.editor_tabs)

    # =============================================================
    # TILESET
    # =============================================================

    def show_tileset(
        self,
        project_root: Path,
        asset_record: AssetRecord,
    ) -> None:
        self.tileset_editor.open_tileset(
            project_root,
            asset_record,
        )

        self.stack.setCurrentWidget(
            self.tileset_editor
        )

    # =============================================================
    # TILEMAP
    # =============================================================

    def show_tilemap(
        self,
        project_root: Path,
        resource_path: Path,
    ) -> None:
        self.tilemap_editor.open_tilemap(
            project_root,
            resource_path,
        )

        self.stack.setCurrentWidget(
            self.tilemap_editor
        )

    # =============================================================
    # ANIMATION
    # =============================================================

    def show_animation(
        self,
        project_root: Path,
        entity: SceneEntity,
        clip_name: str | None = None,
    ) -> None:
        self.animation_editor.open_animation(
            project_root,
            entity,
            clip_name,
        )

        self.stack.setCurrentWidget(
            self.animation_editor
        )

    def show_lupix_flow(self, entity: SceneEntity) -> None:
        index = self.editor_tabs.indexOf(self.flow_editor)
        if index < 0:
            return
        self.flow_editor.open_flow(entity)
        self.editor_tabs.setCurrentIndex(index)
        self.stack.setCurrentWidget(self.editor_tabs)

    # =============================================================
    # PLAY
    # =============================================================

    def show_play_preview(
        self,
        project_root: Path,
        resource: SceneResource,
    ) -> None:
        self.play_preview.start(
            project_root,
            resource,
        )

        self.stack.setCurrentWidget(
            self.play_preview
        )

    def stop_play_preview(
        self,
    ) -> None:
        self.play_preview.stop_runtime()