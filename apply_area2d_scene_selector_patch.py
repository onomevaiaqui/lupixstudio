import shutil
from pathlib import Path

path = Path(
    r".\src\lupix_studio\ui\main_window.py"
)

if not path.exists():
    raise SystemExit(
        f"Arquivo não encontrado: {path.resolve()}"
    )

backup = path.with_suffix(
    path.suffix + ".bak_scene_selector"
)

if not backup.exists():
    shutil.copy2(
        path,
        backup,
    )

text = path.read_text(
    encoding="utf-8"
)

old_none = '''self.area2d_editor.set_context(
            None,
            None,
        )'''

new_none = '''self.area2d_editor.set_context(
            None,
            None,
            (
                self.current_project.root
                if self.current_project is not None
                else None
            ),
        )'''

old_entity = '''self.area2d_editor.set_context(
            self.current_scene,
            entity,
        )'''

new_entity = '''self.area2d_editor.set_context(
            self.current_scene,
            entity,
            (
                self.current_project.root
                if self.current_project is not None
                else None
            ),
        )'''

count_none = text.count(old_none)
count_entity = text.count(old_entity)

text = text.replace(
    old_none,
    new_none,
)

text = text.replace(
    old_entity,
    new_entity,
)

path.write_text(
    text,
    encoding="utf-8",
)

print(
    f"Chamadas com None atualizadas: {count_none}"
)

print(
    f"Chamadas com entidade atualizadas: {count_entity}"
)

print(
    f"Backup: {backup}"
)
