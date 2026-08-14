from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.animation import (
    AnimationClip,
    AnimationComponent,
)
from lupix_studio.scene.model import SceneEntity


class AnimationComponentEditor(QWidget):
    """Editor compacto do componente Animation no Inspector."""

    animation_changed = Signal(str)
    edit_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.entity: SceneEntity | None = None

        self._updating = False

        self.setStyleSheet(
            """
            QCheckBox {
                spacing: 6px;
            }

            QLineEdit,
            QSpinBox,
            QDoubleSpinBox,
            QComboBox {
                min-height: 26px;
                padding-left: 6px;
            }

            QListWidget {
                border: 1px solid #3c4048;
                border-radius: 5px;
                padding: 3px;
            }

            QListWidget::item {
                min-height: 24px;
                padding-left: 5px;
                border-radius: 3px;
            }

            QListWidget::item:selected {
                background-color: #245ec7;
            }

            QPushButton#SmallButton {
                min-width: 32px;
                max-width: 32px;
                min-height: 26px;
                max-height: 26px;
                padding: 0px;
            }

            QPushButton#EditSpriteSheetButton {
                min-height: 30px;
                max-height: 30px;
                font-weight: 600;
            }

            QPushButton#RemoveAnimationButton {
                min-height: 30px;
                max-height: 30px;
                border: 1px solid #d74646;
                border-radius: 5px;
                color: #ff6565;
                background-color: rgba(130, 20, 20, 28);
            }

            QPushButton#RemoveAnimationButton:hover {
                background-color: rgba(160, 30, 30, 55);
            }

            QLabel#SectionLabel {
                font-weight: 600;
            }

            QLabel#HintLabel {
                color: #8d929b;
            }
            """
        )

        # =========================================================
        # COMPONENTE
        # =========================================================

        self.enabled_checkbox = QCheckBox()

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

        self.default_combo = QComboBox()

        # =========================================================
        # LISTA DE ANIMAÇÕES
        # =========================================================

        self.clip_list = QListWidget()

        self.clip_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.clip_list.setMinimumHeight(
            90
        )

        self.clip_list.setMaximumHeight(
            150
        )

        # =========================================================
        # CLIP
        # =========================================================

        self.clip_name_label = QLabel(
            "-"
        )

        self.frames_edit = QLineEdit()

        self.frames_edit.setPlaceholderText(
            "Ex.: 0, 1, 2, 3"
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

        # =========================================================
        # BOTÕES
        # =========================================================

        self.add_component_button = QPushButton(
            "+ Animation"
        )

        self.remove_component_button = QPushButton(
            "Remover Animation"
        )

        self.remove_component_button.setObjectName(
            "RemoveAnimationButton"
        )

        self.add_clip_button = QPushButton(
            "+"
        )

        self.add_clip_button.setObjectName(
            "SmallButton"
        )

        self.add_clip_button.setToolTip(
            "Adicionar animação"
        )

        self.remove_clip_button = QPushButton(
            "−"
        )

        self.remove_clip_button.setObjectName(
            "SmallButton"
        )

        self.remove_clip_button.setToolTip(
            "Remover animação selecionada"
        )

        self.edit_spritesheet_button = QPushButton(
            "Editar Spritesheet"
        )

        self.edit_spritesheet_button.setObjectName(
            "EditSpriteSheetButton"
        )

        self.edit_spritesheet_button.setToolTip(
            "Abrir o editor visual de animação"
        )

        self.editor_hint = QLabel(
            "A seleção visual dos frames, preview e timeline "
            "ficam no Animation Editor."
        )

        self.editor_hint.setObjectName(
            "HintLabel"
        )

        self.editor_hint.setWordWrap(
            True
        )

        # =========================================================
        # FORM COMPONENTE
        # =========================================================

        component_form = QFormLayout()

        component_form.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        component_form.setHorizontalSpacing(
            12
        )

        component_form.setVerticalSpacing(
            8
        )

        component_form.addRow(
            "Ativo:",
            self.enabled_checkbox,
        )

        component_form.addRow(
            "Frame Width:",
            self.frame_width_spin,
        )

        component_form.addRow(
            "Frame Height:",
            self.frame_height_spin,
        )

        component_form.addRow(
            "Padrão:",
            self.default_combo,
        )

        # =========================================================
        # CABEÇALHO ANIMAÇÕES
        # =========================================================

        animations_label = QLabel(
            "Animações"
        )

        animations_label.setObjectName(
            "SectionLabel"
        )

        animation_header = QHBoxLayout()

        animation_header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        animation_header.setSpacing(
            5
        )

        animation_header.addWidget(
            animations_label
        )

        animation_header.addStretch()

        animation_header.addWidget(
            self.add_clip_button
        )

        animation_header.addWidget(
            self.remove_clip_button
        )

        # =========================================================
        # FORM CLIP
        # =========================================================

        clip_form = QFormLayout()

        clip_form.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        clip_form.setHorizontalSpacing(
            12
        )

        clip_form.setVerticalSpacing(
            8
        )

        clip_form.addRow(
            "Nome:",
            self.clip_name_label,
        )

        clip_form.addRow(
            "Frames:",
            self.frames_edit,
        )

        clip_form.addRow(
            "FPS:",
            self.fps_spin,
        )

        clip_form.addRow(
            "Loop:",
            self.loop_checkbox,
        )

        # =========================================================
        # CONTEÚDO
        # =========================================================

        self.component_content = QWidget()

        content_layout = QVBoxLayout(
            self.component_content
        )

        content_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        content_layout.setSpacing(
            9
        )

        content_layout.addLayout(
            component_form
        )

        content_layout.addSpacing(
            4
        )

        content_layout.addLayout(
            animation_header
        )

        content_layout.addWidget(
            self.clip_list
        )

        content_layout.addSpacing(
            4
        )

        content_layout.addLayout(
            clip_form
        )

        content_layout.addSpacing(
            4
        )

        content_layout.addWidget(
            self.edit_spritesheet_button
        )

        content_layout.addWidget(
            self.editor_hint
        )

        content_layout.addSpacing(
            5
        )

        content_layout.addWidget(
            self.remove_component_button
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
            7
        )

        layout.addWidget(
            self.add_component_button
        )

        layout.addWidget(
            self.component_content
        )

        # =========================================================
        # SIGNALS
        # =========================================================

        self.add_component_button.clicked.connect(
            self._add_component
        )

        self.remove_component_button.clicked.connect(
            self._remove_component
        )

        self.add_clip_button.clicked.connect(
            self._add_clip
        )

        self.remove_clip_button.clicked.connect(
            self._remove_clip
        )

        self.edit_spritesheet_button.clicked.connect(
            self._request_editor
        )

        self.clip_list.currentTextChanged.connect(
            self._on_clip_selected
        )

        self.enabled_checkbox.toggled.connect(
            self._apply_component_values
        )

        self.frame_width_spin.valueChanged.connect(
            self._apply_component_values
        )

        self.frame_height_spin.valueChanged.connect(
            self._apply_component_values
        )

        self.default_combo.currentTextChanged.connect(
            self._apply_default_animation
        )

        self.frames_edit.editingFinished.connect(
            self._apply_clip_values
        )

        self.fps_spin.valueChanged.connect(
            self._apply_clip_values
        )

        self.loop_checkbox.toggled.connect(
            self._apply_clip_values
        )

        self.set_context(
            None,
            None,
        )

    # =============================================================
    # CONTEXTO
    # =============================================================

    def set_context(
        self,
        project_root: Path | None,
        entity: SceneEntity | None,
    ) -> None:
        self.project_root = (
            project_root.resolve()
            if project_root is not None
            else None
        )

        self.entity = entity

        self._refresh()

    def _animation(
        self,
    ) -> AnimationComponent | None:
        if self.entity is None:
            return None

        return self.entity.animation

    # =============================================================
    # REFRESH
    # =============================================================

    def _refresh(self) -> None:
        self._updating = True

        try:
            if self.entity is None:
                self.add_component_button.setVisible(
                    False
                )

                self.component_content.setVisible(
                    False
                )

                return

            animation = self._animation()

            has_animation = (
                animation is not None
            )

            self.add_component_button.setVisible(
                not has_animation
            )

            self.component_content.setVisible(
                has_animation
            )

            if animation is None:
                self.clip_list.clear()
                self.default_combo.clear()

                self.clip_name_label.setText(
                    "-"
                )

                self.frames_edit.clear()

                return

            self.enabled_checkbox.setChecked(
                animation.enabled
            )

            self.frame_width_spin.setValue(
                animation.frame_width
            )

            self.frame_height_spin.setValue(
                animation.frame_height
            )

            selected_item = (
                self.clip_list.currentItem()
            )

            selected_name = (
                selected_item.text()
                if selected_item is not None
                else None
            )

            self.clip_list.clear()
            self.default_combo.clear()

            for name in animation.clips:
                self.clip_list.addItem(
                    name
                )

                self.default_combo.addItem(
                    name
                )

            default_index = (
                self.default_combo.findText(
                    animation.default_animation
                )
            )

            if default_index >= 0:
                self.default_combo.setCurrentIndex(
                    default_index
                )

            if selected_name:
                matches = (
                    self.clip_list.findItems(
                        selected_name,
                        Qt.MatchFlag.MatchExactly,
                    )
                )

                if matches:
                    self.clip_list.setCurrentItem(
                        matches[0]
                    )

            if (
                self.clip_list.currentItem()
                is None
                and self.clip_list.count() > 0
            ):
                self.clip_list.setCurrentRow(
                    0
                )

            self._update_clip_list_height()

        finally:
            self._updating = False

        self._refresh_clip_fields()

    def _update_clip_list_height(self) -> None:
        count = self.clip_list.count()

        row_height = 28

        visible_rows = min(
            max(
                count,
                3,
            ),
            5,
        )

        height = (
            visible_rows
            * row_height
            + 10
        )

        self.clip_list.setFixedHeight(
            height
        )

    def _refresh_clip_fields(self) -> None:
        animation = self._animation()

        if animation is None:
            self._set_clip_controls_enabled(
                False
            )
            return

        item = self.clip_list.currentItem()

        if item is None:
            self._updating = True

            try:
                self.clip_name_label.setText(
                    "-"
                )

                self.frames_edit.clear()

                self._set_clip_controls_enabled(
                    False
                )

            finally:
                self._updating = False

            return

        clip = animation.clip(
            item.text()
        )

        if clip is None:
            self._set_clip_controls_enabled(
                False
            )
            return

        self._updating = True

        try:
            self.clip_name_label.setText(
                clip.name
            )

            self.frames_edit.setText(
                ", ".join(
                    str(frame)
                    for frame in clip.frames
                )
            )

            self.fps_spin.setValue(
                clip.fps
            )

            self.loop_checkbox.setChecked(
                clip.loop
            )

            self._set_clip_controls_enabled(
                True
            )

        finally:
            self._updating = False

    def _set_clip_controls_enabled(
        self,
        enabled: bool,
    ) -> None:
        self.frames_edit.setEnabled(
            enabled
        )

        self.fps_spin.setEnabled(
            enabled
        )

        self.loop_checkbox.setEnabled(
            enabled
        )

        self.remove_clip_button.setEnabled(
            enabled
        )

        self.edit_spritesheet_button.setEnabled(
            enabled
        )

    # =============================================================
    # COMPONENTE
    # =============================================================

    def _add_component(self) -> None:
        if self.entity is None:
            return

        self.entity.animation = (
            AnimationComponent()
        )

        self.entity.animation.add_clip(
            AnimationClip(
                name="idle",
                frames=[0],
                fps=6.0,
                loop=True,
            )
        )

        self.entity.animation.default_animation = (
            "idle"
        )

        self._refresh()

        self._emit_changed()

    def _remove_component(self) -> None:
        if self.entity is None:
            return

        self.entity.animation = None

        self._refresh()

        self._emit_changed()

    # =============================================================
    # CLIPS
    # =============================================================

    def _add_clip(self) -> None:
        animation = self._animation()

        if animation is None:
            return

        name, accepted = (
            QInputDialog.getText(
                self,
                "Nova Animação",
                "Nome:",
                text="animation",
            )
        )

        if not accepted:
            return

        name = name.strip()

        if not name:
            return

        if animation.clip(
            name
        ) is not None:
            return

        animation.add_clip(
            AnimationClip(
                name=name,
                frames=[0],
                fps=6.0,
                loop=True,
            )
        )

        if len(animation.clips) == 1:
            animation.default_animation = (
                name
            )

        self._refresh()

        matches = self.clip_list.findItems(
            name,
            Qt.MatchFlag.MatchExactly,
        )

        if matches:
            self.clip_list.setCurrentItem(
                matches[0]
            )

        self._emit_changed()

    def _remove_clip(self) -> None:
        animation = self._animation()

        if animation is None:
            return

        item = self.clip_list.currentItem()

        if item is None:
            return

        name = item.text()

        animation.remove_clip(
            name
        )

        if (
            animation.default_animation
            == name
        ):
            if animation.clips:
                animation.default_animation = next(
                    iter(animation.clips)
                )
            else:
                animation.default_animation = ""

        self._refresh()

        self._emit_changed()

    def _on_clip_selected(
        self,
        name: str,
    ) -> None:
        del name

        if self._updating:
            return

        self._refresh_clip_fields()

    def _request_editor(self) -> None:
        if self.entity is None:
            return

        item = self.clip_list.currentItem()

        if item is None:
            return

        entity_id = str(
            self.entity.id
        )

        clip_name = str(
            item.text()
        )

        self.edit_requested.emit(
            entity_id,
            clip_name,
        )

    # =============================================================
    # ALTERAÇÕES
    # =============================================================

    def _apply_component_values(self) -> None:
        if self._updating:
            return

        animation = self._animation()

        if animation is None:
            return

        animation.enabled = (
            self.enabled_checkbox.isChecked()
        )

        animation.frame_width = (
            self.frame_width_spin.value()
        )

        animation.frame_height = (
            self.frame_height_spin.value()
        )

        self._emit_changed()

    def _apply_default_animation(
        self,
        name: str,
    ) -> None:
        if self._updating:
            return

        animation = self._animation()

        if (
            animation is None
            or not name
        ):
            return

        animation.default_animation = name

        self._emit_changed()

    def _apply_clip_values(self) -> None:
        if self._updating:
            return

        animation = self._animation()

        if animation is None:
            return

        item = self.clip_list.currentItem()

        if item is None:
            return

        clip = animation.clip(
            item.text()
        )

        if clip is None:
            return

        clip.frames = self._parse_frames(
            self.frames_edit.text()
        )

        clip.fps = max(
            0.01,
            self.fps_spin.value(),
        )

        clip.loop = (
            self.loop_checkbox.isChecked()
        )

        self._emit_changed()

    # =============================================================
    # UTILITÁRIOS
    # =============================================================

    @staticmethod
    def _parse_frames(
        text: str,
    ) -> list[int]:
        frames: list[int] = []

        for part in text.split(","):
            value = part.strip()

            if not value:
                continue

            try:
                frame = int(
                    value
                )

            except ValueError:
                continue

            frames.append(
                max(
                    0,
                    frame,
                )
            )

        return frames

    def _emit_changed(self) -> None:
        if self.entity is None:
            return

        self.animation_changed.emit(
            self.entity.id
        )
