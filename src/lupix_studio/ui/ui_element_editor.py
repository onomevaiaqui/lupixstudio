from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import SceneEntity


class UIElementEditor(QWidget):
    element_changed = Signal(str)
    center_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.entity: SceneEntity | None = None
        self._updating = False
        self.type_combo = QComboBox()
        self.type_combo.addItem("Texto", "text")
        self.type_combo.addItem("Imagem", "image")
        self.type_combo.addItem("Botão", "button")
        self.text_edit = QLineEdit()
        self.asset_edit = QLineEdit()
        self.asset_button = QPushButton("Escolher imagem...")
        self.asset_row = QWidget()
        asset_layout = QHBoxLayout(self.asset_row)
        asset_layout.setContentsMargins(0, 0, 0, 0)
        asset_layout.addWidget(self.asset_edit, 1)
        asset_layout.addWidget(self.asset_button)
        self.font_edit = QLineEdit()
        self.color_edit = QLineEdit("#ffffff")
        self.color_button = QPushButton("Selecionar cor")
        self.color_row = self._color_row(self.color_edit, self.color_button)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 200)
        self.position_x_spin = QDoubleSpinBox()
        self.position_y_spin = QDoubleSpinBox()
        for spin in (self.position_x_spin, self.position_y_spin):
            spin.setRange(-100000.0, 100000.0)
            spin.setDecimals(2)
        self.width_spin = QDoubleSpinBox()
        self.height_spin = QDoubleSpinBox()
        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(-1000, 1000)
        self.layer_spin.setToolTip("Valores maiores aparecem na frente.")
        for spin in (self.width_spin, self.height_spin):
            spin.setRange(1.0, 8192.0)
        self.action_combo = QComboBox()
        self.action_combo.addItem("Nenhuma", "none")
        self.action_combo.addItem("Continuar jogo", "continue_game")
        self.action_combo.addItem("Reiniciar cena", "restart_scene")
        self.action_combo.addItem("Trocar cena", "change_scene")
        self.action_combo.addItem("Sair", "quit")
        self.target_scene_edit = QLineEdit()
        self.button_normal_color = QLineEdit("#252a34")
        self.button_hover_color = QLineEdit("#3b4352")
        self.button_pressed_color = QLineEdit("#d5ad38")
        self.button_border_color = QLineEdit("#d5ad38")
        self.button_text_normal_color = QLineEdit("#ffffff")
        self.button_text_hover_color = QLineEdit("#d5ad38")
        self.button_text_pressed_color = QLineEdit("#ffffff")
        self.button_normal_color_button = QPushButton("Selecionar cor")
        self.button_hover_color_button = QPushButton("Selecionar cor")
        self.button_pressed_color_button = QPushButton("Selecionar cor")
        self.button_border_color_button = QPushButton("Selecionar cor")
        self.button_text_normal_color_button = QPushButton("Selecionar cor")
        self.button_text_hover_color_button = QPushButton("Selecionar cor")
        self.button_text_pressed_color_button = QPushButton("Selecionar cor")
        self.button_normal_color_row = self._color_row(self.button_normal_color, self.button_normal_color_button)
        self.button_hover_color_row = self._color_row(self.button_hover_color, self.button_hover_color_button)
        self.button_pressed_color_row = self._color_row(self.button_pressed_color, self.button_pressed_color_button)
        self.button_border_color_row = self._color_row(self.button_border_color, self.button_border_color_button)
        self.button_text_normal_color_row = self._color_row(self.button_text_normal_color, self.button_text_normal_color_button)
        self.button_text_hover_color_row = self._color_row(self.button_text_hover_color, self.button_text_hover_color_button)
        self.button_text_pressed_color_row = self._color_row(self.button_text_pressed_color, self.button_text_pressed_color_button)
        self.button_transparent = QCheckBox("Deixar somente texto e borda")
        self.button_opacity_slider = QSlider()
        self.button_opacity_slider.setOrientation(Qt.Orientation.Horizontal)
        self.button_opacity_slider.setRange(0, 100)
        self.button_opacity_slider.setValue(100)
        self.button_opacity_label = QLabel("100%")
        self.button_border_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.button_border_opacity_slider.setRange(0, 100)
        self.button_border_opacity_slider.setValue(100)
        self.button_border_opacity_label = QLabel("100%")
        self.button_border_opacity_row = QWidget()
        border_opacity_layout = QHBoxLayout(self.button_border_opacity_row)
        border_opacity_layout.setContentsMargins(0, 0, 0, 0)
        border_opacity_layout.addWidget(self.button_border_opacity_slider, 1)
        border_opacity_layout.addWidget(self.button_border_opacity_label)
        self.button_opacity_row = QWidget()
        opacity_layout = QHBoxLayout(self.button_opacity_row)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.addWidget(self.button_opacity_slider, 1)
        opacity_layout.addWidget(self.button_opacity_label)
        self.button_normal_image = QLineEdit()
        self.button_hover_image = QLineEdit()
        self.button_pressed_image = QLineEdit()
        self.button_normal_image_button = QPushButton("Escolher...")
        self.button_hover_image_button = QPushButton("Escolher...")
        self.button_pressed_image_button = QPushButton("Escolher...")
        self.button_normal_image_row = self._image_row(self.button_normal_image, self.button_normal_image_button)
        self.button_hover_image_row = self._image_row(self.button_hover_image, self.button_hover_image_button)
        self.button_pressed_image_row = self._image_row(self.button_pressed_image, self.button_pressed_image_button)
        self.add_button = QPushButton("Adicionar Elemento UI nesta entidade")
        self.center_button = QPushButton("Centralizar na cena")
        self.remove_button = QPushButton("Remover este item UI")
        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form.setVerticalSpacing(9)
        form.setHorizontalSpacing(0)
        form.addRow("Tipo:", self.type_combo)
        form.addRow("Texto:", self.text_edit)
        form.addRow("Imagem:", self.asset_row)
        form.addRow("Fonte:", self.font_edit)
        form.addRow("Cor:", self.color_row)
        form.addRow("Tamanho da fonte:", self.font_size_spin)
        form.addRow("Posição X:", self.position_x_spin)
        form.addRow("Posição Y:", self.position_y_spin)
        form.addRow("Largura:", self.width_spin)
        form.addRow("Altura:", self.height_spin)
        form.addRow("Camada:", self.layer_spin)
        form.addRow("Ação:", self.action_combo)
        form.addRow("Cena de destino:", self.target_scene_edit)
        form.addRow("Fundo transparente:", self.button_transparent)
        form.addRow("Opacidade do fundo:", self.button_opacity_row)
        form.addRow("Opacidade da borda:", self.button_border_opacity_row)
        form.addRow("Cor da borda:", self.button_border_color_row)
        form.addRow("Texto normal — cor:", self.button_text_normal_color_row)
        form.addRow("Texto com mouse — cor:", self.button_text_hover_color_row)
        form.addRow("Texto pressionado — cor:", self.button_text_pressed_color_row)
        form.addRow("Botão normal — cor:", self.button_normal_color_row)
        form.addRow("Botão normal — imagem:", self.button_normal_image_row)
        form.addRow("Mouse sobre — cor:", self.button_hover_color_row)
        form.addRow("Mouse sobre — imagem:", self.button_hover_image_row)
        form.addRow("Pressionado — cor:", self.button_pressed_color_row)
        form.addRow("Pressionado — imagem:", self.button_pressed_image_row)
        layout = QVBoxLayout(self)
        layout.addWidget(self.add_button)
        layout.addLayout(form)
        layout.addWidget(self.center_button)
        layout.addWidget(self.remove_button)
        self.add_button.clicked.connect(self._add)
        self.center_button.clicked.connect(self._center)
        self.asset_button.clicked.connect(self._choose_image)
        self.color_button.clicked.connect(lambda: self._choose_color(self.color_edit, self.color_button))
        self.button_normal_color_button.clicked.connect(lambda: self._choose_color(self.button_normal_color, self.button_normal_color_button))
        self.button_hover_color_button.clicked.connect(lambda: self._choose_color(self.button_hover_color, self.button_hover_color_button))
        self.button_pressed_color_button.clicked.connect(lambda: self._choose_color(self.button_pressed_color, self.button_pressed_color_button))
        self.button_border_color_button.clicked.connect(lambda: self._choose_color(self.button_border_color, self.button_border_color_button))
        self.button_text_normal_color_button.clicked.connect(lambda: self._choose_color(self.button_text_normal_color, self.button_text_normal_color_button))
        self.button_text_hover_color_button.clicked.connect(lambda: self._choose_color(self.button_text_hover_color, self.button_text_hover_color_button))
        self.button_text_pressed_color_button.clicked.connect(lambda: self._choose_color(self.button_text_pressed_color, self.button_text_pressed_color_button))
        self.button_transparent.toggled.connect(self._apply)
        self.button_opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self.button_border_opacity_slider.valueChanged.connect(self._on_border_opacity_changed)
        self.button_normal_image_button.clicked.connect(lambda: self._choose_state_image(self.button_normal_image))
        self.button_hover_image_button.clicked.connect(lambda: self._choose_state_image(self.button_hover_image))
        self.button_pressed_image_button.clicked.connect(lambda: self._choose_state_image(self.button_pressed_image))
        self.remove_button.clicked.connect(self._remove)
        self.type_combo.currentIndexChanged.connect(self._apply)
        self.action_combo.currentIndexChanged.connect(self._apply)
        for edit in (self.text_edit, self.asset_edit, self.font_edit, self.color_edit, self.target_scene_edit, self.button_normal_color, self.button_hover_color, self.button_pressed_color, self.button_border_color, self.button_text_normal_color, self.button_text_hover_color, self.button_text_pressed_color, self.button_normal_image, self.button_hover_image, self.button_pressed_image):
            edit.editingFinished.connect(self._apply)
        for spin in (self.font_size_spin, self.position_x_spin, self.position_y_spin, self.width_spin, self.height_spin, self.layer_spin):
            spin.valueChanged.connect(self._apply)
        self.set_context(None)

    @staticmethod
    def _color_row(edit: QLineEdit, button: QPushButton) -> QWidget:
        row = QWidget()
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        button.setMinimumHeight(30)
        edit.setPlaceholderText("#RRGGBB")
        layout.addWidget(button)
        layout.addWidget(edit)
        return row

    @staticmethod
    def _image_row(edit: QLineEdit, button: QPushButton) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit, 1)
        layout.addWidget(button)
        return row

    def set_context(self, entity: SceneEntity | None) -> None:
        self.entity = entity
        self._refresh()

    def _refresh(self) -> None:
        self._updating = True
        try:
            self.setEnabled(self.entity is not None)
            data = self.entity.ui_element if self.entity is not None else None
            has = data is not None
            self.add_button.setVisible(self.entity is not None and not has)
            self.remove_button.setVisible(has)
            self.center_button.setVisible(has)
            for widget in (self.type_combo, self.text_edit, self.asset_edit, self.asset_button, self.font_edit, self.color_edit, self.font_size_spin, self.position_x_spin, self.position_y_spin, self.width_spin, self.height_spin, self.layer_spin, self.action_combo, self.target_scene_edit, self.button_normal_color, self.button_hover_color, self.button_pressed_color, self.button_normal_image, self.button_hover_image, self.button_pressed_image, self.button_normal_image_button, self.button_hover_image_button, self.button_pressed_image_button, self.color_button, self.button_normal_color_button, self.button_hover_color_button, self.button_pressed_color_button, self.button_border_color, self.button_border_color_button, self.button_transparent, self.button_opacity_slider, self.button_border_opacity_slider, self.button_text_normal_color, self.button_text_hover_color, self.button_text_pressed_color, self.button_text_normal_color_button, self.button_text_hover_color_button, self.button_text_pressed_color_button):
                widget.setEnabled(has)
            data = data or {}
            self._select(self.type_combo, str(data.get("type", "text")))
            self.text_edit.setText(str(data.get("text", "")))
            self.asset_edit.setText(str(data.get("asset", "")))
            self.font_edit.setText(str(data.get("font", "")))
            self.color_edit.setText(str(data.get("color", "#ffffff")))
            self.font_size_spin.setValue(int(data.get("font_size", 24)))
            self.position_x_spin.setValue(float(self.entity.transform.x if self.entity is not None else 0.0))
            self.position_y_spin.setValue(float(self.entity.transform.y if self.entity is not None else 0.0))
            self.width_spin.setValue(float(data.get("width", 180.0)))
            self.height_spin.setValue(float(data.get("height", 48.0)))
            self.layer_spin.setValue(int(data.get("layer", 0)))
            self._select(self.action_combo, str(data.get("action", "none")))
            self.target_scene_edit.setText(str(data.get("target_scene", "")))
            self.button_normal_color.setText(str(data.get("button_normal_color", "#252a34")))
            self.button_hover_color.setText(str(data.get("button_hover_color", "#3b4352")))
            self.button_pressed_color.setText(str(data.get("button_pressed_color", "#d5ad38")))
            self.button_border_color.setText(str(data.get("button_border_color", "#d5ad38")))
            self.button_text_normal_color.setText(str(data.get("button_text_normal_color", data.get("color", "#ffffff"))))
            self.button_text_hover_color.setText(str(data.get("button_text_hover_color", "#d5ad38")))
            self.button_text_pressed_color.setText(str(data.get("button_text_pressed_color", "#ffffff")))
            self.button_transparent.setChecked(bool(data.get("button_transparent", False)))
            self.button_opacity_slider.setValue(int(data.get("button_opacity", 100)))
            self.button_opacity_label.setText(f"{self.button_opacity_slider.value()}%")
            self.button_border_opacity_slider.setValue(int(data.get("button_border_opacity", 100)))
            self.button_border_opacity_label.setText(f"{self.button_border_opacity_slider.value()}%")
            self.button_normal_image.setText(str(data.get("button_normal_image", "")))
            self.button_hover_image.setText(str(data.get("button_hover_image", "")))
            self.button_pressed_image.setText(str(data.get("button_pressed_image", "")))
            self._sync_color_buttons()
        finally:
            self._updating = False

    def _select(self, combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        combo.setCurrentIndex(max(0, index))

    def _add(self) -> None:
        if self.entity is None or self.entity.ui_element is not None:
            return
        self.entity.ui_element = {
            "type": "text", "text": "Novo texto", "asset": "",
            "font": "", "color": "#ffffff", "font_size": 24,
            "width": 180.0, "height": 48.0, "action": "none",
            "target_scene": "", "layer": 0,
            "button_normal_color": "#252a34",
            "button_hover_color": "#3b4352",
            "button_pressed_color": "#d5ad38",
            "button_border_color": "#d5ad38",
            "button_transparent": False, "button_opacity": 100,
            "button_border_opacity": 100,
            "button_text_normal_color": "#ffffff",
            "button_text_hover_color": "#d5ad38",
            "button_text_pressed_color": "#ffffff",
            "button_normal_image": "", "button_hover_image": "",
            "button_pressed_image": "",
        }
        self.entity.refresh_kind()
        self._refresh()
        self.element_changed.emit(self.entity.id)

    def _choose_image(self) -> None:
        if self.entity is None or self.entity.ui_element is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Escolher imagem da interface", "",
            "Imagens (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not path:
            return
        self.asset_edit.setText(path)
        self._apply()

    @staticmethod
    def _paint_color_button(edit: QLineEdit, button: QPushButton) -> None:
        color = QColor(edit.text().strip())
        if not color.isValid():
            color = QColor("#000000")
        foreground = "#000000" if color.lightness() > 145 else "#ffffff"
        button.setStyleSheet(
            f"background-color: {color.name()}; color: {foreground};"
            "border: 1px solid #8f98a8; border-radius: 4px;"
        )
        button.setText("Selecionar cor")

    def _sync_color_buttons(self) -> None:
        for edit, button in (
            (self.color_edit, self.color_button),
            (self.button_normal_color, self.button_normal_color_button),
            (self.button_hover_color, self.button_hover_color_button),
            (self.button_pressed_color, self.button_pressed_color_button),
            (self.button_border_color, self.button_border_color_button),
            (self.button_text_normal_color, self.button_text_normal_color_button),
            (self.button_text_hover_color, self.button_text_hover_color_button),
            (self.button_text_pressed_color, self.button_text_pressed_color_button),
        ):
            self._paint_color_button(edit, button)

    def _choose_color(self, edit: QLineEdit, button: QPushButton) -> None:
        initial = QColor(edit.text().strip())
        if not initial.isValid():
            initial = QColor("#ffffff")
        selected = QColorDialog.getColor(
            initial, self, "Selecionar cor",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if not selected.isValid():
            return
        code = selected.name(QColor.NameFormat.HexArgb)
        if selected.alpha() == 255:
            code = selected.name(QColor.NameFormat.HexRgb)
        edit.setText(code)
        self._paint_color_button(edit, button)
        self._apply()

    def _choose_state_image(self, edit: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Escolher imagem do estado do botão", "",
            "Imagens (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if path:
            edit.setText(path)
            self._apply()

    def _on_opacity_changed(self, value: int) -> None:
        self.button_opacity_label.setText(f"{value}%")
        self._apply()

    def _on_border_opacity_changed(self, value: int) -> None:
        self.button_border_opacity_label.setText(f"{value}%")
        self._apply()

    def _center(self) -> None:
        if self.entity is not None and self.entity.ui_element is not None:
            self.center_requested.emit(self.entity.id)

    def _remove(self) -> None:
        if self.entity is None:
            return
        self.entity.ui_element = None
        self.entity.refresh_kind()
        self._refresh()
        self.element_changed.emit(self.entity.id)

    def _apply(self) -> None:
        if self._updating or self.entity is None or self.entity.ui_element is None:
            return
        self.entity.transform.x = self.position_x_spin.value()
        self.entity.transform.y = self.position_y_spin.value()
        self.entity.ui_element.update({
            "type": str(self.type_combo.currentData()),
            "text": self.text_edit.text(), "asset": self.asset_edit.text(),
            "font": self.font_edit.text(), "color": self.color_edit.text(),
            "font_size": self.font_size_spin.value(),
            "width": self.width_spin.value(), "height": self.height_spin.value(),
            "action": str(self.action_combo.currentData()),
            "target_scene": self.target_scene_edit.text(),
            "layer": self.layer_spin.value(),
            "button_normal_color": self.button_normal_color.text(),
            "button_hover_color": self.button_hover_color.text(),
            "button_pressed_color": self.button_pressed_color.text(),
            "button_border_color": self.button_border_color.text(),
            "button_transparent": self.button_transparent.isChecked(),
            "button_border_opacity": self.button_border_opacity_slider.value(),
            "button_text_normal_color": self.button_text_normal_color.text(),
            "button_text_hover_color": self.button_text_hover_color.text(),
            "button_text_pressed_color": self.button_text_pressed_color.text(),
            "button_opacity": self.button_opacity_slider.value(),
            "button_normal_image": self.button_normal_image.text(),
            "button_hover_image": self.button_hover_image.text(),
            "button_pressed_image": self.button_pressed_image.text(),
        })
        self.entity.refresh_kind()
        self._sync_color_buttons()
        self.element_changed.emit(self.entity.id)
