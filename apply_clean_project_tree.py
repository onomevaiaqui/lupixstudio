import shutil
from pathlib import Path

PATH = Path(
    r".\src\lupix_studio\ui\project_tree.py"
)

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_clean_project_tree"
)

if not backup.exists():
    shutil.copy2(
        PATH,
        backup,
    )

content = 'from __future__ import annotations\n\nfrom pathlib import Path\n\nfrom PySide6.QtCore import Qt\nfrom PySide6.QtWidgets import (\n    QStyle,\n    QTreeWidget,\n    QTreeWidgetItem,\n)\n\n\nclass ProjectTree(QTreeWidget):\n    """Explorador visual simplificado de um projeto Lupix."""\n\n    ROLE_PATH = Qt.ItemDataRole.UserRole\n\n    PROJECT_CATEGORIES = (\n        ("assets", "Assets"),\n        ("scenes", "Cenas"),\n        ("maps", "Mapas"),\n        ("scripts", "Scripts"),\n    )\n\n    HIDDEN_NAMES = {\n        "lupix",\n        "lupix.project",\n        "README.md",\n        "__pycache__",\n    }\n\n    def __init__(self) -> None:\n        super().__init__()\n\n        self.project_root: Path | None = None\n\n        self.setHeaderLabel(\n            "Projeto"\n        )\n\n        self.setAlternatingRowColors(\n            False\n        )\n\n        self.setAnimated(\n            True\n        )\n\n        self.setIndentation(\n            18\n        )\n\n        self.setUniformRowHeights(\n            True\n        )\n\n    def load_project(\n        self,\n        root: Path,\n    ) -> None:\n        self.project_root = Path(\n            root\n        ).resolve()\n\n        self.clear()\n\n        root_item = QTreeWidgetItem(\n            [\n                self.project_root.name,\n            ]\n        )\n\n        root_item.setData(\n            0,\n            self.ROLE_PATH,\n            str(\n                self.project_root\n            ),\n        )\n\n        root_item.setIcon(\n            0,\n            self.style().standardIcon(\n                QStyle.StandardPixmap.SP_DirHomeIcon\n            ),\n        )\n\n        root_item.setExpanded(\n            True\n        )\n\n        self.addTopLevelItem(\n            root_item\n        )\n\n        for folder_name, label in (\n            self.PROJECT_CATEGORIES\n        ):\n            folder_path = (\n                self.project_root\n                / folder_name\n            )\n\n            category_item = (\n                self._create_category_item(\n                    label,\n                    folder_path,\n                )\n            )\n\n            root_item.addChild(\n                category_item\n            )\n\n            if folder_path.exists():\n                self._populate_directory(\n                    category_item,\n                    folder_path,\n                )\n\n            if folder_name == "scripts":\n                self._add_entry_point(\n                    category_item\n                )\n\n        root_item.setExpanded(\n            True\n        )\n\n    def _create_category_item(\n        self,\n        label: str,\n        path: Path,\n    ) -> QTreeWidgetItem:\n        item = QTreeWidgetItem(\n            [\n                label,\n            ]\n        )\n\n        item.setData(\n            0,\n            self.ROLE_PATH,\n            str(path),\n        )\n\n        item.setIcon(\n            0,\n            self.style().standardIcon(\n                QStyle.StandardPixmap.SP_DirIcon\n            ),\n        )\n\n        return item\n\n    def _populate_directory(\n        self,\n        parent: QTreeWidgetItem,\n        directory: Path,\n    ) -> None:\n        try:\n            children = sorted(\n                directory.iterdir(),\n                key=lambda path: (\n                    not path.is_dir(),\n                    path.name.lower(),\n                ),\n            )\n        except OSError:\n            return\n\n        for path in children:\n            if (\n                path.name\n                in self.HIDDEN_NAMES\n            ):\n                continue\n\n            if path.name.startswith(\n                "."\n            ):\n                continue\n\n            item = QTreeWidgetItem(\n                [\n                    path.name,\n                ]\n            )\n\n            item.setData(\n                0,\n                self.ROLE_PATH,\n                str(path),\n            )\n\n            if path.is_dir():\n                item.setIcon(\n                    0,\n                    self.style().standardIcon(\n                        QStyle.StandardPixmap.SP_DirIcon\n                    ),\n                )\n\n                parent.addChild(\n                    item\n                )\n\n                self._populate_directory(\n                    item,\n                    path,\n                )\n\n            else:\n                item.setIcon(\n                    0,\n                    self.style().standardIcon(\n                        QStyle.StandardPixmap.SP_FileIcon\n                    ),\n                )\n\n                parent.addChild(\n                    item\n                )\n\n    def _add_entry_point(\n        self,\n        scripts_item: QTreeWidgetItem,\n    ) -> None:\n        if self.project_root is None:\n            return\n\n        game_lua = (\n            self.project_root\n            / "game.lua"\n        )\n\n        if not game_lua.exists():\n            return\n\n        # Evita duplicar caso game.lua já esteja fisicamente\n        # dentro da pasta scripts em projetos futuros.\n        for index in range(\n            scripts_item.childCount()\n        ):\n            child = scripts_item.child(\n                index\n            )\n\n            value = child.data(\n                0,\n                self.ROLE_PATH,\n            )\n\n            if (\n                value\n                and Path(\n                    str(value)\n                ).resolve()\n                == game_lua.resolve()\n            ):\n                return\n\n        item = QTreeWidgetItem(\n            [\n                "game.lua",\n            ]\n        )\n\n        item.setToolTip(\n            0,\n            "Script principal do jogo",\n        )\n\n        item.setData(\n            0,\n            self.ROLE_PATH,\n            str(game_lua),\n        )\n\n        item.setIcon(\n            0,\n            self.style().standardIcon(\n                QStyle.StandardPixmap.SP_FileIcon\n            ),\n        )\n\n        scripts_item.insertChild(\n            0,\n            item,\n        )\n'

PATH.write_text(
    content,
    encoding="utf-8",
)

print("Explorador de Projeto atualizado.")
print()
print("Agora exibe somente:")
print("- Assets")
print("- Cenas")
print("- Mapas")
print("- Scripts")
print()
print("Ocultos:")
print("- lupix/")
print("- lupix.project")
print("- README.md")
print()
print("game.lua aparece dentro de Scripts sem ser movido no disco.")
print(f"Backup: {backup}")
