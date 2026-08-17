from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import (
    CameraComponent,
    SceneEntity,
    SceneResource,
)


class VisibleCheckBox(QCheckBox):
    """Checkbox consistente com o tema escuro do Lupix."""

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        if not self.isChecked():
            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        indicator_size = 18

        top = (
            self.rect().height()
            - indicator_size
        ) // 2

        pen = QPen(
            QColor("#ffffff"),
            2.2,
        )

        painter.setPen(pen)

        painter.drawLine(
            4,
            top + 9,
            8,
            top + 13,
        )

        painter.drawLine(
            8,
            top + 13,
            15,
            top + 5,
        )


class CameraComponentEditor(QWidget):
    """Editor do componente Camera."""

    camera_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.scene: SceneResource | None = None
        self.entity: SceneEntity | None = None

        self._updating = False

        self.setStyleSheet(
            """
            QSpinBox,
            QDoubleSpinBox {
                min-height: 26px;
            }

            QPushButton {
                min-height: 30px;
            }

            QLabel#CameraHint {
                color: #8d929b;
            }

            QLabel#CameraSection {
                font-weight: 600;
                margin-top: 8px;
            }

            QPushButton#RemoveCameraButton {
                color: #ff6565;
                border: 1px solid #d74646;
            }
            """
        )

        self.status_label = QLabel(
            "Nenhuma entidade selecionada."
        )

        self.status_label.setObjectName(
            "CameraHint"
        )

        self.status_label.setWordWrap(
            True
        )

        self.add_button = QPushButton(
            "Adicionar Camera"
        )

        self.active_checkbox = VisibleCheckBox(
            "Camera ativa"
        )

        self.width_spin = QSpinBox()
        self.width_spin.setRange(
            1,
            16384,
        )
        self.width_spin.setValue(
            480
        )

        self.height_spin = QSpinBox()
        self.height_spin.setRange(
            1,
            16384,
        )
        self.height_spin.setValue(
            270
        )

        self.zoom_spin = QDoubleSpinBox()
        self.zoom_spin.setRange(
            0.05,
            32.0,
        )
        self.zoom_spin.setDecimals(
            2
        )
        self.zoom_spin.setSingleStep(
            0.10
        )
        self.zoom_spin.setValue(
            1.0
        )

        self.offset_x_spin = QDoubleSpinBox()
        self.offset_x_spin.setRange(
            -100000.0,
            100000.0,
        )
        self.offset_x_spin.setDecimals(
            1
        )

        self.offset_y_spin = QDoubleSpinBox()
        self.offset_y_spin.setRange(
            -100000.0,
            100000.0,
        )
        self.offset_y_spin.setDecimals(
            1
        )

        self.limit_section = QLabel(
            "Limites"
        )
        self.limit_section.setObjectName(
            "CameraSection"
        )

        self.limit_checkbox = VisibleCheckBox(
            "Limitar aos limites da fase"
        )

        self.custom_limits_checkbox = VisibleCheckBox(
            "Usar limites personalizados"
        )

        self.limit_left_spin = self._limit_spin()
        self.limit_top_spin = self._limit_spin()
        self.limit_right_spin = self._limit_spin()
        self.limit_bottom_spin = self._limit_spin()

        self.dead_zone_section = QLabel(
            "Dead Zone"
        )
        self.dead_zone_section.setObjectName(
            "CameraSection"
        )

        self.dead_zone_checkbox = VisibleCheckBox(
            "Ativar Dead Zone"
        )

        self.dead_zone_width_spin = QDoubleSpinBox()
        self.dead_zone_width_spin.setRange(
            0.0,
            100000.0,
        )
        self.dead_zone_width_spin.setDecimals(
            1
        )
        self.dead_zone_width_spin.setValue(
            80.0
        )

        self.dead_zone_height_spin = QDoubleSpinBox()
        self.dead_zone_height_spin.setRange(
            0.0,
            100000.0,
        )
        self.dead_zone_height_spin.setDecimals(
            1
        )
        self.dead_zone_height_spin.setValue(
            50.0
        )

        self.smoothing_section = QLabel(
            "Suavização"
        )
        self.smoothing_section.setObjectName(
            "CameraSection"
        )

        self.smoothing_checkbox = VisibleCheckBox(
            "Ativar suavização"
        )

        self.smoothing_speed_spin = QDoubleSpinBox()
        self.smoothing_speed_spin.setRange(
            0.01,
            100.0,
        )
        self.smoothing_speed_spin.setDecimals(
            2
        )
        self.smoothing_speed_spin.setSingleStep(
            0.25
        )
        self.smoothing_speed_spin.setValue(
            5.0
        )

        self.follow_label = QLabel(
            "A Camera acompanha automaticamente a entidade "
            "que possui este componente. Se ela estiver no Player, "
            "acompanhará o Player durante o jogo."
        )

        self.follow_label.setObjectName(
            "CameraHint"
        )

        self.follow_label.setWordWrap(
            True
        )

        form = QFormLayout()

        form.addRow(
            "Largura visível:",
            self.width_spin,
        )

        form.addRow(
            "Altura visível:",
            self.height_spin,
        )

        form.addRow(
            "Zoom:",
            self.zoom_spin,
        )

        form.addRow(
            "Offset X:",
            self.offset_x_spin,
        )

        form.addRow(
            "Offset Y:",
            self.offset_y_spin,
        )

        limits_form = QFormLayout()

        limits_form.addRow(
            "Esquerda:",
            self.limit_left_spin,
        )

        limits_form.addRow(
            "Topo:",
            self.limit_top_spin,
        )

        limits_form.addRow(
            "Direita:",
            self.limit_right_spin,
        )

        limits_form.addRow(
            "Baixo:",
            self.limit_bottom_spin,
        )

        dead_zone_form = QFormLayout()

        dead_zone_form.addRow(
            "Largura:",
            self.dead_zone_width_spin,
        )

        dead_zone_form.addRow(
            "Altura:",
            self.dead_zone_height_spin,
        )

        smoothing_form = QFormLayout()

        smoothing_form.addRow(
            "Velocidade:",
            self.smoothing_speed_spin,
        )

        self.remove_button = QPushButton(
            "Remover Camera"
        )

        self.remove_button.setObjectName(
            "RemoveCameraButton"
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
            8
        )

        layout.addWidget(
            self.status_label
        )

        layout.addWidget(
            self.add_button
        )

        layout.addWidget(
            self.active_checkbox
        )

        layout.addLayout(
            form
        )

        layout.addWidget(
            self.limit_section
        )

        layout.addWidget(
            self.limit_checkbox
        )

        layout.addWidget(
            self.custom_limits_checkbox
        )

        layout.addLayout(
            limits_form
        )

        layout.addWidget(
            self.dead_zone_section
        )

        layout.addWidget(
            self.dead_zone_checkbox
        )

        layout.addLayout(
            dead_zone_form
        )

        layout.addWidget(
            self.smoothing_section
        )

        layout.addWidget(
            self.smoothing_checkbox
        )

        layout.addLayout(
            smoothing_form
        )

        layout.addWidget(
            self.follow_label
        )

        layout.addWidget(
            self.remove_button
        )

        layout.addStretch()

        self.add_button.clicked.connect(
            self._add_camera
        )

        self.remove_button.clicked.connect(
            self._remove_camera
        )

        for widget in (
            self.active_checkbox,
            self.width_spin,
            self.height_spin,
            self.zoom_spin,
            self.offset_x_spin,
            self.offset_y_spin,
            self.limit_checkbox,
            self.custom_limits_checkbox,
            self.limit_left_spin,
            self.limit_top_spin,
            self.limit_right_spin,
            self.limit_bottom_spin,
            self.dead_zone_checkbox,
            self.dead_zone_width_spin,
            self.dead_zone_height_spin,
            self.smoothing_checkbox,
            self.smoothing_speed_spin,
        ):
            if isinstance(
                widget,
                QCheckBox,
            ):
                widget.toggled.connect(
                    self._apply
                )
            else:
                widget.valueChanged.connect(
                    self._apply
                )

        self.custom_limits_checkbox.toggled.connect(
            self._update_dependency_controls
        )

        self.dead_zone_checkbox.toggled.connect(
            self._update_dependency_controls
        )

        self.smoothing_checkbox.toggled.connect(
            self._update_dependency_controls
        )

        self.limit_checkbox.toggled.connect(
            self._update_dependency_controls
        )

        self.set_context(
            None,
            None,
        )

    @staticmethod
    def _limit_spin() -> QDoubleSpinBox:
        spin = QDoubleSpinBox()

        spin.setRange(
            -1000000.0,
            1000000.0,
        )

        spin.setDecimals(
            1
        )

        return spin

    def set_context(
        self,
        scene: SceneResource | None,
        entity: SceneEntity | None,
    ) -> None:
        self.scene = scene
        self.entity = entity

        self._refresh()

    def _refresh(self) -> None:
        self._updating = True

        try:
            if self.entity is None:
                self.status_label.setText(
                    "Nenhuma entidade selecionada."
                )

                self.add_button.setVisible(
                    False
                )

                self._set_camera_controls_enabled(
                    False
                )

                return

            camera = self.entity.camera

            if camera is None:
                self.status_label.setText(
                    "Esta entidade ainda não possui Camera."
                )

                self.add_button.setVisible(
                    True
                )

                self._set_camera_controls_enabled(
                    False
                )

                return

            self.status_label.setText(
                "Camera anexada a esta entidade."
            )

            self.add_button.setVisible(
                False
            )

            self._set_camera_controls_enabled(
                True
            )

            self.active_checkbox.setChecked(
                camera.active
            )

            self.width_spin.setValue(
                camera.width
            )

            self.height_spin.setValue(
                camera.height
            )

            self.zoom_spin.setValue(
                camera.zoom
            )

            self.offset_x_spin.setValue(
                camera.offset_x
            )

            self.offset_y_spin.setValue(
                camera.offset_y
            )

            self.limit_checkbox.setChecked(
                camera.limit_to_scene
            )

            self.custom_limits_checkbox.setChecked(
                camera.custom_limits_enabled
            )

            self.limit_left_spin.setValue(
                camera.limit_left
            )

            self.limit_top_spin.setValue(
                camera.limit_top
            )

            self.limit_right_spin.setValue(
                camera.limit_right
            )

            self.limit_bottom_spin.setValue(
                camera.limit_bottom
            )

            self.dead_zone_checkbox.setChecked(
                camera.dead_zone_enabled
            )

            self.dead_zone_width_spin.setValue(
                camera.dead_zone_width
            )

            self.dead_zone_height_spin.setValue(
                camera.dead_zone_height
            )

            self.smoothing_checkbox.setChecked(
                camera.smoothing_enabled
            )

            self.smoothing_speed_spin.setValue(
                camera.smoothing_speed
            )

        finally:
            self._updating = False

        self._update_dependency_controls()

    def _set_camera_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        for widget in (
            self.active_checkbox,
            self.width_spin,
            self.height_spin,
            self.zoom_spin,
            self.offset_x_spin,
            self.offset_y_spin,
            self.limit_section,
            self.limit_checkbox,
            self.custom_limits_checkbox,
            self.limit_left_spin,
            self.limit_top_spin,
            self.limit_right_spin,
            self.limit_bottom_spin,
            self.dead_zone_section,
            self.dead_zone_checkbox,
            self.dead_zone_width_spin,
            self.dead_zone_height_spin,
            self.smoothing_section,
            self.smoothing_checkbox,
            self.smoothing_speed_spin,
            self.follow_label,
            self.remove_button,
        ):
            widget.setVisible(
                enabled
            )

    def _update_dependency_controls(
        self,
        *_args,
    ) -> None:
        custom_limits_enabled = (
            self.limit_checkbox.isChecked()
            and self.custom_limits_checkbox.isChecked()
        )

        for widget in (
            self.limit_left_spin,
            self.limit_top_spin,
            self.limit_right_spin,
            self.limit_bottom_spin,
        ):
            widget.setEnabled(
                custom_limits_enabled
            )

        dead_zone_enabled = (
            self.dead_zone_checkbox.isChecked()
        )

        self.dead_zone_width_spin.setEnabled(
            dead_zone_enabled
        )

        self.dead_zone_height_spin.setEnabled(
            dead_zone_enabled
        )

        self.smoothing_speed_spin.setEnabled(
            self.smoothing_checkbox.isChecked()
        )

    def _add_camera(self) -> None:
        if self.entity is None:
            return

        if self.entity.camera is not None:
            return

        width = 480
        height = 270

        if self.scene is not None:
            width = self.scene.width
            height = self.scene.height

        self.entity.camera = CameraComponent(
            active=False,
            width=width,
            height=height,
            zoom=1.0,
            offset_x=0.0,
            offset_y=0.0,
            limit_to_scene=True,
            custom_limits_enabled=False,
            limit_left=0.0,
            limit_top=0.0,
            limit_right=float(width),
            limit_bottom=float(height),
            dead_zone_enabled=False,
            dead_zone_width=80.0,
            dead_zone_height=50.0,
            smoothing_enabled=False,
            smoothing_speed=5.0,
        )

        self.entity.refresh_kind()

        self._refresh()

        self.camera_changed.emit(
            self.entity.id
        )

    def _remove_camera(self) -> None:
        if self.entity is None:
            return

        self.entity.camera = None

        self.entity.refresh_kind()

        self._refresh()

        self.camera_changed.emit(
            self.entity.id
        )

    def _apply(self) -> None:
        if self._updating:
            return

        if (
            self.entity is None
            or self.entity.camera is None
        ):
            return

        camera = self.entity.camera

        requested_active = (
            self.active_checkbox.isChecked()
        )

        if (
            requested_active
            and self.scene is not None
        ):
            self.scene.activate_camera(
                self.entity.id
            )

        else:
            camera.active = (
                requested_active
            )

        camera.width = (
            self.width_spin.value()
        )

        camera.height = (
            self.height_spin.value()
        )

        camera.zoom = max(
            0.05,
            self.zoom_spin.value(),
        )

        camera.offset_x = (
            self.offset_x_spin.value()
        )

        camera.offset_y = (
            self.offset_y_spin.value()
        )

        camera.limit_to_scene = (
            self.limit_checkbox.isChecked()
        )

        camera.custom_limits_enabled = (
            self.custom_limits_checkbox.isChecked()
        )

        camera.limit_left = (
            self.limit_left_spin.value()
        )

        camera.limit_top = (
            self.limit_top_spin.value()
        )

        camera.limit_right = (
            self.limit_right_spin.value()
        )

        camera.limit_bottom = (
            self.limit_bottom_spin.value()
        )

        camera.dead_zone_enabled = (
            self.dead_zone_checkbox.isChecked()
        )

        camera.dead_zone_width = max(
            0.0,
            self.dead_zone_width_spin.value(),
        )

        camera.dead_zone_height = max(
            0.0,
            self.dead_zone_height_spin.value(),
        )

        camera.smoothing_enabled = (
            self.smoothing_checkbox.isChecked()
        )

        camera.smoothing_speed = max(
            0.01,
            self.smoothing_speed_spin.value(),
        )

        self._update_dependency_controls()

        self.camera_changed.emit(
            self.entity.id
        )
