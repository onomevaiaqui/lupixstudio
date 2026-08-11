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
    PlayerControllerComponent,
    SceneEntity,
)


class PlayerControllerEditor(QWidget):
    """Editor do componente Player Controller."""

    player_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.entity: SceneEntity | None = None
        self._updating = False

        self.enabled_checkbox = QCheckBox()

        self.speed_spin = QDoubleSpinBox()
        self.jump_force_spin = QDoubleSpinBox()
        self.gravity_spin = QDoubleSpinBox()
        self.max_fall_speed_spin = QDoubleSpinBox()
        self.air_control_spin = QDoubleSpinBox()

        for spin in (
            self.speed_spin,
            self.jump_force_spin,
            self.gravity_spin,
            self.max_fall_speed_spin,
        ):
            spin.setRange(
                0.0,
                100000.0,
            )

            spin.setDecimals(
                2
            )

            spin.setSingleStep(
                10.0
            )

        self.air_control_spin.setRange(
            0.0,
            1.0,
        )

        self.air_control_spin.setDecimals(
            2
        )

        self.air_control_spin.setSingleStep(
            0.05
        )

        self.add_button = QPushButton(
            "Adicionar Player Controller"
        )

        self.remove_button = QPushButton(
            "Remover Player Controller"
        )

        form = QFormLayout()

        form.addRow(
            "Ativo:",
            self.enabled_checkbox,
        )

        form.addRow(
            "Velocidade:",
            self.speed_spin,
        )

        form.addRow(
            "Força do pulo:",
            self.jump_force_spin,
        )

        form.addRow(
            "Gravidade:",
            self.gravity_spin,
        )

        form.addRow(
            "Velocidade máx. de queda:",
            self.max_fall_speed_spin,
        )

        form.addRow(
            "Controle no ar:",
            self.air_control_spin,
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
            self._add_player_controller
        )

        self.remove_button.clicked.connect(
            self._remove_player_controller
        )

        self.enabled_checkbox.toggled.connect(
            self._apply_values
        )

        self.speed_spin.valueChanged.connect(
            self._apply_values
        )

        self.jump_force_spin.valueChanged.connect(
            self._apply_values
        )

        self.gravity_spin.valueChanged.connect(
            self._apply_values
        )

        self.max_fall_speed_spin.valueChanged.connect(
            self._apply_values
        )

        self.air_control_spin.valueChanged.connect(
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

            controller = (
                self.entity.player_controller
            )

            has_controller = (
                controller is not None
            )

            self.add_button.setVisible(
                not has_controller
            )

            self.remove_button.setVisible(
                has_controller
            )

            self.enabled_checkbox.setEnabled(
                has_controller
            )

            self.speed_spin.setEnabled(
                has_controller
            )

            self.jump_force_spin.setEnabled(
                has_controller
            )

            self.gravity_spin.setEnabled(
                has_controller
            )

            self.max_fall_speed_spin.setEnabled(
                has_controller
            )

            self.air_control_spin.setEnabled(
                has_controller
            )

            if controller is None:
                self.enabled_checkbox.setChecked(
                    True
                )

                self.speed_spin.setValue(
                    80.0
                )

                self.jump_force_spin.setValue(
                    220.0
                )

                self.gravity_spin.setValue(
                    600.0
                )

                self.max_fall_speed_spin.setValue(
                    500.0
                )

                self.air_control_spin.setValue(
                    0.75
                )

                return

            self.enabled_checkbox.setChecked(
                controller.enabled
            )

            self.speed_spin.setValue(
                controller.speed
            )

            self.jump_force_spin.setValue(
                controller.jump_force
            )

            self.gravity_spin.setValue(
                controller.gravity
            )

            self.max_fall_speed_spin.setValue(
                controller.max_fall_speed
            )

            self.air_control_spin.setValue(
                controller.air_control
            )

        finally:
            self._updating = False

    def _add_player_controller(self) -> None:
        if self.entity is None:
            return

        self.entity.player_controller = (
            PlayerControllerComponent()
        )

        self.entity.refresh_kind()

        self._refresh_values()

        self.player_changed.emit(
            self.entity.id
        )

    def _remove_player_controller(self) -> None:
        if self.entity is None:
            return

        self.entity.player_controller = None

        self.entity.refresh_kind()

        self._refresh_values()

        self.player_changed.emit(
            self.entity.id
        )

    def _apply_values(self) -> None:
        if (
            self.entity is None
            or self.entity.player_controller is None
            or self._updating
        ):
            return

        controller = (
            self.entity.player_controller
        )

        controller.enabled = (
            self.enabled_checkbox.isChecked()
        )

        controller.speed = (
            self.speed_spin.value()
        )

        controller.jump_force = (
            self.jump_force_spin.value()
        )

        controller.gravity = (
            self.gravity_spin.value()
        )

        controller.max_fall_speed = (
            self.max_fall_speed_spin.value()
        )

        controller.air_control = (
            self.air_control_spin.value()
        )

        self.player_changed.emit(
            self.entity.id
        )