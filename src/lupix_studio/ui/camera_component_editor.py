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

        self.limit_checkbox = VisibleCheckBox(
            "Limitar aos limites da cena"
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
            self.limit_checkbox
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

        self.active_checkbox.toggled.connect(
            self._apply
        )

        self.width_spin.valueChanged.connect(
            self._apply
        )

        self.height_spin.valueChanged.connect(
            self._apply
        )

        self.zoom_spin.valueChanged.connect(
            self._apply
        )

        self.offset_x_spin.valueChanged.connect(
            self._apply
        )

        self.offset_y_spin.valueChanged.connect(
            self._apply
        )

        self.limit_checkbox.toggled.connect(
            self._apply
        )

        self.set_context(
            None,
            None,
        )

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

        finally:
            self._updating = False

    def _set_camera_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        self.active_checkbox.setVisible(
            enabled
        )

        self.width_spin.setVisible(
            enabled
        )

        self.height_spin.setVisible(
            enabled
        )

        self.zoom_spin.setVisible(
            enabled
        )

        self.offset_x_spin.setVisible(
            enabled
        )

        self.offset_y_spin.setVisible(
            enabled
        )

        self.limit_checkbox.setVisible(
            enabled
        )

        self.follow_label.setVisible(
            enabled
        )

        self.remove_button.setVisible(
            enabled
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

        self.camera_changed.emit(
            self.entity.id
        )
