from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.project.model import DevelopmentMode, ProjectConfig


class NewProjectDialog(QDialog):
    """Assistente para criação de um projeto Lupix."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Novo Projeto")
        self.setMinimumWidth(520)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Meu Jogo")

        self.location_edit = QLineEdit(
            str(Path.home() / "Documents" / "Lupix Projects")
        )

        browse_button = QPushButton("Procurar")
        browse_button.clicked.connect(self._browse)

        location_layout = QHBoxLayout()
        location_layout.setContentsMargins(0, 0, 0, 0)
        location_layout.addWidget(self.location_edit)
        location_layout.addWidget(browse_button)

        location_widget = QWidget()
        location_widget.setLayout(location_layout)

        self.mode_combo = QComboBox()

        self.mode_combo.addItem(
            "Blueprint",
            DevelopmentMode.BLUEPRINT.value,
        )

        self.mode_combo.addItem(
            "Blueprint + Script",
            DevelopmentMode.HYBRID.value,
        )

        self.mode_combo.addItem(
            "Script",
            DevelopmentMode.SCRIPT.value,
        )

        form = QFormLayout()
        form.addRow("Nome:", self.name_edit)
        form.addRow("Local:", location_widget)
        form.addRow("Tipo:", QLabel("2D"))
        form.addRow("Modo:", self.mode_combo)
        form.addRow("Plataforma principal:", QLabel("Lupi"))
        form.addRow("Resolução:", QLabel("480 × 270"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )

        buttons.button(
            QDialogButtonBox.StandardButton.Ok
        ).setText("Criar Projeto")

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addSpacing(12)
        layout.addWidget(buttons)

    def _browse(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Escolher local do projeto",
            self.location_edit.text(),
        )

        if directory:
            self.location_edit.setText(directory)

    def project_config(self) -> ProjectConfig:
        mode_value = str(self.mode_combo.currentData())

        return ProjectConfig(
            name=self.name_edit.text().strip(),
            root=Path(self.location_edit.text()),
            development_mode=DevelopmentMode(mode_value),
        )