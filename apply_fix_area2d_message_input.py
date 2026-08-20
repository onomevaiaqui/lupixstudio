import shutil
from pathlib import Path

PATH = Path(
    r".\src\lupix_studio\ui\area2d_component_editor.py"
)

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_message_input"
)

if not backup.exists():
    shutil.copy2(
        PATH,
        backup,
    )

text = PATH.read_text(
    encoding="utf-8"
)

old = """        message_edit.textChanged.connect(
            save_row
        )
"""

new = """        message_edit.editingFinished.connect(
            save_row
        )
"""

if old in text:
    text = text.replace(
        old,
        new,
        1,
    )

elif new in text:
    print(
        "O campo de mensagem já usa editingFinished."
    )
    print(
        "Nenhuma alteração foi necessária."
    )
    raise SystemExit(0)

else:
    raise RuntimeError(
        "Não foi possível localizar o signal "
        "do campo message_edit. "
        "Nenhum arquivo foi alterado."
    )

PATH.write_text(
    text,
    encoding="utf-8",
)

print("Correção aplicada.")
print()
print("- o Inspector não é reconstruído a cada letra")
print("- é possível digitar normalmente")
print("- Ctrl+V funciona no campo Mensagem")
print("- o texto é salvo ao terminar a edição")
print(f"Backup: {backup}")
