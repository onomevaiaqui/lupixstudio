import shutil
from pathlib import Path

path = Path(
    r".\\src\\lupix_studio\\ui\\main_window.py"
)

if not path.exists():
    raise SystemExit(
        f"Arquivo não encontrado: {path.resolve()}"
    )

backup = path.with_suffix(
    path.suffix + ".bak_start_screen_v2"
)

if not backup.exists():
    shutil.copy2(path, backup)

text = path.read_text(encoding="utf-8")

# Adiciona métodos para alternar entre a tela inicial limpa
# e a interface completa do editor.
if "def _set_start_screen_mode(" not in text:
    anchor = "    def _create_menu(self) -> None:\n"

    methods = """    def _set_start_screen_mode(
        self,
    ) -> None:
        self.menuBar().setVisible(False)

        self.project_dock.setVisible(False)
        self.inspector_dock.setVisible(False)
        self.bottom_dock.setVisible(False)

        self.statusBar().setVisible(False)

    def _set_editor_mode(
        self,
    ) -> None:
        self.menuBar().setVisible(True)

        self.project_dock.setVisible(True)
        self.inspector_dock.setVisible(True)
        self.bottom_dock.setVisible(True)

        self.statusBar().setVisible(True)

    def _create_menu(self) -> None:
"""

    if anchor not in text:
        raise RuntimeError(
            "Método _create_menu não encontrado."
        )

    text = text.replace(
        anchor,
        methods,
        1,
    )

# O dock inferior pode ter qualquer variável local no código antigo.
# Converte para self.bottom_dock para poder escondê-lo na StartPage.
text = text.replace(
    '        dock = QDockWidget(\n            "Saída",\n            self,\n        )',
    '        self.bottom_dock = QDockWidget(\n            "Saída",\n            self,\n        )',
    1,
)

text = text.replace(
    "        dock.setWidget(\n            tabs\n        )",
    "        self.bottom_dock.setWidget(\n            tabs\n        )",
    1,
)

text = text.replace(
    "        dock.setMinimumHeight(\n            180\n        )",
    "        self.bottom_dock.setMinimumHeight(\n            180\n        )",
    1,
)

text = text.replace(
    "            dock,\n        )",
    "            self.bottom_dock,\n        )",
    1,
)

# Após toda a interface ser criada no __init__, entra no modo inicial limpo.
init_anchor = """        self._refresh_recent_projects()
        self._update_play_actions()
"""

if (
    init_anchor in text
    and "        self._set_start_screen_mode()\n"
    not in text.split(
        "    def _create_menu",
        1,
    )[0]
):
    text = text.replace(
        init_anchor,
        init_anchor
        + "        self._set_start_screen_mode()\n",
        1,
    )

# Ao abrir um projeto, restaura a interface completa.
open_anchor = """    def _open_project(
        self,
        project: LoadedProject,
    ) -> None:
"""

if open_anchor in text:
    replacement = open_anchor + (
        "        self._set_editor_mode()\n"
    )

    if replacement not in text:
        text = text.replace(
            open_anchor,
            replacement,
            1,
        )

path.write_text(
    text,
    encoding="utf-8",
)

print("main_window.py atualizado para StartPage limpa.")
print(f"Backup: {backup}")
