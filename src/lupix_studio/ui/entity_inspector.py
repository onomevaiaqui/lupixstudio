from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import SceneEntity


class EntityInspector(QWidget):
    """Inspector de propriedades de uma entidade."""

    entity_changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.entity: SceneEntity | None = None
        self._updating = False

        self.title = QLabel(
            "Nenhuma entidade selecionada"
        )
        self.title.setObjectName(
            "SectionTitle"
        )

        self.kind_value = QLabel("-")
        self.id_value = QLabel("-")
        self.id_value.setWordWrap(True)

        self.x_spin = self._create_position_spin()
        self.y_spin = self._create_position_spin()

        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(
            -3600.0,
            3600.0,
        )
        self.rotation_spin.setDecimals(2)
        self.rotation_spin.setSingleStep(1.0)

        self.scale_x_spin = self._create_scale_spin()
        self.scale_y_spin = self._create_scale_spin()

        form = QFormLayout()

        form.addRow(
            "Tipo:",
            self.kind_value,
        )

        form.addRow(
            "ID:",
            self.id_value,
        )

        form.addRow(
            "Position X:",
            self.x_spin,
        )

        form.addRow(
            "Position Y:",
            self.y_spin,
        )

        form.addRow(
            "Rotation:",
            self.rotation_spin,
        )

        form.addRow(
            "Scale X:",
            self.scale_x_spin,
        )

        form.addRow(
            "Scale Y:",
            self.scale_y_spin,
        )

        layout = QVBoxLayout(self)

        layout.addWidget(
            self.title
        )

        layout.addLayout(
            form
        )

        layout.addStretch()

        self.x_spin.valueChanged.connect(
            self._apply_values
        )

        self.y_spin.valueChanged.connect(
            self._apply_values
        )

        self.rotation_spin.valueChanged.connect(
            self._apply_values
        )

        self.scale_x_spin.valueChanged.connect(
            self._apply_values
        )

        self.scale_y_spin.valueChanged.connect(
            self._apply_values
        )

        self.clear_entity()

    def _create_position_spin(
        self,
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()

        spin.setRange(
            -100000.0,
            100000.0,
        )

        spin.setDecimals(2)
        spin.setSingleStep(1.0)

        return spin

    def _create_scale_spin(
        self,
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()

        spin.setRange(
            -100.0,
            100.0,
        )

        spin.setDecimals(3)
        spin.setSingleStep(0.1)

        return spin

    def clear_entity(
        self,
    ) -> None:
        self.entity = None
        self._updating = True

        try:
            self.title.setText(
                "Nenhuma entidade selecionada"
            )

            self.kind_value.setText("-")
            self.id_value.setText("-")

            self.x_spin.setValue(0.0)
            self.y_spin.setValue(0.0)
            self.rotation_spin.setValue(0.0)

            self.scale_x_spin.setValue(1.0)
            self.scale_y_spin.setValue(1.0)

            self._set_controls_enabled(
                False
            )

        finally:
            self._updating = False

    def show_entity(
        self,
        entity: SceneEntity,
    ) -> None:
        self.entity = entity
        self._updating = True

        try:
            self.title.setText(
                entity.name
            )

            self.kind_value.setText(
                entity.kind
            )

            self.id_value.setText(
                entity.id
            )

            self.x_spin.setValue(
                entity.transform.x
            )

            self.y_spin.setValue(
                entity.transform.y
            )

            self.rotation_spin.setValue(
                entity.transform.rotation
            )

            self.scale_x_spin.setValue(
                entity.transform.scale_x
            )

            self.scale_y_spin.setValue(
                entity.transform.scale_y
            )

            self._set_controls_enabled(
                True
            )

        finally:
            self._updating = False

    def refresh(
        self,
    ) -> None:
        if self.entity is None:
            return

        self.show_entity(
            self.entity
        )

    def _set_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        for control in (
            self.x_spin,
            self.y_spin,
            self.rotation_spin,
            self.scale_x_spin,
            self.scale_y_spin,
        ):
            control.setEnabled(
                enabled
            )

    def _apply_values(
        self,
    ) -> None:
        if (
            self._updating
            or self.entity is None
        ):
            return

        self.entity.transform.x = (
            self.x_spin.value()
        )

        self.entity.transform.y = (
            self.y_spin.value()
        )

        self.entity.transform.rotation = (
            self.rotation_spin.value()
        )

        self.entity.transform.scale_x = (
            self.scale_x_spin.value()
        )

        self.entity.transform.scale_y = (
            self.scale_y_spin.value()
        )

        self.entity_changed.emit()