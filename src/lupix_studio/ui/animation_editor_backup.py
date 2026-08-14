from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import SceneEntity
from lupix_studio.ui.animation_spritesheet_editor import (
    AnimationSpriteSheetEditor,
)


class AnimationEditor(QWidget):
    """Editor visual de animações exibido no workspace."""

    back_requested = Signal()
    animation_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.entity: SceneEntity | None = None

        self._updating = False

        self.back_button = QPushButton(
            "← Voltar para Cena"
        )

        self.title = QLabel(
            "Animation Editor"
        )

        self.title.setStyleSheet(
            "font-size: 16px; font-weight: 600;"
        )

        self.entity_label = QLabel(
            "-"
        )

        self.clip_combo = QComboBox()

        self.frame_width_spin = QSpinBox()
        self.frame_width_spin.setRange(
            1,
            4096,
        )

        self.frame_height_spin = QSpinBox()
        self.frame_height_spin.setRange(
            1,
            4096,
        )

        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(
            0.01,
            240.0,
        )
        self.fps_spin.setDecimals(
            2
        )
        self.fps_spin.setSingleStep(
            1.0
        )

        self.loop_checkbox = QCheckBox()

        self.save_button = QPushButton(
            "Salvar Animação"
        )

        self.save_button.setMinimumHeight(
            30
        )

        self.status_label = QLabel(
            "Selecione uma animação."
        )

        self.status_label.setStyleSheet(
            "color: #8d929b;"
        )

        self.spritesheet_editor = (
            AnimationSpriteSheetEditor()
        )

        self.spritesheet_scroll = QScrollArea()
        self.spritesheet_scroll.setWidgetResizable(
            True
        )
        self.spritesheet_scroll.setWidget(
            self.spritesheet_editor
        )

        header = QHBoxLayout()
        header.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        header.setSpacing(
            10
        )

        header.addWidget(
            self.back_button
        )
        header.addWidget(
            self.title
        )
        header.addSpacing(
            8
        )
        header.addWidget(
            self.entity_label
        )
        header.addStretch()

        controls = QFormLayout()
        controls.setHorizontalSpacing(
            12
        )
        controls.setVerticalSpacing(
            8
        )

        controls.addRow(
            "Animação:",
            self.clip_combo,
        )
        controls.addRow(
            "Frame Width:",
            self.frame_width_spin,
        )
        controls.addRow(
            "Frame Height:",
            self.frame_height_spin,
        )
        controls.addRow(
            "FPS:",
            self.fps_spin,
        )
        controls.addRow(
            "Loop:",
            self.loop_checkbox,
        )

        top_controls = QHBoxLayout()
        top_controls.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        controls_widget = QWidget()
        controls_widget.setLayout(
            controls
        )

        top_controls.addWidget(
            controls_widget
        )
        top_controls.addStretch()

        save_row = QHBoxLayout()
        save_row.addWidget(
            self.status_label
        )
        save_row.addStretch()
        save_row.addWidget(
            self.save_button
        )

        layout = QVBoxLayout(
            self
        )
        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )
        layout.setSpacing(
            10
        )

        layout.addLayout(
            header
        )
        layout.addLayout(
            top_controls
        )
        layout.addWidget(
            self.spritesheet_scroll,
            1,
        )
        layout.addLayout(
            save_row
        )

        self.back_button.clicked.connect(
            self.back_requested.emit
        )

        self.clip_combo.currentTextChanged.connect(
            self._on_clip_changed
        )

        self.frame_width_spin.valueChanged.connect(
            self._apply_component_values
        )

        self.frame_height_spin.valueChanged.connect(
            self._apply_component_values
        )

        self.fps_spin.valueChanged.connect(
            self._apply_clip_values
        )

        self.loop_checkbox.toggled.connect(
            self._apply_clip_values
        )

        self.spritesheet_editor.frames_changed.connect(
            self._on_frames_changed
        )

        self.save_button.clicked.connect(
            self._save
        )

        self.clear()

    def clear(self) -> None:
        self.project_root = None
        self.entity = None

        self._updating = True

        try:
            self.entity_label.setText(
                "-"
            )
            self.clip_combo.clear()

            self.frame_width_spin.setValue(
                16
            )
            self.frame_height_spin.setValue(
                16
            )
            self.fps_spin.setValue(
                6.0
            )
            self.loop_checkbox.setChecked(
                True
            )

            self.spritesheet_editor.set_context(
                None,
                None,
            )
            self.spritesheet_editor.set_frames(
                []
            )

            self.status_label.setText(
                "Nenhuma animação aberta."
            )

            self._set_controls_enabled(
                False
            )

        finally:
            self._updating = False

    def open_animation(
        self,
        project_root: Path,
        entity: SceneEntity,
        clip_name: str | None = None,
    ) -> None:
        self.project_root = project_root.resolve()
        self.entity = entity

        animation = entity.animation

        if animation is None:
            self.clear()
            return

        self._updating = True

        try:
            self.entity_label.setText(
                entity.name
            )

            self.clip_combo.clear()

            for name in animation.clips:
                self.clip_combo.addItem(
                    name
                )

            self.frame_width_spin.setValue(
                animation.frame_width
            )

            self.frame_height_spin.setValue(
                animation.frame_height
            )

            target_name = (
                clip_name
                if (
                    clip_name
                    and animation.clip(
                        clip_name
                    ) is not None
                )
                else animation.default_animation
            )

            index = self.clip_combo.findText(
                target_name
            )

            if (
                index < 0
                and self.clip_combo.count() > 0
            ):
                index = 0

            if index >= 0:
                self.clip_combo.setCurrentIndex(
                    index
                )

            self.spritesheet_editor.set_context(
                self.project_root,
                entity,
            )

            self.spritesheet_editor.set_frame_size(
                animation.frame_width,
                animation.frame_height,
            )

            self._set_controls_enabled(
                self.clip_combo.count() > 0
            )

        finally:
            self._updating = False

        self._refresh_clip()

    def current_clip_name(self) -> str:
        return self.clip_combo.currentText()

    def _animation(self):
        if (
            self.entity is None
            or self.entity.animation is None
        ):
            return None

        return self.entity.animation

    def _current_clip(self):
        animation = self._animation()

        if animation is None:
            return None

        name = self.clip_combo.currentText()

        if not name:
            return None

        return animation.clip(
            name
        )

    def _on_clip_changed(
        self,
        name: str,
    ) -> None:
        del name

        if self._updating:
            return

        self._refresh_clip()

    def _refresh_clip(self) -> None:
        animation = self._animation()
        clip = self._current_clip()

        if (
            animation is None
            or clip is None
        ):
            self.spritesheet_editor.set_frames(
                []
            )
            self._set_controls_enabled(
                False
            )
            return

        self._updating = True

        try:
            self.frame_width_spin.setValue(
                animation.frame_width
            )

            self.frame_height_spin.setValue(
                animation.frame_height
            )

            self.fps_spin.setValue(
                clip.fps
            )

            self.loop_checkbox.setChecked(
                clip.loop
            )

            self.spritesheet_editor.set_frame_size(
                animation.frame_width,
                animation.frame_height,
            )

            self.spritesheet_editor.set_frames(
                list(
                    clip.frames
                )
            )

            self.spritesheet_editor.set_preview_settings(
                frames=list(
                    clip.frames
                ),
                fps=clip.fps,
                loop=clip.loop,
            )

            self.status_label.setText(
                f"Editando: {entity_name(self.entity)} > {clip.name}"
            )

            self._set_controls_enabled(
                True
            )

        finally:
            self._updating = False

    def _apply_component_values(self) -> None:
        if self._updating:
            return

        animation = self._animation()

        if animation is None:
            return

        animation.frame_width = (
            self.frame_width_spin.value()
        )

        animation.frame_height = (
            self.frame_height_spin.value()
        )

        self.spritesheet_editor.set_frame_size(
            animation.frame_width,
            animation.frame_height,
        )

        self._refresh_clip()
        self._emit_changed()

    def _apply_clip_values(self) -> None:
        if self._updating:
            return

        clip = self._current_clip()

        if clip is None:
            return

        clip.fps = max(
            0.01,
            self.fps_spin.value(),
        )

        clip.loop = (
            self.loop_checkbox.isChecked()
        )

        self.spritesheet_editor.set_preview_settings(
            frames=list(
                clip.frames
            ),
            fps=clip.fps,
            loop=clip.loop,
        )

        self._emit_changed()

    def _on_frames_changed(
        self,
        frames: list[int],
    ) -> None:
        if self._updating:
            return

        clip = self._current_clip()

        if clip is None:
            return

        clip.frames = list(
            frames
        )

        self.spritesheet_editor.set_preview_settings(
            frames=list(
                clip.frames
            ),
            fps=clip.fps,
            loop=clip.loop,
        )

        self.status_label.setText(
            f"{len(clip.frames)} frame(s) em {clip.name}"
        )

        self._emit_changed()

    def _save(self) -> None:
        self._apply_clip_values()
        self._emit_changed()

        clip = self._current_clip()

        if clip is not None:
            self.status_label.setText(
                f"Animação salva: {clip.name}"
            )

    def _set_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        self.clip_combo.setEnabled(
            enabled
        )
        self.frame_width_spin.setEnabled(
            enabled
        )
        self.frame_height_spin.setEnabled(
            enabled
        )
        self.fps_spin.setEnabled(
            enabled
        )
        self.loop_checkbox.setEnabled(
            enabled
        )
        self.spritesheet_scroll.setEnabled(
            enabled
        )
        self.save_button.setEnabled(
            enabled
        )

    def _emit_changed(self) -> None:
        if self.entity is None:
            return

        self.animation_changed.emit(
            self.entity.id
        )


def entity_name(
    entity: SceneEntity | None,
) -> str:
    if entity is None:
        return "-"

    return entity.name
