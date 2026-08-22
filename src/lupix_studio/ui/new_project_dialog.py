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
    QSpinBox,
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
            "Flowchart",
            DevelopmentMode.BLUEPRINT.value,
        )

        self.mode_combo.addItem(
            "Flowchart + Script",
            DevelopmentMode.HYBRID.value,
        )

        self.mode_combo.addItem(
            "Script",
            DevelopmentMode.SCRIPT.value,
        )

        self.platform_combo = QComboBox()

        self.platform_combo.addItem(
            "Lupi",
            "lupi",
        )

        self.platform_combo.addItem(
            "PC",
            "pc",
        )

        self.width_spin = QSpinBox()
        self.width_spin.setRange(
            160,
            7680,
        )
        self.width_spin.setValue(
            480
        )

        self.height_spin = QSpinBox()
        self.height_spin.setRange(
            90,
            4320,
        )
        self.height_spin.setValue(
            270
        )

        resolution_layout = QHBoxLayout()
        resolution_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        resolution_layout.addWidget(
            self.width_spin
        )
        resolution_layout.addWidget(
            QLabel("×")
        )
        resolution_layout.addWidget(
            self.height_spin
        )

        resolution_widget = QWidget()
        resolution_widget.setLayout(
            resolution_layout
        )

        self.resolution_hint = QLabel()
        self.resolution_hint.setWordWrap(
            True
        )

        form = QFormLayout()
        form.addRow("Nome:", self.name_edit)
        form.addRow("Local:", location_widget)
        form.addRow("Tipo:", QLabel("2D"))
        form.addRow("Modo:", self.mode_combo)
        form.addRow(
            "Plataforma de saída:",
            self.platform_combo,
        )
        form.addRow(
            "Resolução:",
            resolution_widget,
        )
        form.addRow(
            "",
            self.resolution_hint,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )

        buttons.button(
            QDialogButtonBox.StandardButton.Ok
        ).setText("Criar Projeto")

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.platform_combo.currentIndexChanged.connect(
            self._on_platform_changed
        )

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addSpacing(12)
        layout.addWidget(buttons)

        self._on_platform_changed()

    def _on_platform_changed(
        self,
        *_args,
    ) -> None:
        platform = str(
            self.platform_combo.currentData()
        )

        if platform == "lupi":
            self.width_spin.setValue(
                480
            )
            self.height_spin.setValue(
                270
            )

            self.width_spin.setEnabled(
                False
            )
            self.height_spin.setEnabled(
                False
            )

            self.resolution_hint.setText(
                "Lupi usa resolução fixa "
                "480 × 270 px (Widescreen 16:9)."
            )

            return

        self.width_spin.setEnabled(
            True
        )
        self.height_spin.setEnabled(
            True
        )

        if (
            self.width_spin.value() == 480
            and self.height_spin.value() == 270
        ):
            self.width_spin.setValue(
                1920
            )
            self.height_spin.setValue(
                1080
            )

        self.resolution_hint.setText(
            "PC permite resolução personalizada. "
            "O padrão sugerido é 1920 × 1080."
        )

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