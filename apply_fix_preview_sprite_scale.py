import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\ui\play_preview.py")

if not PATH.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {PATH}")

backup = PATH.with_suffix(PATH.suffix + ".bak_preview_sprite_scale")
if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(encoding="utf-8")

old = """        scale_x = (
            -1.0
            if entity.sprite.flip_x
            else 1.0
        )

        scale_y = (
            -1.0
            if entity.sprite.flip_y
            else 1.0
        )
"""

new = """        scale_x = (
            entity.transform.scale_x
            * (
                -1.0
                if entity.sprite.flip_x
                else 1.0
            )
        )

        scale_y = (
            entity.transform.scale_y
            * (
                -1.0
                if entity.sprite.flip_y
                else 1.0
            )
        )
"""

if old not in text:
    if "def _apply_sprite_item_settings" in text and "entity.transform.scale_x" in text:
        print("O Preview já parece aplicar a escala do Transform ao Sprite.")
        raise SystemExit(0)
    raise RuntimeError("Bloco de escala do Sprite não encontrado. Nenhum arquivo foi alterado.")

text = text.replace(old, new, 1)
PATH.write_text(text, encoding="utf-8")

print("Correção aplicada.")
print("- Preview agora respeita Scale X e Scale Y do Transform")
print("- Flip X/Flip Y continuam funcionando")
print("- animações usam a mesma escala")
print(f"Backup: {backup}")
