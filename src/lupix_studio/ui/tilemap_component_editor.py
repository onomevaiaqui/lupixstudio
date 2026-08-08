from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import (
    SceneEntity,
    SceneResource,
    TileMapComponent,
)
from lupix_studio.tilemap.model import TileMapResource
from lupix_studio.tilemap.serializer import TileMapSerializer


class TileMapComponentEditor(QWidget):
    """Editor do componente TileMap."""

    tilemap_changed = Signal(str)
    edit_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.scene: SceneResource | None = None
        self.entity: SceneEntity | None = None

        self._updating = False

        self.resource_label = QLabel("-")
        self.resource_label.setWordWrap(True)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(
            1,
            4096,
        )

        self.height_spin = QSpinBox()
        self.height_spin.setRange(
            1,
            4096,
        )

        self.tile_width_spin = QSpinBox()
        self.tile_width_spin.setRange(
            1,
            512,
        )

        self.tile_height_spin = QSpinBox()
        self.tile_height_spin.setRange(
            1,
            512,
        )

        self.add_button = QPushButton(
            "Adicionar TileMap"
        )

        self.remove_button = QPushButton(
            "Remover TileMap"
        )

        self.edit_button = QPushButton(
            "Editar TileMap"
        )

        form = QFormLayout()

        form.addRow(
            "Recurso:",
            self.resource_label,
        )

        form.addRow(
            "Largura:",
            self.width_spin,
        )

        form.addRow(
            "Altura:",
            self.height_spin,
        )

        form.addRow(
            "Tile Width:",
            self.tile_width_spin,
        )

        form.addRow(
            "Tile Height:",
            self.tile_height_spin,
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            self.add_button
        )

        layout.addLayout(
            form
        )

        layout.addWidget(
            self.edit_button
        )

        layout.addWidget(
            self.remove_button
        )

        layout.addStretch()

        self.add_button.clicked.connect(
            self._add_tilemap
        )

        self.remove_button.clicked.connect(
            self._remove_tilemap
        )

        self.edit_button.clicked.connect(
            self._request_edit
        )

        self.width_spin.valueChanged.connect(
            self._apply_resource_values
        )

        self.height_spin.valueChanged.connect(
            self._apply_resource_values
        )

        self.tile_width_spin.valueChanged.connect(
            self._apply_resource_values
        )

        self.tile_height_spin.valueChanged.connect(
            self._apply_resource_values
        )

        self.set_context(
            None,
            None,
            None,
        )

    def set_context(
        self,
        project_root: Path | None,
        scene: SceneResource | None,
        entity: SceneEntity | None,
    ) -> None:
        self.project_root = (
            project_root.resolve()
            if project_root is not None
            else None
        )

        self.scene = scene
        self.entity = entity

        self._refresh_values()

    def _resource_path(self) -> Path | None:
        if (
            self.project_root is None
            or self.entity is None
            or self.entity.tilemap is None
            or not self.entity.tilemap.resource_path
        ):
            return None

        return (
            self.project_root
            / self.entity.tilemap.resource_path
        )

    def _load_resource(
        self,
    ) -> TileMapResource | None:
        path = self._resource_path()

        if (
            path is None
            or not path.exists()
        ):
            return None

        return TileMapSerializer().load(
            path
        )

    def _refresh_values(self) -> None:
        self._updating = True

        try:
            if self.entity is None:
                self.setEnabled(False)
                return

            self.setEnabled(True)

            has_tilemap = (
                self.entity.tilemap
                is not None
            )

            self.add_button.setVisible(
                not has_tilemap
            )

            self.remove_button.setVisible(
                has_tilemap
            )

            self.edit_button.setVisible(
                has_tilemap
            )

            self.width_spin.setEnabled(
                has_tilemap
            )

            self.height_spin.setEnabled(
                has_tilemap
            )

            self.tile_width_spin.setEnabled(
                has_tilemap
            )

            self.tile_height_spin.setEnabled(
                has_tilemap
            )

            if not has_tilemap:
                self.resource_label.setText(
                    "-"
                )

                width = 30
                height = 17

                if self.scene is not None:
                    width = max(
                        1,
                        self.scene.width // 16,
                    )

                    height = max(
                        1,
                        self.scene.height // 16,
                    )

                self.width_spin.setValue(
                    width
                )

                self.height_spin.setValue(
                    height
                )

                self.tile_width_spin.setValue(
                    16
                )

                self.tile_height_spin.setValue(
                    16
                )

                return

            self.resource_label.setText(
                self.entity.tilemap.resource_path
            )

            resource = self._load_resource()

            if resource is None:
                return

            self.width_spin.setValue(
                resource.width
            )

            self.height_spin.setValue(
                resource.height
            )

            self.tile_width_spin.setValue(
                resource.tile_width
            )

            self.tile_height_spin.setValue(
                resource.tile_height
            )

        finally:
            self._updating = False

    def _add_tilemap(self) -> None:
        if (
            self.project_root is None
            or self.entity is None
        ):
            return

        safe_name = (
            self.entity.name
            .strip()
            .replace(" ", "_")
        )

        if not safe_name:
            safe_name = "TileMap"

        relative_path = (
            Path("maps")
            / f"{safe_name}_{self.entity.id[:8]}.tilemap"
        )

        absolute_path = (
            self.project_root
            / relative_path
        )

        tile_width = 16
        tile_height = 16

        width = 30
        height = 17

        if self.scene is not None:
            width = max(
                1,
                self.scene.width // tile_width,
            )

            height = max(
                1,
                self.scene.height // tile_height,
            )

        resource = TileMapResource(
            name=self.entity.name,
            tile_width=tile_width,
            tile_height=tile_height,
            width=width,
            height=height,
        )

        TileMapSerializer().save(
            resource,
            absolute_path,
        )

        self.entity.tilemap = TileMapComponent(
            resource_path=str(
                relative_path
            ).replace("\\", "/")
        )

        self.entity.refresh_kind()

        self._refresh_values()

        self.tilemap_changed.emit(
            self.entity.id
        )

    def _remove_tilemap(self) -> None:
        if self.entity is None:
            return

        self.entity.tilemap = None
        self.entity.refresh_kind()

        self._refresh_values()

        self.tilemap_changed.emit(
            self.entity.id
        )

    def _apply_resource_values(self) -> None:
        if self._updating:
            return

        resource = self._load_resource()

        if resource is None:
            return

        resource.width = (
            self.width_spin.value()
        )

        resource.height = (
            self.height_spin.value()
        )

        resource.tile_width = (
            self.tile_width_spin.value()
        )

        resource.tile_height = (
            self.tile_height_spin.value()
        )

        path = self._resource_path()

        if path is None:
            return

        TileMapSerializer().save(
            resource,
            path,
        )

        if self.entity is not None:
            self.tilemap_changed.emit(
                self.entity.id
            )

    def _request_edit(self) -> None:
        if (
            self.entity is None
            or self.entity.tilemap is None
        ):
            return

        self.edit_requested.emit(
            self.entity.id
        )