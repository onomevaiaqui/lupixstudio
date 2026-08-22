from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class InspectorSection(QWidget):
    """Seção recolhível do Inspector."""

    def __init__(
        self,
        title: str,
        content: QWidget,
        expanded: bool = False,
    ) -> None:
        super().__init__()

        self.title = title
        self.content = content

        self.button = QToolButton()

        self.button.setText(
            title
        )

        self.button.setCheckable(
            True
        )

        self.button.setChecked(
            expanded
        )

        self.button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )

        self.button.setArrowType(
            
                Qt.ArrowType.DownArrow
                if expanded
                else Qt.ArrowType.RightArrow
            
        )

        self.button.setStyleSheet(
            """
            QToolButton {
                border: none;
                text-align: left;
                padding: 7px 6px;
                font-weight: 600;
            }

            QToolButton:hover {
                background-color: rgba(255, 255, 255, 18);
            }

            QToolButton:checked {
                background-color: rgba(255, 255, 255, 12);
            }
            """
        )

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setFrameShadow(
            QFrame.Shadow.Sunken
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            0
        )

        layout.addWidget(
            self.button
        )

        layout.addWidget(
            separator
        )

        self.content_container = QWidget()

        content_layout = QVBoxLayout(
            self.content_container
        )

        content_layout.setContentsMargins(
            8,
            8,
            8,
            12,
        )

        content_layout.addWidget(
            content
        )

        layout.addWidget(
            self.content_container
        )

        self.content_container.setVisible(
            expanded
        )

        self.button.toggled.connect(
            self._on_toggled
        )

    def _on_toggled(
        self,
        checked: bool,
    ) -> None:
        self.content_container.setVisible(
            checked
        )

        self.button.setArrowType(
            
                Qt.ArrowType.DownArrow
                if checked
                else Qt.ArrowType.RightArrow
            
        )

    def set_expanded(
        self,
        expanded: bool,
    ) -> None:
        self.button.setChecked(
            expanded
        )

    def is_expanded(self) -> bool:
        return self.button.isChecked()


class EntityInspectorPanel(QWidget):
    """Inspector de entidade com seções recolhíveis."""

    SECTION_TRANSFORM = "transform"
    SECTION_SPRITE = "sprite"
    SECTION_ANIMATION = "animation"
    SECTION_CAMERA = "camera"
    SECTION_TILEMAP = "tilemap"
    SECTION_COLLIDER = "collider"
    SECTION_AREA2D = "area2d"
    SECTION_PLAYER = "player"
    SECTION_UI_ELEMENT = "ui_element"

    def __init__(
        self,
        transform_editor: QWidget,
        sprite_editor: QWidget,
        animation_editor: QWidget,
        camera_editor: QWidget,
        tilemap_editor: QWidget,
        collider_editor: QWidget,
        area2d_editor: QWidget,
        player_editor: QWidget,
        ui_element_editor: QWidget,
    ) -> None:
        super().__init__()

        self.sections: dict[
            str,
            InspectorSection,
        ] = {}

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            0
        )

        self._add_section(
            layout,
            self.SECTION_TRANSFORM,
            "Transform",
            transform_editor,
            expanded=True,
        )

        self._add_section(
            layout,
            self.SECTION_SPRITE,
            "Sprite",
            sprite_editor,
        )

        self._add_section(
            layout,
            self.SECTION_ANIMATION,
            "Animation",
            animation_editor,
        )

        self._add_section(
            layout,
            self.SECTION_CAMERA,
            "Camera",
            camera_editor,
        )

        self._add_section(
            layout,
            self.SECTION_TILEMAP,
            "TileMap",
            tilemap_editor,
        )

        self._add_section(
            layout,
            self.SECTION_COLLIDER,
            "Collider",
            collider_editor,
        )

        self._add_section(
            layout,
            self.SECTION_AREA2D,
            "Area2D",
            area2d_editor,
        )

        self._add_section(
            layout,
            self.SECTION_PLAYER,
            "Player Controller",
            player_editor,
        )

        self._add_section(
            layout, self.SECTION_UI_ELEMENT,
            "Elemento UI", ui_element_editor,
        )

        layout.addStretch()

    def _add_section(
        self,
        layout: QVBoxLayout,
        key: str,
        title: str,
        editor: QWidget,
        expanded: bool = False,
    ) -> None:
        section = InspectorSection(
            title,
            editor,
            expanded=expanded,
        )

        self.sections[
            key
        ] = section

        layout.addWidget(
            section
        )

    def open_section(
        self,
        section_name: str,
        collapse_others: bool = True,
    ) -> None:
        section = self.sections.get(
            section_name
        )

        if section is None:
            return

        if collapse_others:
            for key, other in self.sections.items():
                other.set_expanded(
                    key == section_name
                )

        else:
            section.set_expanded(
                True
            )

    def collapse_all(self) -> None:
        for section in self.sections.values():
            section.set_expanded(
                False
            )

    def expand_transform(self) -> None:
        self.open_section(
            self.SECTION_TRANSFORM
        )