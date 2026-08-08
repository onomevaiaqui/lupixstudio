from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRecord, AssetRegistry
from lupix_studio.scene.model import SceneEntity, SpriteComponent


class SpriteComponentEditor(QWidget):
    """Editor do componente Sprite de uma entidade."""

    sprite_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.entity: SceneEntity | None = None
        self.records: list[AssetRecord] = []
        self._updating = False

        self.title = QLabel(
            "Sprite"
        )
        self.title.setObjectName(
            "SectionTitle"
        )

        self.asset_combo = QComboBox()

        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(
            0.0,
            1.0,
        )
        self.opacity_spin.setSingleStep(
            0.05
        )
        self.opacity_spin.setDecimals(
            2
        )

        self.flip_x = QCheckBox()
        self.flip_y = QCheckBox()

        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(
            -10000,
            10000,
        )

        self.remove_button = QPushButton(
            "Remover Sprite"
        )

        form = QFormLayout()

        form.addRow(
            "Asset:",
            self.asset_combo,
        )

        form.addRow(
            "Opacity:",
            self.opacity_spin,
        )

        form.addRow(
            "Flip X:",
            self.flip_x,
        )

        form.addRow(
            "Flip Y:",
            self.flip_y,
        )

        form.addRow(
            "Layer:",
            self.layer_spin,
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            self.title
        )

        layout.addLayout(
            form
        )

        layout.addWidget(
            self.remove_button
        )

        layout.addStretch()

        self.asset_combo.currentIndexChanged.connect(
            self._apply_values
        )

        self.opacity_spin.valueChanged.connect(
            self._apply_values
        )

        self.flip_x.toggled.connect(
            self._apply_values
        )

        self.flip_y.toggled.connect(
            self._apply_values
        )

        self.layer_spin.valueChanged.connect(
            self._apply_values
        )

        self.remove_button.clicked.connect(
            self._remove_sprite
        )

    def set_context(
        self,
        project_root: Path | None,
        entity: SceneEntity | None,
    ) -> None:
        self.project_root = (
            project_root.resolve()
            if project_root is not None
            else None
        )

        self.entity = entity

        self._reload_assets()
        self._refresh_values()

    def _reload_assets(self) -> None:
        self.asset_combo.blockSignals(
            True
        )

        try:
            self.asset_combo.clear()
            self.records = []

            self.asset_combo.addItem(
                "Nenhum",
                "",
            )

            if self.project_root is None:
                return

            registry = AssetRegistry(
                self.project_root
            )

            self.records = [
                record
                for record in registry.load()
                if record.type == "sprites"
            ]

            for record in self.records:
                self.asset_combo.addItem(
                    record.name,
                    record.id,
                )

        finally:
            self.asset_combo.blockSignals(
                False
            )

    def _refresh_values(self) -> None:
        self._updating = True

        try:
            if self.entity is None:
                self.setEnabled(
                    False
                )
                return

            self.setEnabled(
                True
            )

            sprite = self.entity.sprite

            if sprite is None:
                self.asset_combo.setCurrentIndex(
                    0
                )
                self.opacity_spin.setValue(
                    1.0
                )
                self.flip_x.setChecked(
                    False
                )
                self.flip_y.setChecked(
                    False
                )
                self.layer_spin.setValue(
                    0
                )
                return

            index = self.asset_combo.findData(
                sprite.asset_id
            )

            self.asset_combo.setCurrentIndex(
                max(index, 0)
            )

            self.opacity_spin.setValue(
                sprite.opacity
            )

            self.flip_x.setChecked(
                sprite.flip_x
            )

            self.flip_y.setChecked(
                sprite.flip_y
            )

            self.layer_spin.setValue(
                sprite.layer
            )

        finally:
            self._updating = False

    def _apply_values(self) -> None:
        if (
            self.entity is None
            or self._updating
        ):
            return

        asset_id = str(
            self.asset_combo.currentData()
            or ""
        )

        if not asset_id:
            self.entity.sprite = None
            self.entity.kind = "empty"

            self.sprite_changed.emit(
                self.entity.id
            )
            return

        if self.entity.sprite is None:
            self.entity.sprite = SpriteComponent()

        self.entity.kind = "sprite"

        self.entity.sprite.asset_id = (
            asset_id
        )

        self.entity.sprite.opacity = (
            self.opacity_spin.value()
        )

        self.entity.sprite.flip_x = (
            self.flip_x.isChecked()
        )

        self.entity.sprite.flip_y = (
            self.flip_y.isChecked()
        )

        self.entity.sprite.layer = (
            self.layer_spin.value()
        )

        self.sprite_changed.emit(
            self.entity.id
        )

    def _remove_sprite(self) -> None:
        if self.entity is None:
            return

        self.entity.sprite = None
        self.entity.kind = "empty"

        self._refresh_values()

        self.sprite_changed.emit(
            self.entity.id
        )