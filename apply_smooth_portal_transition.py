import shutil
from pathlib import Path

PATH = Path(
    r".\\src\\lupix_studio\\ui\\play_preview.py"
)

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_smooth_portal"
)

if not backup.exists():
    shutil.copy2(
        PATH,
        backup,
    )

text = PATH.read_text(
    encoding="utf-8"
)

old = (
    '                if target_scene:\n'
    '                    if self.runtime is not None:\n'
    '                        self.runtime.running = False\n\n'
    '                    QTimer.singleShot(\n'
    '                        3000,\n'
)

new = (
    '                if target_scene:\n'
    '                    QTimer.singleShot(\n'
    '                        3000,\n'
)

if old not in text:
    raise RuntimeError(
        "Bloco de pausa do runtime não encontrado."
    )

text = text.replace(
    old,
    new,
    1,
)

PATH.write_text(
    text,
    encoding="utf-8",
)

print(
    "Transição suavizada: o runtime não será mais pausado "
    "durante a mensagem."
)
print(f"Backup: {backup}")
