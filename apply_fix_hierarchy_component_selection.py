import shutil
from pathlib import Path

PATH = Path(
    r".\\src\\lupix_studio\\ui\\main_window.py"
)

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_hierarchy_component_selection"
)

if not backup.exists():
    shutil.copy2(
        PATH,
        backup,
    )

text = PATH.read_text(
    encoding="utf-8"
)

old = '''        self.workspace.scene_viewport.select_component(
            entity_id,
            component,
        )
'''

new = '''        self.workspace.scene_viewport.select_entity(
            entity_id
        )
'''

if old not in text:
    if "scene_viewport.select_component(" not in text:
        print(
            "Nenhuma chamada select_component encontrada. "
            "O arquivo pode já estar corrigido."
        )
        raise SystemExit(0)

    raise RuntimeError(
        "A chamada select_component existe, "
        "mas está em um formato diferente do esperado. "
        "Nenhum arquivo foi alterado."
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

print("Correção aplicada.")
print(
    "- seleção de componente agora seleciona "
    "a entidade correspondente no viewport"
)
print(
    "- o Inspector continua abrindo a seção "
    "do componente escolhido"
)
print(f"Backup: {backup}")
