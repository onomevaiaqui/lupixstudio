from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
)

from lupix_studio.assets.compatibility import (
    CompatibilityStatus,
    analyze_png,
)

STATUS_LABELS = {
    CompatibilityStatus.COMPATIBLE: "Compatível",
    CompatibilityStatus.CONVERSION_REQUIRED: "Conversão necessária",
    CompatibilityStatus.INVALID: "Inválido",
}


class AssetBrowser(QListWidget):
    """Exibe assets importados do projeto."""

    asset_selected = Signal(Path)
    asset_activated = Signal(Path)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None

        self.setViewMode(
            QListWidget.ViewMode.IconMode
        )

        self.setResizeMode(
            QListWidget.ResizeMode.Adjust
        )

        self.setIconSize(
            QPixmap(96, 96).size()
        )

        self.setSpacing(8)

        self.itemClicked.connect(
            self._on_item_clicked
        )

        self.itemDoubleClicked.connect(
            self._on_item_double_clicked
        )

    def load_project(
        self,
        project_root: Path,
    ) -> None:
        self.project_root = project_root.resolve()
        self.refresh()

    def refresh(self) -> None:
        self.clear()

        if self.project_root is None:
            return

        assets_root = self.project_root / "assets"

        if not assets_root.exists():
            return

        png_files = sorted(
            assets_root.rglob("*.png"),
            key=lambda path: str(path).lower(),
        )

        for path in png_files:
            self._add_png(path)

    def _add_png(self, path: Path) -> None:
        pixmap = QPixmap(str(path))

        compatibility = analyze_png(path)

        status = STATUS_LABELS[
            compatibility.status
        ]

        item = QListWidgetItem(
            QIcon(pixmap),
            f"{path.name}\n{status}",
        )

        item.setData(
            Qt.ItemDataRole.UserRole,
            str(path),
        )

        reasons = "\n".join(
            compatibility.reasons
        )

        tooltip = (
            f"{path.relative_to(self.project_root)}\n"
            f"{compatibility.width}x{compatibility.height}\n"
            f"{compatibility.color_count} cores\n"
            f"Status: {status}"
        )

        if reasons:
            tooltip += f"\n\n{reasons}"

        item.setToolTip(tooltip)

        self.addItem(item)

    def _on_item_clicked(
        self,
        item: QListWidgetItem,
    ) -> None:
        value = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not value:
            return

        self.asset_selected.emit(
            Path(str(value))
        )

    def _on_item_double_clicked(
        self,
        item: QListWidgetItem,
    ) -> None:
        value = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not value:
            return

        self.asset_activated.emit(
            Path(str(value))
        )