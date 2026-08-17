import shutil
from pathlib import Path

path = Path(r".\src\lupix_studio\ui\main_window.py")

if not path.exists():
    raise SystemExit(
        f"Arquivo não encontrado: {path.resolve()}"
    )

backup = path.with_suffix(
    path.suffix + ".bak_area2d_context"
)

if not backup.exists():
    shutil.copy2(
        path,
        backup,
    )

text = path.read_text(
    encoding="utf-8"
)

# Corrige chamadas com None.
text = text.replace(
    '''self.area2d_editor.set_context(
            None
        )''',
    '''self.area2d_editor.set_context(
            None,
            None,
        )''',
)

# Corrige chamadas com entity.
text = text.replace(
    '''self.area2d_editor.set_context(
            entity
        )''',
    '''self.area2d_editor.set_context(
            self.current_scene,
            entity,
        )''',
)

# Remove duplicação consecutiva mais comum.
duplicate = '''self.area2d_editor.set_context(
            self.current_scene,
            entity,
        )

        self.area2d_editor.set_context(
            self.current_scene,
            entity,
        )'''

single = '''self.area2d_editor.set_context(
            self.current_scene,
            entity,
        )'''

while duplicate in text:
    text = text.replace(
        duplicate,
        single,
        1,
    )

path.write_text(
    text,
    encoding="utf-8"
)

print("Correção aplicada com sucesso.")
print(f"Backup criado em: {backup}")
print()
print("Agora rode:")
print(
    r'python -m py_compile ".\src\lupix_studio\ui\main_window.py"'
)
print("python -m ruff check . --fix")
print("python -m lupix_studio")
