from pathlib import Path

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.compatibility import CompatibilityStatus
from lupix_studio.assets.registry import AssetRecord, AssetRegistry

STATUS_LABELS = {
    CompatibilityStatus.COMPATIBLE.value: "Compatível",
    CompatibilityStatus.CONVERSION_REQUIRED.value: "Conversão necessária",
    CompatibilityStatus.INVALID.value: "Inválido",
}


class AssetInspector(QWidget):
    """Inspector visual de assets."""

    def __init__(self) -> None:
        super().__init__()

        self.title = QLabel("Nenhum asset selecionado")
        self.title.setObjectName("SectionTitle")

        self.name_value = QLabel("-")
        self.id_value = QLabel("-")
        self.type_value = QLabel("-")
        self.path_value = QLabel("-")
        self.size_value = QLabel("-")
        self.colors_value = QLabel("-")
        self.compatibility_value = QLabel("-")

        self.id_value.setWordWrap(True)
        self.path_value.setWordWrap(True)

        form = QFormLayout()

        form.addRow("Nome:", self.name_value)
        form.addRow("ID:", self.id_value)
        form.addRow("Tipo:", self.type_value)
        form.addRow("Caminho:", self.path_value)
        form.addRow("Dimensões:", self.size_value)
        form.addRow("Cores:", self.colors_value)
        form.addRow(
            "Compatibilidade:",
            self.compatibility_value,
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addLayout(form)
        layout.addStretch()

    def clear_asset(self) -> None:
        self.title.setText(
            "Nenhum asset selecionado"
        )

        for label in (
            self.name_value,
            self.id_value,
            self.type_value,
            self.path_value,
            self.size_value,
            self.colors_value,
            self.compatibility_value,
        ):
            label.setText("-")

    def show_record(
        self,
        record: AssetRecord,
    ) -> None:
        self.title.setText(record.name)

        self.name_value.setText(
            record.name
        )

        self.id_value.setText(
            record.id
        )

        self.type_value.setText(
            record.type
        )

        self.path_value.setText(
            record.path
        )

        self.size_value.setText(
            f"{record.width} x {record.height}"
        )

        self.colors_value.setText(
            str(record.color_count)
        )

        self.compatibility_value.setText(
            STATUS_LABELS.get(
                record.compatibility,
                record.compatibility,
            )
        )


def load_asset_record(
    project_root: Path,
    asset_path: Path,
) -> AssetRecord | None:
    registry = AssetRegistry(
        project_root
    )

    return registry.find_by_path(
        asset_path
    )