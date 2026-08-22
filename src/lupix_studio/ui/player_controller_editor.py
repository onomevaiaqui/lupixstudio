from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
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
        self.max_health_spin = QDoubleSpinBox()
        self.respawn_delay_spin = QDoubleSpinBox()
        self.death_fade_spin = QDoubleSpinBox()
        self.show_death_message_checkbox = QCheckBox()
        self.death_message_edit = QLineEdit()
        self.confirm_respawn_checkbox = QCheckBox()
        self.damage_stun_spin = QDoubleSpinBox()
        self.damage_invulnerability_spin = QDoubleSpinBox()
        self.show_health_hud_checkbox = QCheckBox()

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

        self.max_health_spin.setRange(1.0, 9999.0)
        self.max_health_spin.setDecimals(0)
        self.max_health_spin.setSingleStep(1.0)
        self.respawn_delay_spin.setRange(0.0, 60.0)
        self.respawn_delay_spin.setDecimals(2)
        self.respawn_delay_spin.setSingleStep(0.25)
        self.respawn_delay_spin.setSuffix(" s")
        self.death_fade_spin.setRange(0.05, 3.0)
        self.death_fade_spin.setDecimals(2)
        self.death_fade_spin.setSingleStep(0.05)
        self.death_fade_spin.setSuffix(" s")
        self.death_message_edit.setPlaceholderText("Você morreu")
        for spin in (self.damage_stun_spin, self.damage_invulnerability_spin):
            spin.setRange(0.0, 10.0)
            spin.setDecimals(2)
            spin.setSingleStep(0.05)
            spin.setSuffix(" s")

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

        form.addRow(
            "Vida máxima:",
            self.max_health_spin,
        )

        form.addRow(
            "Tempo de respawn:",
            self.respawn_delay_spin,
        )

        form.addRow(
            "Duração do fade:",
            self.death_fade_spin,
        )

        form.addRow(
            "Exibir texto de morte:",
            self.show_death_message_checkbox,
        )

        form.addRow(
            "Texto de morte:",
            self.death_message_edit,
        )

        form.addRow(
            "Perguntar se deseja continuar:",
            self.confirm_respawn_checkbox,
        )

        form.addRow("Bloqueio ao sofrer dano:", self.damage_stun_spin)
        form.addRow(
            "Invulnerabilidade após dano:",
            self.damage_invulnerability_spin,
        )

        form.addRow(
            "Mostrar vida no Preview:",
            self.show_health_hud_checkbox,
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

        self.max_health_spin.valueChanged.connect(
            self._apply_values
        )

        self.respawn_delay_spin.valueChanged.connect(
            self._apply_values
        )

        self.death_fade_spin.valueChanged.connect(
            self._apply_values
        )

        self.show_death_message_checkbox.toggled.connect(
            self._apply_values
        )

        self.death_message_edit.editingFinished.connect(
            self._apply_values
        )

        self.confirm_respawn_checkbox.toggled.connect(
            self._apply_values
        )
        self.damage_stun_spin.valueChanged.connect(self._apply_values)
        self.damage_invulnerability_spin.valueChanged.connect(
            self._apply_values
        )
        self.show_health_hud_checkbox.toggled.connect(
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
            self.max_health_spin.setEnabled(has_controller)
            self.respawn_delay_spin.setEnabled(has_controller)
            self.death_fade_spin.setEnabled(has_controller)
            self.show_death_message_checkbox.setEnabled(
                has_controller
            )
            self.death_message_edit.setEnabled(has_controller)
            self.confirm_respawn_checkbox.setEnabled(
                has_controller
            )
            self.damage_stun_spin.setEnabled(has_controller)
            self.damage_invulnerability_spin.setEnabled(has_controller)
            self.show_health_hud_checkbox.setEnabled(has_controller)

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
                self.max_health_spin.setValue(3.0)
                self.respawn_delay_spin.setValue(1.0)
                self.death_fade_spin.setValue(0.35)
                self.show_death_message_checkbox.setChecked(True)
                self.death_message_edit.setText("Você morreu")
                self.confirm_respawn_checkbox.setChecked(True)
                self.damage_stun_spin.setValue(0.15)
                self.damage_invulnerability_spin.setValue(0.75)
                self.show_health_hud_checkbox.setChecked(True)

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
            self.max_health_spin.setValue(
                controller.max_health
            )
            self.respawn_delay_spin.setValue(
                controller.respawn_delay
            )
            self.death_fade_spin.setValue(
                controller.death_fade_duration
            )
            self.show_death_message_checkbox.setChecked(
                controller.show_death_message
            )
            self.death_message_edit.setText(
                controller.death_message
            )
            self.confirm_respawn_checkbox.setChecked(
                controller.confirm_respawn
            )
            self.damage_stun_spin.setValue(
                controller.damage_stun_duration
            )
            self.damage_invulnerability_spin.setValue(
                controller.damage_invulnerability
            )
            self.show_health_hud_checkbox.setChecked(
                controller.show_health_hud
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
        controller.max_health = int(
            self.max_health_spin.value()
        )
        controller.respawn_delay = (
            self.respawn_delay_spin.value()
        )
        controller.death_fade_duration = (
            self.death_fade_spin.value()
        )
        controller.show_death_message = (
            self.show_death_message_checkbox.isChecked()
        )
        controller.death_message = (
            self.death_message_edit.text()
        )
        controller.confirm_respawn = (
            self.confirm_respawn_checkbox.isChecked()
        )
        controller.damage_stun_duration = self.damage_stun_spin.value()
        controller.damage_invulnerability = (
            self.damage_invulnerability_spin.value()
        )
        controller.show_health_hud = (
            self.show_health_hud_checkbox.isChecked()
        )

        self.player_changed.emit(
            self.entity.id
        )