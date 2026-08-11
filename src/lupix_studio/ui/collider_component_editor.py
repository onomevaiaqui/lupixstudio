from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import (
    ColliderComponent,
    SceneEntity,
)


class ColliderComponentEditor(QWidget):
    """Editor do componente Collider."""

    collider_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.entity: SceneEntity | None = None
        self._updating = False

        self.enabled_checkbox = QCheckBox()

        self.width_spin = QDoubleSpinBox()
        self.height_spin = QDoubleSpinBox()

        self.offset_x_spin = QDoubleSpinBox()
        self.offset_y_spin = QDoubleSpinBox()

        self.solid_checkbox = QCheckBox()

        for spin in (
            self.width_spin,
            self.height_spin,
        ):
            spin.setRange(
                0.01,
                100000.0,
            )

            spin.setDecimals(
                2
            )

            spin.setSingleStep(
                1.0
            )

        for spin in (
            self.offset_x_spin,
            self.offset_y_spin,
        ):
            spin.setRange(
                -100000.0,
                100000.0,
            )

            spin.setDecimals(
                2
            )

            spin.setSingleStep(
                1.0
            )

        self.add_button = QPushButton(
            "Adicionar Collider"
        )

        self.remove_button = QPushButton(
            "Remover Collider"
        )

        form = QFormLayout()

        form.addRow(
            "Ativo:",
            self.enabled_checkbox,
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
            "Offset X:",
            self.offset_x_spin,
        )

        form.addRow(
            "Offset Y:",
            self.offset_y_spin,
        )

        form.addRow(
            "Sólido:",
            self.solid_checkbox,
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
            self.remove_button
        )

        layout.addStretch()

        self.add_button.clicked.connect(
            self._add_collider
        )

        self.remove_button.clicked.connect(
            self._remove_collider
        )

        self.enabled_checkbox.toggled.connect(
            self._apply_values
        )

        self.width_spin.valueChanged.connect(
            self._apply_values
        )

        self.height_spin.valueChanged.connect(
            self._apply_values
        )

        self.offset_x_spin.valueChanged.connect(
            self._apply_values
        )

        self.offset_y_spin.valueChanged.connect(
            self._apply_values
        )

        self.solid_checkbox.toggled.connect(
            self._apply_values
        )

        self.set_context(
            None
        )

    def set_context(
        self,
        entity: SceneEntity | None,
    ) -> None:
        self.entity = entity

        self._refresh_values()

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

            collider = (
                self.entity.collider
            )

            has_collider = (
                collider is not None
            )

            self.add_button.setVisible(
                not has_collider
            )

            self.remove_button.setVisible(
                has_collider
            )

            self.enabled_checkbox.setEnabled(
                has_collider
            )

            self.width_spin.setEnabled(
                has_collider
            )

            self.height_spin.setEnabled(
                has_collider
            )

            self.offset_x_spin.setEnabled(
                has_collider
            )

            self.offset_y_spin.setEnabled(
                has_collider
            )

            self.solid_checkbox.setEnabled(
                has_collider
            )

            if collider is None:
                self.enabled_checkbox.setChecked(
                    True
                )

                self.width_spin.setValue(
                    16.0
                )

                self.height_spin.setValue(
                    16.0
                )

                self.offset_x_spin.setValue(
                    0.0
                )

                self.offset_y_spin.setValue(
                    0.0
                )

                self.solid_checkbox.setChecked(
                    True
                )

                return

            self.enabled_checkbox.setChecked(
                collider.enabled
            )

            self.width_spin.setValue(
                collider.width
            )

            self.height_spin.setValue(
                collider.height
            )

            self.offset_x_spin.setValue(
                collider.offset_x
            )

            self.offset_y_spin.setValue(
                collider.offset_y
            )

            self.solid_checkbox.setChecked(
                collider.solid
            )

        finally:
            self._updating = False

    def _add_collider(self) -> None:
        if self.entity is None:
            return

        self.entity.collider = (
            ColliderComponent(
                enabled=True,
                width=16.0,
                height=16.0,
                offset_x=0.0,
                offset_y=0.0,
                solid=True,
            )
        )

        self.entity.refresh_kind()

        self._refresh_values()

        self.collider_changed.emit(
            self.entity.id
        )

    def _remove_collider(self) -> None:
        if self.entity is None:
            return

        self.entity.collider = None

        self.entity.refresh_kind()

        self._refresh_values()

        self.collider_changed.emit(
            self.entity.id
        )

    def _apply_values(self) -> None:
        if (
            self.entity is None
            or self.entity.collider is None
            or self._updating
        ):
            return

        collider = self.entity.collider

        collider.enabled = (
            self.enabled_checkbox.isChecked()
        )

        collider.width = (
            self.width_spin.value()
        )

        collider.height = (
            self.height_spin.value()
        )

        collider.offset_x = (
            self.offset_x_spin.value()
        )

        collider.offset_y = (
            self.offset_y_spin.value()
        )

        collider.solid = (
            self.solid_checkbox.isChecked()
        )

        self.collider_changed.emit(
            self.entity.id
        )