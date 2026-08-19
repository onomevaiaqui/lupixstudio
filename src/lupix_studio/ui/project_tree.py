from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
)


class ProjectTree(QTreeWidget):
    """Explorador visual simplificado de um projeto Lupix."""

    ROLE_PATH = Qt.ItemDataRole.UserRole

    PROJECT_CATEGORIES = (
        ("assets", "Assets"),
        ("scenes", "Cenas"),
        ("maps", "Mapas"),
        ("scripts", "Scripts"),
    )

    HIDDEN_NAMES = {
        "lupix",
        "lupix.project",
        "README.md",
        "__pycache__",
    }

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None

        self.setHeaderLabel(
            "Projeto"
        )

        self.setAlternatingRowColors(
            False
        )

        self.setAnimated(
            True
        )

        self.setIndentation(
            18
        )

        self.setUniformRowHeights(
            True
        )

    def load_project(
        self,
        root: Path,
    ) -> None:
        self.project_root = Path(
            root
        ).resolve()

        self.clear()

        root_item = QTreeWidgetItem(
            [
                self.project_root.name,
            ]
        )

        root_item.setData(
            0,
            self.ROLE_PATH,
            str(
                self.project_root
            ),
        )

        root_item.setIcon(
            0,
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_DirHomeIcon
            ),
        )

        root_item.setExpanded(
            True
        )

        self.addTopLevelItem(
            root_item
        )

        for folder_name, label in (
            self.PROJECT_CATEGORIES
        ):
            folder_path = (
                self.project_root
                / folder_name
            )

            category_item = (
                self._create_category_item(
                    label,
                    folder_path,
                )
            )

            root_item.addChild(
                category_item
            )

            if folder_path.exists():
                self._populate_directory(
                    category_item,
                    folder_path,
                )

            if folder_name == "scripts":
                self._add_entry_point(
                    category_item
                )

        root_item.setExpanded(
            True
        )

    def _create_category_item(
        self,
        label: str,
        path: Path,
    ) -> QTreeWidgetItem:
        item = QTreeWidgetItem(
            [
                label,
            ]
        )

        item.setData(
            0,
            self.ROLE_PATH,
            str(path),
        )

        item.setIcon(
            0,
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_DirIcon
            ),
        )

        return item

    def _populate_directory(
        self,
        parent: QTreeWidgetItem,
        directory: Path,
    ) -> None:
        try:
            children = sorted(
                directory.iterdir(),
                key=lambda path: (
                    not path.is_dir(),
                    path.name.lower(),
                ),
            )
        except OSError:
            return

        for path in children:
            if (
                path.name
                in self.HIDDEN_NAMES
            ):
                continue

            if path.name.startswith(
                "."
            ):
                continue

            item = QTreeWidgetItem(
                [
                    path.name,
                ]
            )

            item.setData(
                0,
                self.ROLE_PATH,
                str(path),
            )

            if path.is_dir():
                item.setIcon(
                    0,
                    self.style().standardIcon(
                        QStyle.StandardPixmap.SP_DirIcon
                    ),
                )

                parent.addChild(
                    item
                )

                self._populate_directory(
                    item,
                    path,
                )

            else:
                item.setIcon(
                    0,
                    self.style().standardIcon(
                        QStyle.StandardPixmap.SP_FileIcon
                    ),
                )

                parent.addChild(
                    item
                )

    def _add_entry_point(
        self,
        scripts_item: QTreeWidgetItem,
    ) -> None:
        if self.project_root is None:
            return

        game_lua = (
            self.project_root
            / "game.lua"
        )

        if not game_lua.exists():
            return

        # Evita duplicar caso game.lua já esteja fisicamente
        # dentro da pasta scripts em projetos futuros.
        for index in range(
            scripts_item.childCount()
        ):
            child = scripts_item.child(
                index
            )

            value = child.data(
                0,
                self.ROLE_PATH,
            )

            if (
                value
                and Path(
                    str(value)
                ).resolve()
                == game_lua.resolve()
            ):
                return

        item = QTreeWidgetItem(
            [
                "game.lua",
            ]
        )

        item.setToolTip(
            0,
            "Script principal do jogo",
        )

        item.setData(
            0,
            self.ROLE_PATH,
            str(game_lua),
        )

        item.setIcon(
            0,
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_FileIcon
            ),
        )

        scripts_item.insertChild(
            0,
            item,
        )
