from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)


class NewSceneDialog(QDialog):
    """Diálogo para criação de uma nova cena."""

    def __init__(
        self,
        parent=None,
        default_width: int = 480,
        default_height: int = 270,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Nova Cena")
        self.setMinimumWidth(360)

        self.name_edit = QLineEdit()
        self.name_edit.setText("Main")
        self.name_edit.selectAll()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 8192)
        self.width_spin.setValue(default_width)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 8192)
        self.height_spin.setValue(default_height)

        form = QFormLayout()

        form.addRow(
            "Nome:",
            self.name_edit,
        )

        form.addRow(
            "Largura:",
            self.width_spin,
        )

        form.addRow(
            "Altura:",
            self.height_spin,
        )

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.accepted.connect(
            self.accept
        )

        self.buttons.rejected.connect(
            self.reject
        )

        layout = QVBoxLayout(self)

        layout.addLayout(form)
        layout.addWidget(self.buttons)

    def scene_name(self) -> str:
        return self.name_edit.text().strip()

    def scene_width(self) -> int:
        return self.width_spin.value()

    def scene_height(self) -> int:
        return self.height_spin.value()