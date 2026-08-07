from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.compatibility import (
    CompatibilityStatus,
    analyze_png,
    create_rgb555_preview,
)


class AssetPreviewDialog(QDialog):
    """Exibe o asset original e uma simulação RGB555."""

    def __init__(
        self,
        path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.path = path

        self.setWindowTitle(
            f"Preview - {path.name}"
        )
        self.resize(900, 520)

        analysis = analyze_png(path)

        status_names = {
            CompatibilityStatus.COMPATIBLE: "Compatível",
            CompatibilityStatus.CONVERSION_REQUIRED: (
                "Conversão necessária"
            ),
            CompatibilityStatus.INVALID: "Inválido",
        }

        info = QLabel(
            f"{analysis.width}x{analysis.height} | "
            f"{analysis.color_count} cores | "
            f"{status_names[analysis.status]}"
        )

        info.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        original_label = QLabel()
        original_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        converted_label = QLabel()
        converted_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        original = QPixmap(str(path))

        converted_image = create_rgb555_preview(
            path
        )
        converted = QPixmap.fromImage(
            converted_image
        )

        original_label.setPixmap(
            original.scaled(
                360,
                360,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )

        converted_label.setPixmap(
            converted.scaled(
                360,
                360,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )

        original_column = QVBoxLayout()
        original_column.addWidget(
            QLabel("Original")
        )
        original_column.addWidget(
            original_label
        )

        converted_column = QVBoxLayout()
        converted_column.addWidget(
            QLabel("Preview 5 bits/canal")
        )
        converted_column.addWidget(
            converted_label
        )

        images = QHBoxLayout()
        images.addLayout(
            original_column
        )
        images.addLayout(
            converted_column
        )

        layout = QVBoxLayout(self)
        layout.addWidget(info)
        layout.addLayout(images)