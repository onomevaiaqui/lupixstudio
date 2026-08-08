from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
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


class CameraComponentEditor(QWidget):
    """Editor do componente Camera."""

    camera_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.scene: SceneResource | None = None
        self.entity: SceneEntity | None = None

        self._updating = False

        self.active_checkbox = QCheckBox()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(
            1,
            8192,
        )
        self.width_spin.setValue(
            480
        )

        self.height_spin = QSpinBox()
        self.height_spin.setRange(
            1,
            8192,
        )
        self.height_spin.setValue(
            270
        )

        self.zoom_spin = QDoubleSpinBox()
        self.zoom_spin.setRange(
            0.01,
            100.0,
        )
        self.zoom_spin.setDecimals(
            2
        )
        self.zoom_spin.setSingleStep(
            0.1
        )
        self.zoom_spin.setValue(
            1.0
        )

        self.add_button = QPushButton(
            "Adicionar Camera"
        )

        self.remove_button = QPushButton(
            "Remover Camera"
        )

        form = QFormLayout()

        form.addRow(
            "Ativa:",
            self.active_checkbox,
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
            "Zoom:",
            self.zoom_spin,
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

        self.active_checkbox.toggled.connect(
            self._apply_values
        )

        self.width_spin.valueChanged.connect(
            self._apply_values
        )

        self.height_spin.valueChanged.connect(
            self._apply_values
        )

        self.zoom_spin.valueChanged.connect(
            self._apply_values
        )

        self.add_button.clicked.connect(
            self._add_camera
        )

        self.remove_button.clicked.connect(
            self._remove_camera
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

            camera = self.entity.camera

            has_camera = (
                camera is not None
            )

            self.add_button.setVisible(
                not has_camera
            )

            self.remove_button.setVisible(
                has_camera
            )

            self.active_checkbox.setEnabled(
                has_camera
            )

            self.width_spin.setEnabled(
                has_camera
            )

            self.height_spin.setEnabled(
                has_camera
            )

            self.zoom_spin.setEnabled(
                has_camera
            )

            if camera is None:
                self.active_checkbox.setChecked(
                    False
                )

                self.width_spin.setValue(
                    self.scene.width
                    if self.scene is not None
                    else 480
                )

                self.height_spin.setValue(
                    self.scene.height
                    if self.scene is not None
                    else 270
                )

                self.zoom_spin.setValue(
                    1.0
                )

                return

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

        finally:
            self._updating = False

    def _add_camera(self) -> None:
        if self.entity is None:
            return

        width = 480
        height = 270

        if self.scene is not None:
            width = self.scene.width
            height = self.scene.height

        self.entity.camera = CameraComponent(
            width=width,
            height=height,
        )

        self.entity.refresh_kind()

        self._refresh_values()

        self.camera_changed.emit(
            self.entity.id
        )

    def _remove_camera(self) -> None:
        if self.entity is None:
            return

        self.entity.camera = None
        self.entity.refresh_kind()

        self._refresh_values()

        self.camera_changed.emit(
            self.entity.id
        )

    def _apply_values(self) -> None:
        if (
            self.entity is None
            or self.entity.camera is None
            or self._updating
        ):
            return

        camera = self.entity.camera

        if (
            self.active_checkbox.isChecked()
            and self.scene is not None
        ):
            self.scene.activate_camera(
                self.entity.id
            )
        else:
            camera.active = False

        camera.width = (
            self.width_spin.value()
        )

        camera.height = (
            self.height_spin.value()
        )

        camera.zoom = (
            self.zoom_spin.value()
        )

        self.camera_changed.emit(
            self.entity.id
        )