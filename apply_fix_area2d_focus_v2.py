import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\ui\main_window.py")

if not PATH.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {PATH}")

backup = PATH.with_suffix(PATH.suffix + ".bak_area2d_focus_v2")
if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(encoding="utf-8")

start = text.find("    def _on_area2d_changed(")
if start == -1:
    raise RuntimeError("_on_area2d_changed não encontrado.")

end = text.find("\n    def ", start + 5)
if end == -1:
    end = len(text)

region = text[start:end]

old = """        self.entity_inspector.show_entity(
            entity
        )

        self.area2d_editor.set_context(
            self.current_scene,
            entity,
            (
                self.current_project.root
                if self.current_project is not None
                else None
            ),
        )

        self._save_current_scene()
"""

new = """        # Não reconstruir o Inspector/Area2D durante este signal.
        # O editor já alterou o modelo antes de emitir area2d_changed.
        self._save_current_scene()
"""

if new in region:
    print("A correção de foco da Area2D já está aplicada.")
    raise SystemExit(0)

if old not in region:
    raise RuntimeError(
        "Bloco de reconstrução não encontrado em _on_area2d_changed. "
        "Nenhum arquivo foi alterado."
    )

region = region.replace(old, new, 1)
text = text[:start] + region + text[end:]
PATH.write_text(text, encoding="utf-8")

print("Correção aplicada.")
print("- Area2D não é reconstruída durante edição")
print("- Mensagem mantém foco")
print("- Backspace e Ctrl+V devem funcionar")
print("- salvamento continua ativo")
print(f"Backup: {backup}")
