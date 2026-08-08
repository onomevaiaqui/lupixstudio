from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRecord
from lupix_studio.scene.model import SceneResource
from lupix_studio.ui.scene_viewport import SceneViewport
from lupix_studio.ui.start_page import StartPage
from lupix_studio.ui.tileset_editor import TileSetEditor


class ProjectPage(QWidget):
    """Área principal de um projeto aberto."""

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

        layout = QVBoxLayout(self)

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

        self.subtitle.setText(
            "Nenhuma cena aberta"
        )


class WorkspaceWidget(QWidget):
    """Área central da IDE."""

    def __init__(self) -> None:
        super().__init__()

        self.stack = QStackedWidget()

        self.start_page = StartPage()
        self.project_page = ProjectPage()
        self.scene_viewport = SceneViewport()
        self.tileset_editor = TileSetEditor()

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

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.addWidget(
            self.stack
        )

        self.show_start_page()

    def show_start_page(
        self,
    ) -> None:
        self.stack.setCurrentWidget(
            self.start_page
        )

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

    def show_scene(
        self,
        path: Path,
        resource: SceneResource,
    ) -> None:
        del path

        self.scene_viewport.open_scene(
            resource
        )

        self.stack.setCurrentWidget(
            self.scene_viewport
        )

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