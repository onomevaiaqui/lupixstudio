from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

IGNORED_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}


class ProjectTree(QTreeWidget):
    """Exibe os arquivos reais do projeto aberto."""

    def __init__(self) -> None:
        super().__init__()

        self.setHeaderHidden(True)
        self.setIndentation(18)
        self.setAnimated(True)
        self.setMinimumWidth(220)

        self.project_root: Path | None = None

    def clear_project(self) -> None:
        self.clear()
        self.project_root = None

    def load_project(self, root: Path) -> None:
        self.clear()

        self.project_root = root.resolve()

        root_item = QTreeWidgetItem([self.project_root.name])
        root_item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            str(self.project_root),
        )

        self.addTopLevelItem(root_item)

        self._populate_directory(
            root_item,
            self.project_root,
        )

        root_item.setExpanded(True)

    def _populate_directory(
        self,
        parent_item: QTreeWidgetItem,
        directory: Path,
    ) -> None:
        entries = sorted(
            (
                entry
                for entry in directory.iterdir()
                if entry.name not in IGNORED_NAMES
            ),
            key=lambda entry: (
                not entry.is_dir(),
                entry.name.lower(),
            ),
        )

        for entry in entries:
            item = QTreeWidgetItem([entry.name])

            item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                str(entry),
            )

            parent_item.addChild(item)

            if entry.is_dir():
                self._populate_directory(item, entry)