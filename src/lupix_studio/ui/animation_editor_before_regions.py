from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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

        self.setObjectName(
            "AnimationEditor"
        )

        self.setStyleSheet(
            """
            QWidget#AnimationEditor {
                background-color: #17191d;
            }

            QFrame#TopBar {
                background-color: #202329;
                border-bottom: 1px solid #343840;
            }

            QFrame#ToolBar {
                background-color: #1d2025;
                border: 1px solid #343840;
                border-radius: 6px;
            }

            QFrame#EditorArea {
                background-color: #14161a;
                border: 1px solid #343840;
                border-radius: 6px;
            }

            QLabel#EditorTitle {
                font-size: 16px;
                font-weight: 600;
            }

            QLabel#EntityLabel {
                color: #9ca3af;
            }

            QLabel#FieldLabel {
                color: #b6bbc5;
            }

            QLabel#StatusLabel {
                color: #9096a1;
            }

            QPushButton {
                min-height: 28px;
                padding-left: 10px;
                padding-right: 10px;
            }

            QPushButton#BackButton {
                min-width: 125px;
            }

            QPushButton#SaveButton {
                min-width: 130px;
                font-weight: 600;
            }

            QComboBox,
            QSpinBox,
            QDoubleSpinBox {
                min-height: 28px;
                min-width: 90px;
            }
            """
        )

        # =========================================================
        # TOPO
        # =========================================================

        self.back_button = QPushButton(
            "← Voltar para Cena"
        )

        self.back_button.setObjectName(
            "BackButton"
        )

        self.title_label = QLabel(
            "Animation Editor"
        )

        self.title_label.setObjectName(
            "EditorTitle"
        )

        self.entity_label = QLabel(
            "Nenhuma entidade"
        )

        self.entity_label.setObjectName(
            "EntityLabel"
        )

        self.top_bar = QFrame()

        self.top_bar.setObjectName(
            "TopBar"
        )

        top_layout = QHBoxLayout(
            self.top_bar
        )

        top_layout.setContentsMargins(
            12,
            8,
            12,
            8,
        )

        top_layout.setSpacing(
            10
        )

        top_layout.addWidget(
            self.back_button
        )

        top_layout.addWidget(
            self.title_label
        )

        top_layout.addSpacing(
            8
        )

        top_layout.addWidget(
            self.entity_label
        )

        top_layout.addStretch()

        # =========================================================
        # BARRA DE CONFIGURAÇÕES
        # =========================================================

        self.clip_label = QLabel(
            "Animação"
        )

        self.clip_label.setObjectName(
            "FieldLabel"
        )

        self.clip_combo = QComboBox()

        self.clip_combo.setMinimumWidth(
            150
        )

        self.frame_width_label = QLabel(
            "Frame W"
        )

        self.frame_width_label.setObjectName(
            "FieldLabel"
        )

        self.frame_width_spin = QSpinBox()

        self.frame_width_spin.setRange(
            1,
            4096,
        )

        self.frame_width_spin.setSuffix(
            " px"
        )

        self.frame_height_label = QLabel(
            "Frame H"
        )

        self.frame_height_label.setObjectName(
            "FieldLabel"
        )

        self.frame_height_spin = QSpinBox()

        self.frame_height_spin.setRange(
            1,
            4096,
        )

        self.frame_height_spin.setSuffix(
            " px"
        )

        self.fps_label = QLabel(
            "FPS"
        )

        self.fps_label.setObjectName(
            "FieldLabel"
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

        self.loop_checkbox = QCheckBox(
            "Loop"
        )

        self.save_button = QPushButton(
            "Salvar Animação"
        )

        self.save_button.setObjectName(
            "SaveButton"
        )

        self.tool_bar = QFrame()

        self.tool_bar.setObjectName(
            "ToolBar"
        )

        toolbar_layout = QHBoxLayout(
            self.tool_bar
        )

        toolbar_layout.setContentsMargins(
            10,
            7,
            10,
            7,
        )

        toolbar_layout.setSpacing(
            8
        )

        toolbar_layout.addWidget(
            self.clip_label
        )

        toolbar_layout.addWidget(
            self.clip_combo
        )

        toolbar_layout.addSpacing(
            10
        )

        toolbar_layout.addWidget(
            self.frame_width_label
        )

        toolbar_layout.addWidget(
            self.frame_width_spin
        )

        toolbar_layout.addWidget(
            self.frame_height_label
        )

        toolbar_layout.addWidget(
            self.frame_height_spin
        )

        toolbar_layout.addSpacing(
            10
        )

        toolbar_layout.addWidget(
            self.fps_label
        )

        toolbar_layout.addWidget(
            self.fps_spin
        )

        toolbar_layout.addWidget(
            self.loop_checkbox
        )

        toolbar_layout.addStretch()

        toolbar_layout.addWidget(
            self.save_button
        )

        # =========================================================
        # EDITOR DE SPRITESHEET
        # =========================================================

        self.spritesheet_editor = (
            AnimationSpriteSheetEditor()
        )

        self.spritesheet_editor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.editor_scroll = QScrollArea()

        self.editor_scroll.setWidgetResizable(
            True
        )

        self.editor_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.editor_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.editor_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.editor_scroll.setWidget(
            self.spritesheet_editor
        )

        self.editor_frame = QFrame()

        self.editor_frame.setObjectName(
            "EditorArea"
        )

        editor_frame_layout = QVBoxLayout(
            self.editor_frame
        )

        editor_frame_layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        editor_frame_layout.addWidget(
            self.editor_scroll
        )

        # =========================================================
        # STATUS
        # =========================================================

        self.status_label = QLabel(
            "Nenhuma animação aberta."
        )

        self.status_label.setObjectName(
            "StatusLabel"
        )

        self.status_label.setMinimumHeight(
            24
        )

        # =========================================================
        # LAYOUT PRINCIPAL
        # =========================================================

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
            0
        )

        layout.addWidget(
            self.top_bar
        )

        content = QWidget()

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            10,
            10,
            10,
            8,
        )

        content_layout.setSpacing(
            8
        )

        content_layout.addWidget(
            self.tool_bar
        )

        content_layout.addWidget(
            self.editor_frame,
            1,
        )

        content_layout.addWidget(
            self.status_label
        )

        layout.addWidget(
            content,
            1,
        )

        # =========================================================
        # SIGNALS
        # =========================================================

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

    # =============================================================
    # CONTEXTO
    # =============================================================

    def clear(self) -> None:
        self.project_root = None
        self.entity = None

        self._updating = True

        try:
            self.entity_label.setText(
                "Nenhuma entidade"
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
        self.project_root = (
            project_root.resolve()
        )

        self.entity = entity

        animation = entity.animation

        if animation is None:
            self.clear()
            return

        self._updating = True

        try:
            self.entity_label.setText(
                f"Entidade: {entity.name}"
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

            target_name = clip_name

            if (
                not target_name
                or animation.clip(
                    target_name
                ) is None
            ):
                target_name = (
                    animation.default_animation
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

    # =============================================================
    # ACESSO AOS DADOS
    # =============================================================

    def current_clip_name(
        self,
    ) -> str:
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

    # =============================================================
    # TROCA DE CLIP
    # =============================================================

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
                "Editando: "
                f"{self.entity.name} > {clip.name} | "
                f"{len(clip.frames)} frame(s)"
            )

            self._set_controls_enabled(
                True
            )

        finally:
            self._updating = False

    # =============================================================
    # FRAME SIZE
    # =============================================================

    def _apply_component_values(
        self,
    ) -> None:
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

    # =============================================================
    # FPS / LOOP
    # =============================================================

    def _apply_clip_values(
        self,
    ) -> None:
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

        self.status_label.setText(
            f"{clip.name} | "
            f"{len(clip.frames)} frame(s) | "
            f"{clip.fps:.2f} FPS"
        )

        self._emit_changed()

    # =============================================================
    # FRAMES
    # =============================================================

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
            f"{clip.name} | "
            f"{len(clip.frames)} frame(s) selecionado(s)"
        )

        self._emit_changed()

    # =============================================================
    # SALVAR
    # =============================================================

    def _save(self) -> None:
        clip = self._current_clip()

        if clip is None:
            return

        self._apply_clip_values()

        self._emit_changed()

        self.status_label.setText(
            "Animação salva: "
            f"{clip.name} | "
            f"{len(clip.frames)} frame(s)"
        )

    # =============================================================
    # ESTADO DOS CONTROLES
    # =============================================================

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

        self.editor_scroll.setEnabled(
            enabled
        )

        self.save_button.setEnabled(
            enabled
        )

    # =============================================================
    # ALTERAÇÃO DA CENA
    # =============================================================

    def _emit_changed(self) -> None:
        if self.entity is None:
            return

        entity_id = str(
            self.entity.id
        )

        self.animation_changed.emit(
            entity_id
        )