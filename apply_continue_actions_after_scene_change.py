import shutil
from pathlib import Path

PATH = Path(
    r".\src\lupix_studio\ui\play_preview.py"
)

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_scene_action_continuation"
)

if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(
    encoding="utf-8"
)

old = '''        if action_type == "change_scene":
            target_scene = str(
                getattr(
                    action,
                    "target_scene",
                    "",
                )
                or ""
            ).strip()

            self._finish_area_sequence(
                area_id
            )

            if target_scene:
                self._change_scene(
                    target_scene
                )

            return
'''

new = '''        if action_type == "change_scene":
            target_scene = str(
                getattr(
                    action,
                    "target_scene",
                    "",
                )
                or ""
            ).strip()

            remaining_actions = actions[
                index + 1:
            ]

            self._finish_area_sequence(
                area_id
            )

            if not target_scene:
                return

            changed = self._change_scene(
                target_scene
            )

            if (
                changed
                and remaining_actions
            ):
                QTimer.singleShot(
                    0,
                    lambda: self._run_area_actions(
                        area_id,
                        remaining_actions,
                        0,
                    ),
                )

            return
'''

if old not in text:
    raise RuntimeError(
        "Bloco change_scene da sequência não encontrado. "
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
    "- ações posteriores a Trocar cena agora continuam "
    "na cena de destino"
)
print(
    "- exemplo suportado: Trocar cena -> Aguardar -> Mensagem"
)
print(f"Backup: {backup}")
