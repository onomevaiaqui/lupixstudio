import shutil
from pathlib import Path

ROOT = Path(r".\src\lupix_studio")

EDITOR = ROOT / "ui" / "area2d_component_editor.py"
PREVIEW = ROOT / "ui" / "play_preview.py"


def backup(path: Path, suffix: str) -> None:
    backup_path = path.with_suffix(
        path.suffix + suffix
    )

    if not backup_path.exists():
        shutil.copy2(
            path,
            backup_path,
        )


def replace_once(
    text: str,
    old: str,
    new: str,
    label: str,
) -> str:
    if old not in text:
        raise RuntimeError(
            f"Bloco não encontrado: {label}"
        )

    return text.replace(
        old,
        new,
        1,
    )


# ==========================================================
# 1. CORRIGE O EDITOR
# ==========================================================

backup(
    EDITOR,
    ".bak_repair_actions_editor",
)

text = EDITOR.read_text(
    encoding="utf-8"
)

# Evita perder foco a cada letra digitada.
text = text.replace(
    """        message_edit.textChanged.connect(
            save_row
        )
""",
    """        message_edit.editingFinished.connect(
            save_row
        )
""",
)

# Troca símbolos que podem não aparecer na fonte do sistema.
text = text.replace(
    '        up_button = QPushButton("↑")\n'
    '        down_button = QPushButton("↓")\n'
    '        remove_button = QPushButton("×")\n',
    '        up_button = QPushButton("Subir")\n'
    '        down_button = QPushButton("Descer")\n'
    '        remove_button = QPushButton("Remover")\n',
)

# Dá espaço suficiente para os textos dos botões.
text = text.replace(
    """        for button in (
            up_button,
            down_button,
            remove_button,
        ):
            button.setFixedWidth(30)
""",
    """        up_button.setFixedWidth(52)
        down_button.setFixedWidth(60)
        remove_button.setFixedWidth(68)
""",
)

EDITOR.write_text(
    text,
    encoding="utf-8",
)


# ==========================================================
# 2. CORRIGE O PREVIEW / SEQUENCE GUARD
# ==========================================================

backup(
    PREVIEW,
    ".bak_repair_actions_preview",
)

text = PREVIEW.read_text(
    encoding="utf-8"
)

class_marker = "class PlayPreview(QWidget):"

class_start = text.find(
    class_marker
)

if class_start < 0:
    raise RuntimeError(
        "class PlayPreview não encontrada."
    )

preview_text = text[class_start:]

anchor = """        self.project_root: Path | None = None
        self.runtime: SceneRuntime | None = None
"""

if anchor not in preview_text:
    raise RuntimeError(
        "Atributos project_root/runtime do PlayPreview não encontrados."
    )

# Só adiciona se ainda não existir DENTRO de PlayPreview.
before_change_scene = preview_text.split(
    "    def _change_scene(",
    1,
)[0]

if (
    "self.active_area_sequences"
    not in before_change_scene
):
    preview_text = preview_text.replace(
        anchor,
        anchor
        + """
        self.active_area_sequences: set[str] = set()
""",
        1,
    )

# Segurança adicional: inicializa caso uma versão antiga do __init__
# ainda não tenha sido corrigida.
runtime_anchor = """    def _update_runtime(self) -> None:
        if self.runtime is None:
            return
"""

runtime_replacement = """    def _update_runtime(self) -> None:
        if self.runtime is None:
            return

        if not hasattr(
            self,
            "active_area_sequences",
        ):
            self.active_area_sequences = set()
"""

if runtime_anchor in preview_text:
    preview_text = preview_text.replace(
        runtime_anchor,
        runtime_replacement,
        1,
    )

text = (
    text[:class_start]
    + preview_text
)

PREVIEW.write_text(
    text,
    encoding="utf-8",
)

print()
print("Reparo aplicado.")
print()
print("Corrigido:")
print("- campo Mensagem não perde mais o foco a cada letra;")
print("- botões agora mostram Subir / Descer / Remover;")
print("- active_area_sequences fica garantido no PlayPreview;")
print("- _update_runtime possui fallback seguro.")
print()
print("Backups criados antes das alterações.")
