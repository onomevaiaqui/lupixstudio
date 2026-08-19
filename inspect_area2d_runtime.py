import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\ui\play_preview.py")

if not PATH.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {PATH}")

backup = PATH.with_suffix(PATH.suffix + ".bak_runtime_actions")
if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(encoding="utf-8")

# Mostra regiões importantes para confirmar a estrutura atual antes
# de aplicar a alteração definitiva do runtime.
patterns = (
    "def _update_runtime",
    "consume_area_events",
    "area_event.emit",
    "def _change_scene",
    "message_change_scene",
)

print("=" * 72)
print("DIAGNÓSTICO DO RUNTIME DE AÇÕES - LUPIX STUDIO")
print("=" * 72)

lines = text.splitlines()

for pattern in patterns:
    matches = [
        index
        for index, line in enumerate(lines)
        if pattern in line
    ]

    print()
    print(f">>> {pattern}")

    if not matches:
        print("NÃO ENCONTRADO")
        continue

    for index in matches:
        start = max(0, index - 8)
        end = min(len(lines), index + 36)

        print(
            f"\n--- linhas {start + 1} a {end} ---"
        )

        for number in range(start, end):
            print(
                f"{number + 1:04d}: {lines[number]}"
            )

print()
print("=" * 72)
print("Nenhum arquivo foi alterado.")
print("Envie a saída acima para continuarmos com o patch do runtime.")
print("=" * 72)
