import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\ui\area2d_component_editor.py")

if not PATH.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {PATH}")

backup = PATH.with_suffix(PATH.suffix + ".bak_arrow_colors")

if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(encoding="utf-8")

old = (
    '        up_button.setIcon(\n'
    '            self.style().standardIcon(\n'
    '                QStyle.StandardPixmap.SP_ArrowUp\n'
    '            )\n'
    '        )\n'
    '        down_button.setIcon(\n'
    '            self.style().standardIcon(\n'
    '                QStyle.StandardPixmap.SP_ArrowDown\n'
    '            )\n'
    '        )\n'
)

new = (
    '        up_button.setText("↑")\n'
    '        down_button.setText("↓")\n\n'
    '        arrow_style = (\n'
    '            "QToolButton {"\n'
    '            " color: #f2f2f2;"\n'
    '            " background-color: #2a2d33;"\n'
    '            " border: 1px solid #3a3e46;"\n'
    '            " border-radius: 4px;"\n'
    '            " font-size: 18px;"\n'
    '            " font-weight: 700;"\n'
    '            " padding: 0px;"\n'
    '            " }"\n'
    '            " QToolButton:hover {"\n'
    '            " color: #ffffff;"\n'
    '            " background-color: #343840;"\n'
    '            " border-color: #555b66;"\n'
    '            " }"\n'
    '            " QToolButton:pressed {"\n'
    '            " background-color: #202329;"\n'
    '            " }"\n'
    '            " QToolButton:disabled {"\n'
    '            " color: #666b73;"\n'
    '            " background-color: #24272c;"\n'
    '            " border-color: #30343a;"\n'
    '            " }"\n'
    '        )\n\n'
    '        up_button.setStyleSheet(arrow_style)\n'
    '        down_button.setStyleSheet(arrow_style)\n'
)

if old not in text:
    raise RuntimeError(
        "Bloco atual das setas não encontrado. Nenhum arquivo foi alterado."
    )

text = text.replace(old, new, 1)

PATH.write_text(text, encoding="utf-8")

print("Correção aplicada.")
print("Somente as setas ↑ e ↓ foram alteradas.")
print(f"Backup: {backup}")
