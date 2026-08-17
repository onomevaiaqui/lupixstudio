import shutil
from pathlib import Path

path = Path(r".\src\lupix_studio\ui\main_window.py")

if not path.exists():
    raise SystemExit(
        f"Arquivo não encontrado: {path.resolve()}"
    )

backup = path.with_suffix(
    path.suffix + ".bak_area2d_console"
)

if not backup.exists():
    shutil.copy2(
        path,
        backup,
    )

text = path.read_text(
    encoding="utf-8"
)

# ---------------------------------------------------------
# 1) Conecta o sinal do PlayPreview ao console.
# ---------------------------------------------------------
if (
    "self.workspace.play_preview.area_event.connect"
    not in text
):
    anchor = '''        self.workspace.play_stop_requested.connect(
            self._stop_play_preview
        )
'''

    replacement = '''        self.workspace.play_stop_requested.connect(
            self._stop_play_preview
        )

        self.workspace.play_preview.area_event.connect(
            self._on_play_area_event
        )
'''

    if anchor not in text:
        raise RuntimeError(
            "Conexão play_stop_requested não encontrada."
        )

    text = text.replace(
        anchor,
        replacement,
        1,
    )

# ---------------------------------------------------------
# 2) Adiciona o handler no MainWindow.
# ---------------------------------------------------------
if "def _on_play_area_event(" not in text:
    anchor = '''    def _stop_play_preview(
'''

    handler = '''    def _on_play_area_event(
        self,
        message: str,
    ) -> None:
        self.console.append(
            message
        )

    def _stop_play_preview(
'''

    if anchor not in text:
        raise RuntimeError(
            "Método _stop_play_preview não encontrado."
        )

    text = text.replace(
        anchor,
        handler,
        1,
    )

path.write_text(
    text,
    encoding="utf-8",
)

print("Integração Area2D -> Console aplicada.")
print(f"Backup criado em: {backup}")
