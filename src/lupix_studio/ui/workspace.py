from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
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
            self.scene_viewport
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

        self.show_start_page()

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

        self.stack.setCurrentWidget(
            self.scene_viewport
        )

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