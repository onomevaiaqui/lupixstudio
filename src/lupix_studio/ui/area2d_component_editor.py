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
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import (
    Area2DComponent,
    SceneEntity,
    SceneResource,
)


class Area2DComponentEditor(QWidget):
    """Editor do componente Area2D."""

    area2d_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.scene: SceneResource | None = None
        self.entity: SceneEntity | None = None
        self._updating = False

        self.status_label = QLabel(
            "Nenhuma entidade selecionada."
        )
        self.status_label.setWordWrap(True)

        self.add_button = QPushButton(
            "Adicionar Area2D"
        )

        self.enabled_checkbox = QCheckBox(
            "Ativa"
        )
        self.detect_player_checkbox = QCheckBox(
            "Detectar Player"
        )
        self.debug_visible_checkbox = QCheckBox(
            "Mostrar área no editor"
        )

        self.width_spin = self._size_spin(64.0)
        self.height_spin = self._size_spin(64.0)
        self.offset_x_spin = self._offset_spin()
        self.offset_y_spin = self._offset_spin()

        size_form = QFormLayout()
        size_form.addRow("Largura:", self.width_spin)
        size_form.addRow("Altura:", self.height_spin)
        size_form.addRow("Offset X:", self.offset_x_spin)
        size_form.addRow("Offset Y:", self.offset_y_spin)

        self.events_title = QLabel("Eventos")
        self.events_title.setStyleSheet(
            "font-weight: 600; margin-top: 8px;"
        )

        self.enter_action_combo = QComboBox()
        self.enter_action_combo.addItem(
            "Nenhuma",
            "none",
        )
        self.enter_action_combo.addItem(
            "Trocar Cena",
            "change_scene",
        )

        self.target_scene_combo = QComboBox()
        self.target_scene_combo.setMinimumWidth(180)

        self.refresh_scenes_button = QPushButton("↻")
        self.refresh_scenes_button.setToolTip(
            "Atualizar lista de cenas"
        )
        self.refresh_scenes_button.setFixedWidth(34)

        selector_layout = QHBoxLayout()
        selector_layout.setContentsMargins(0, 0, 0, 0)
        selector_layout.addWidget(self.target_scene_combo)
        selector_layout.addWidget(self.refresh_scenes_button)

        selector_widget = QWidget()
        selector_widget.setLayout(selector_layout)

        event_form = QFormLayout()
        event_form.addRow(
            "Ao entrar:",
            self.enter_action_combo,
        )
        event_form.addRow(
            "Cena destino:",
            selector_widget,
        )

        self.hint_label = QLabel(
            "A lista mostra automaticamente as cenas "
            "salvas na pasta scenes do projeto."
        )
        self.hint_label.setWordWrap(True)

        self.remove_button = QPushButton(
            "Remover Area2D"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.status_label)
        layout.addWidget(self.add_button)
        layout.addWidget(self.enabled_checkbox)
        layout.addLayout(size_form)
        layout.addWidget(self.detect_player_checkbox)
        layout.addWidget(self.debug_visible_checkbox)
        layout.addWidget(self.events_title)
        layout.addLayout(event_form)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.remove_button)
        layout.addStretch()

        self.add_button.clicked.connect(
            self._add_area2d
        )
        self.remove_button.clicked.connect(
            self._remove_area2d
        )

        self.enabled_checkbox.toggled.connect(
            self._apply
        )
        self.detect_player_checkbox.toggled.connect(
            self._apply
        )
        self.debug_visible_checkbox.toggled.connect(
            self._apply
        )
        self.width_spin.valueChanged.connect(
            self._apply
        )
        self.height_spin.valueChanged.connect(
            self._apply
        )
        self.offset_x_spin.valueChanged.connect(
            self._apply
        )
        self.offset_y_spin.valueChanged.connect(
            self._apply
        )
        self.enter_action_combo.currentIndexChanged.connect(
            self._on_action_changed
        )
        self.target_scene_combo.currentIndexChanged.connect(
            self._apply
        )
        self.refresh_scenes_button.clicked.connect(
            self.refresh_scene_list
        )

        self.set_context(
            None,
            None,
            None,
        )

    @staticmethod
    def _size_spin(
        value: float,
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(1.0, 100000.0)
        spin.setDecimals(1)
        spin.setValue(value)
        return spin

    @staticmethod
    def _offset_spin() -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(-100000.0, 100000.0)
        spin.setDecimals(1)
        return spin

    def set_context(
        self,
        scene: SceneResource | None,
        entity: SceneEntity | None,
        project_root: Path | None = None,
    ) -> None:
        self.scene = scene
        self.entity = entity

        if project_root is not None:
            self.project_root = Path(
                project_root
            ).resolve()
        elif scene is None:
            self.project_root = None

        self._refresh()

    def refresh_scene_list(
        self,
    ) -> None:
        selected_path = ""

        if (
            self.entity is not None
            and self.entity.area2d is not None
        ):
            selected_path = (
                self.entity.area2d.target_scene
            )

        self._populate_scene_combo(
            selected_path
        )

    def _populate_scene_combo(
        self,
        selected_path: str = "",
    ) -> None:
        previous_updating = self._updating
        self._updating = True

        try:
            self.target_scene_combo.clear()
            self.target_scene_combo.addItem(
                "Selecione uma cena...",
                "",
            )

            if self.project_root is None:
                self.target_scene_combo.addItem(
                    "Projeto não carregado",
                    "",
                )
                return

            scenes_dir = (
                self.project_root
                / "scenes"
            )

            if not scenes_dir.exists():
                self.target_scene_combo.addItem(
                    "Nenhuma pasta scenes encontrada",
                    "",
                )
                return

            scene_files = sorted(
                scenes_dir.rglob("*.scene"),
                key=lambda path: str(
                    path.relative_to(
                        scenes_dir
                    )
                ).lower(),
            )

            if not scene_files:
                self.target_scene_combo.addItem(
                    "Nenhuma cena salva",
                    "",
                )
                return

            normalized_selected = (
                selected_path.replace(
                    "\\",
                    "/",
                )
            )

            selected_index = 0

            for scene_path in scene_files:
                relative_project = (
                    scene_path.relative_to(
                        self.project_root
                    )
                )

                stored_path = (
                    relative_project.as_posix()
                )

                display_path = (
                    scene_path.relative_to(
                        scenes_dir
                    )
                )

                display_name = (
                    display_path.with_suffix(
                        ""
                    ).as_posix()
                )

                self.target_scene_combo.addItem(
                    display_name,
                    stored_path,
                )

                if stored_path == normalized_selected:
                    selected_index = (
                        self.target_scene_combo.count()
                        - 1
                    )

            self.target_scene_combo.setCurrentIndex(
                selected_index
            )

        finally:
            self._updating = previous_updating

    def _refresh(self) -> None:
        self._updating = True

        try:
            if self.entity is None:
                self.status_label.setText(
                    "Nenhuma entidade selecionada."
                )
                self.add_button.setVisible(False)
                self._set_controls_visible(False)
                return

            area = self.entity.area2d

            if area is None:
                self.status_label.setText(
                    "Esta entidade ainda não possui Area2D."
                )
                self.add_button.setVisible(True)
                self._set_controls_visible(False)
                return

            self.status_label.setText(
                "Area2D anexada a esta entidade."
            )
            self.add_button.setVisible(False)
            self._set_controls_visible(True)

            self.enabled_checkbox.setChecked(
                area.enabled
            )
            self.width_spin.setValue(area.width)
            self.height_spin.setValue(area.height)
            self.offset_x_spin.setValue(
                area.offset_x
            )
            self.offset_y_spin.setValue(
                area.offset_y
            )
            self.detect_player_checkbox.setChecked(
                area.detect_player
            )
            self.debug_visible_checkbox.setChecked(
                area.debug_visible
            )

            action_index = (
                self.enter_action_combo.findData(
                    area.on_enter_action
                )
            )

            action_index = max(action_index, 0)

            self.enter_action_combo.setCurrentIndex(
                action_index
            )

            self._populate_scene_combo(
                area.target_scene
            )

            self._update_target_scene_state()

        finally:
            self._updating = False

    def _set_controls_visible(
        self,
        visible: bool,
    ) -> None:
        for widget in (
            self.enabled_checkbox,
            self.width_spin,
            self.height_spin,
            self.offset_x_spin,
            self.offset_y_spin,
            self.detect_player_checkbox,
            self.debug_visible_checkbox,
            self.events_title,
            self.enter_action_combo,
            self.target_scene_combo,
            self.refresh_scenes_button,
            self.hint_label,
            self.remove_button,
        ):
            widget.setVisible(visible)

        if visible:
            self._update_target_scene_state()

    def _update_target_scene_state(
        self,
    ) -> None:
        enabled = (
            self.enter_action_combo.currentData()
            == "change_scene"
        )

        self.target_scene_combo.setEnabled(
            enabled
        )
        self.refresh_scenes_button.setEnabled(
            enabled
        )

    def _on_action_changed(
        self,
    ) -> None:
        self._update_target_scene_state()
        self._apply()

    def _add_area2d(
        self,
    ) -> None:
        if self.entity is None:
            return

        if self.entity.area2d is not None:
            return

        self.entity.area2d = Area2DComponent()
        self.entity.refresh_kind()
        self._refresh()

        self.area2d_changed.emit(
            self.entity.id
        )

    def _remove_area2d(
        self,
    ) -> None:
        if self.entity is None:
            return

        self.entity.area2d = None
        self.entity.refresh_kind()
        self._refresh()

        self.area2d_changed.emit(
            self.entity.id
        )

    def _apply(
        self,
    ) -> None:
        if self._updating:
            return

        if (
            self.entity is None
            or self.entity.area2d is None
        ):
            return

        area = self.entity.area2d

        area.enabled = (
            self.enabled_checkbox.isChecked()
        )
        area.width = max(
            1.0,
            self.width_spin.value(),
        )
        area.height = max(
            1.0,
            self.height_spin.value(),
        )
        area.offset_x = (
            self.offset_x_spin.value()
        )
        area.offset_y = (
            self.offset_y_spin.value()
        )
        area.detect_player = (
            self.detect_player_checkbox.isChecked()
        )
        area.debug_visible = (
            self.debug_visible_checkbox.isChecked()
        )
        area.on_enter_action = str(
            self.enter_action_combo.currentData()
            or "none"
        )
        area.target_scene = str(
            self.target_scene_combo.currentData()
            or ""
        )

        self.area2d_changed.emit(
            self.entity.id
        )
