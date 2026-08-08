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
    """Inspector de propriedades básicas de uma entidade."""

    entity_changed = Signal(str)

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

        self.position_x = QDoubleSpinBox()
        self.position_y = QDoubleSpinBox()
        self.rotation = QDoubleSpinBox()
        self.scale_x = QDoubleSpinBox()
        self.scale_y = QDoubleSpinBox()

        for spin in (
            self.position_x,
            self.position_y,
        ):
            spin.setRange(
                -100000.0,
                100000.0,
            )
            spin.setDecimals(2)

        self.rotation.setRange(
            -36000.0,
            36000.0,
        )
        self.rotation.setDecimals(2)

        for spin in (
            self.scale_x,
            self.scale_y,
        ):
            spin.setRange(
                -1000.0,
                1000.0,
            )
            spin.setDecimals(3)
            spin.setSingleStep(
                0.1
            )

        form = QFormLayout()

        form.addRow(
            "Tipo:",
            self.kind_value,
        )

        form.addRow(
            "Position X:",
            self.position_x,
        )

        form.addRow(
            "Position Y:",
            self.position_y,
        )

        form.addRow(
            "Rotation:",
            self.rotation,
        )

        form.addRow(
            "Scale X:",
            self.scale_x,
        )

        form.addRow(
            "Scale Y:",
            self.scale_y,
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

        layout.addStretch()

        self.position_x.valueChanged.connect(
            self._apply_values
        )

        self.position_y.valueChanged.connect(
            self._apply_values
        )

        self.rotation.valueChanged.connect(
            self._apply_values
        )

        self.scale_x.valueChanged.connect(
            self._apply_values
        )

        self.scale_y.valueChanged.connect(
            self._apply_values
        )

        self.setEnabled(
            False
        )

    def clear_entity(self) -> None:
        self.entity = None

        self.title.setText(
            "Nenhuma entidade selecionada"
        )

        self.kind_value.setText(
            "-"
        )

        self.setEnabled(
            False
        )

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

            self.position_x.setValue(
                entity.transform.x
            )

            self.position_y.setValue(
                entity.transform.y
            )

            self.rotation.setValue(
                entity.transform.rotation
            )

            self.scale_x.setValue(
                entity.transform.scale_x
            )

            self.scale_y.setValue(
                entity.transform.scale_y
            )

        finally:
            self._updating = False

        self.setEnabled(
            True
        )

    def refresh_values(self) -> None:
        if self.entity is None:
            return

        self.show_entity(
            self.entity
        )

    def _apply_values(self) -> None:
        if (
            self.entity is None
            or self._updating
        ):
            return

        self.entity.transform.x = (
            self.position_x.value()
        )

        self.entity.transform.y = (
            self.position_y.value()
        )

        self.entity.transform.rotation = (
            self.rotation.value()
        )

        self.entity.transform.scale_x = (
            self.scale_x.value()
        )

        self.entity.transform.scale_y = (
            self.scale_y.value()
        )

        self.entity_changed.emit(
            self.entity.id
        )