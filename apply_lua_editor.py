import shutil
from pathlib import Path

ROOT = Path(r".\src\lupix_studio\ui")
MAIN = ROOT / "main_window.py"
EDITOR = ROOT / "lua_editor.py"

if not MAIN.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {MAIN}"
    )

backup = MAIN.with_suffix(
    MAIN.suffix + ".bak_lua_editor"
)

if not backup.exists():
    shutil.copy2(MAIN, backup)

EDITOR.write_text(
    'from __future__ import annotations\n\nfrom pathlib import Path\n\nfrom PySide6.QtCore import Signal\nfrom PySide6.QtGui import QFontDatabase\nfrom PySide6.QtWidgets import (\n    QHBoxLayout,\n    QLabel,\n    QMessageBox,\n    QPushButton,\n    QPlainTextEdit,\n    QVBoxLayout,\n    QWidget,\n)\n\n\nclass LuaEditor(QWidget):\n    """Editor Lua simples integrado ao Lupix Studio."""\n\n    back_requested = Signal()\n    saved = Signal(Path)\n\n    def __init__(self) -> None:\n        super().__init__()\n\n        self.current_path: Path | None = None\n\n        self.title_label = QLabel("Editor Lua")\n        self.title_label.setStyleSheet(\n            "font-size: 16px; font-weight: 600;"\n        )\n\n        self.path_label = QLabel()\n        self.path_label.setWordWrap(True)\n\n        self.editor = QPlainTextEdit()\n\n        fixed_font = QFontDatabase.systemFont(\n            QFontDatabase.SystemFont.FixedFont\n        )\n        self.editor.setFont(fixed_font)\n\n        self.save_button = QPushButton("Salvar")\n        self.back_button = QPushButton("Voltar")\n\n        buttons = QHBoxLayout()\n        buttons.addStretch()\n        buttons.addWidget(self.back_button)\n        buttons.addWidget(self.save_button)\n\n        layout = QVBoxLayout(self)\n        layout.setContentsMargins(14, 14, 14, 14)\n        layout.setSpacing(8)\n        layout.addWidget(self.title_label)\n        layout.addWidget(self.path_label)\n        layout.addWidget(self.editor, 1)\n        layout.addLayout(buttons)\n\n        self.save_button.clicked.connect(self.save)\n        self.back_button.clicked.connect(\n            self.back_requested.emit\n        )\n\n    def open_file(self, path: Path) -> bool:\n        path = Path(path).resolve()\n\n        try:\n            content = path.read_text(\n                encoding="utf-8"\n            )\n        except OSError as error:\n            QMessageBox.critical(\n                self,\n                "Erro ao abrir script",\n                str(error),\n            )\n            return False\n\n        self.current_path = path\n        self.title_label.setText(\n            f"Editor Lua — {path.name}"\n        )\n        self.path_label.setText(str(path))\n        self.editor.setPlainText(content)\n        self.editor.document().setModified(False)\n        self.editor.setFocus()\n        return True\n\n    def save(self) -> bool:\n        if self.current_path is None:\n            return False\n\n        try:\n            self.current_path.write_text(\n                self.editor.toPlainText(),\n                encoding="utf-8",\n            )\n        except OSError as error:\n            QMessageBox.critical(\n                self,\n                "Erro ao salvar script",\n                str(error),\n            )\n            return False\n\n        self.editor.document().setModified(False)\n        self.saved.emit(self.current_path)\n        return True\n',
    encoding="utf-8",
)

text = MAIN.read_text(encoding="utf-8")

import_anchor = (
    "from lupix_studio.ui.project_tree import ProjectTree\n"
)

if import_anchor not in text:
    raise RuntimeError(
        "Import de ProjectTree não encontrado."
    )

if "from lupix_studio.ui.lua_editor import LuaEditor\n" not in text:
    text = text.replace(
        import_anchor,
        "from lupix_studio.ui.lua_editor import LuaEditor\n"
        + import_anchor,
        1,
    )

workspace_anchor = (
    "        self.workspace = WorkspaceWidget()\n"
)

if workspace_anchor not in text:
    raise RuntimeError(
        "_create_workspace não encontrado."
    )

if "self.lua_editor = LuaEditor()" not in text:
    addition = (
        workspace_anchor
        + "\n"
        + "        self.lua_editor = LuaEditor()\n"
        + "        self.workspace.stack.addWidget(\n"
        + "            self.lua_editor\n"
        + "        )\n\n"
        + "        self.lua_editor.back_requested.connect(\n"
        + "            self._on_lua_editor_back\n"
        + "        )\n\n"
        + "        self.lua_editor.saved.connect(\n"
        + "            self._on_lua_editor_saved\n"
        + "        )\n"
    )

    text = text.replace(
        workspace_anchor,
        addition,
        1,
    )

old_double = (
    '        if path.suffix.lower() == ".scene":\n'
    '            self._open_scene_file(\n'
    '                path\n'
    '            )\n'
)

new_double = (
    '        suffix = path.suffix.lower()\n\n'
    '        if suffix == ".scene":\n'
    '            self._open_scene_file(\n'
    '                path\n'
    '            )\n'
    '            return\n\n'
    '        if suffix == ".lua":\n'
    '            self._open_lua_file(\n'
    '                path\n'
    '            )\n'
)

if old_double not in text:
    raise RuntimeError(
        "Bloco de duplo clique em .scene não encontrado."
    )

text = text.replace(
    old_double,
    new_double,
    1,
)

method_anchor = (
    "    def _show_project_view(self) -> None:\n"
)

if method_anchor not in text:
    raise RuntimeError(
        "_show_project_view não encontrado."
    )

if "    def _open_lua_file(" not in text:
    methods = """    def _open_lua_file(
        self,
        path: Path,
    ) -> None:
        if self.playing:
            return

        if not self.lua_editor.open_file(path):
            return

        self.workspace.stack.setCurrentWidget(
            self.lua_editor
        )

        self.statusBar().showMessage(
            f"Script aberto: {path.name}"
        )

        self.console.append(
            f"Script Lua aberto: {path}"
        )

        self.setWindowTitle(
            f"{path.name} - Lupix Studio"
        )

    def _on_lua_editor_saved(
        self,
        path: Path,
    ) -> None:
        self.statusBar().showMessage(
            f"Script salvo: {path.name}"
        )

        self.console.append(
            f"Script Lua salvo: {path}"
        )

    def _on_lua_editor_back(self) -> None:
        if (
            self.current_scene is not None
            and self.current_project is not None
        ):
            self.workspace.show_scene(
                self.current_project.root,
                self.current_scene,
            )

            self._show_scene_hierarchy()

            self.setWindowTitle(
                f"{self.current_scene.name} - "
                f"{self.current_project.name} - "
                "Lupix Studio"
            )
            return

        self._show_project_view()

"""

    text = text.replace(
        method_anchor,
        methods + method_anchor,
        1,
    )

MAIN.write_text(
    text,
    encoding="utf-8",
)

print("Editor Lua integrado ao Lupix Studio.")
print("game.lua agora abre com duplo clique.")
print(f"Backup: {backup}")
