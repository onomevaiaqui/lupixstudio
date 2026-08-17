
import re
import shutil
from pathlib import Path

PROJECT = Path.cwd()
UI = PROJECT / "src" / "lupix_studio" / "ui"

main_window = UI / "main_window.py"
panel = UI / "entity_inspector_panel.py"
tree = UI / "scene_tree.py"

for path in (main_window, panel, tree):
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}")

    backup = path.with_suffix(
        path.suffix + ".bak_area2d"
    )

    if not backup.exists():
        shutil.copy2(path, backup)


def replace_once(text, old, new, label):
    if new in text:
        return text

    if old not in text:
        raise RuntimeError(
            f"Não encontrei o bloco esperado: {label}"
        )

    return text.replace(old, new, 1)


# =========================================================
# entity_inspector_panel.py
# =========================================================
text = panel.read_text(encoding="utf-8")

text = replace_once(
    text,
    '    SECTION_COLLIDER = "collider"\n'
    '    SECTION_PLAYER = "player"\n',
    '    SECTION_COLLIDER = "collider"\n'
    '    SECTION_AREA2D = "area2d"\n'
    '    SECTION_PLAYER = "player"\n',
    "SECTION_AREA2D",
)

text = replace_once(
    text,
    "        collider_editor: QWidget,\n"
    "        player_editor: QWidget,\n",
    "        collider_editor: QWidget,\n"
    "        area2d_editor: QWidget,\n"
    "        player_editor: QWidget,\n",
    "parâmetro area2d_editor",
)

old_section = (
    "        self._add_section(\n"
    "            layout,\n"
    "            self.SECTION_COLLIDER,\n"
    '            "Collider",\n'
    "            collider_editor,\n"
    "        )\n\n"
    "        self._add_section(\n"
    "            layout,\n"
    "            self.SECTION_PLAYER,\n"
)

new_section = (
    "        self._add_section(\n"
    "            layout,\n"
    "            self.SECTION_COLLIDER,\n"
    '            "Collider",\n'
    "            collider_editor,\n"
    "        )\n\n"
    "        self._add_section(\n"
    "            layout,\n"
    "            self.SECTION_AREA2D,\n"
    '            "Area2D",\n'
    "            area2d_editor,\n"
    "        )\n\n"
    "        self._add_section(\n"
    "            layout,\n"
    "            self.SECTION_PLAYER,\n"
)

text = replace_once(
    text,
    old_section,
    new_section,
    "seção Area2D",
)

panel.write_text(
    text,
    encoding="utf-8",
)


# =========================================================
# scene_tree.py
# =========================================================
text = tree.read_text(encoding="utf-8")

if '                "area2d",' not in text:
    old = (
        "        if entity.player_controller is not None:\n"
        '            label = "Player Controller"\n'
    )

    new = (
        "        if entity.area2d is not None:\n"
        '            label = "Area2D"\n\n'
        "            if not entity.area2d.enabled:\n"
        '                label += " (desativada)"\n\n'
        "            self._add_component_item(\n"
        "                parent,\n"
        "                entity,\n"
        '                "area2d",\n'
        "                label,\n"
        "            )\n\n"
        "        if entity.player_controller is not None:\n"
        '            label = "Player Controller"\n'
    )

    if old not in text:
        raise RuntimeError(
            "Não encontrei o bloco Player Controller no SceneTree."
        )

    text = text.replace(
        old,
        new,
        1,
    )

tree.write_text(
    text,
    encoding="utf-8",
)


# =========================================================
# main_window.py
# =========================================================
text = main_window.read_text(
    encoding="utf-8"
)

# import
if "Area2DComponentEditor" not in text:
    anchor = (
        "from lupix_studio.ui.camera_component_editor import (\n"
        "    CameraComponentEditor,\n"
        ")\n"
    )

    replacement = (
        anchor
        + "from lupix_studio.ui.area2d_component_editor import (\n"
        + "    Area2DComponentEditor,\n"
        + ")\n"
    )

    if anchor not in text:
        raise RuntimeError(
            "Import de CameraComponentEditor não encontrado."
        )

    text = text.replace(
        anchor,
        replacement,
        1,
    )

# instance
if "self.area2d_editor = Area2DComponentEditor()" not in text:
    text = replace_once(
        text,
        "        self.collider_editor = ColliderComponentEditor()\n"
        "        self.player_editor = PlayerControllerEditor()\n",
        "        self.collider_editor = ColliderComponentEditor()\n"
        "        self.area2d_editor = Area2DComponentEditor()\n"
        "        self.player_editor = PlayerControllerEditor()\n",
        "instância Area2DComponentEditor",
    )

# panel arg
if "area2d_editor=self.area2d_editor" not in text:
    text = replace_once(
        text,
        "            collider_editor=self.collider_editor,\n"
        "            player_editor=self.player_editor,\n",
        "            collider_editor=self.collider_editor,\n"
        "            area2d_editor=self.area2d_editor,\n"
        "            player_editor=self.player_editor,\n",
        "argumento area2d_editor",
    )

# signal
if "self.area2d_editor.area2d_changed.connect" not in text:
    old = (
        "        self.collider_editor.collider_changed.connect(\n"
        "            self._on_collider_changed\n"
        "        )\n\n"
        "        self.player_editor.player_changed.connect(\n"
    )

    new = (
        "        self.collider_editor.collider_changed.connect(\n"
        "            self._on_collider_changed\n"
        "        )\n\n"
        "        self.area2d_editor.area2d_changed.connect(\n"
        "            self._on_area2d_changed\n"
        "        )\n\n"
        "        self.player_editor.player_changed.connect(\n"
    )

    text = replace_once(
        text,
        old,
        new,
        "signal Area2D",
    )

# section map
if '"area2d": (' not in text:
    old = (
        '            "collider": (\n'
        "                EntityInspectorPanel.SECTION_COLLIDER\n"
        "            ),\n"
        '            "player": (\n'
    )

    new = (
        '            "collider": (\n'
        "                EntityInspectorPanel.SECTION_COLLIDER\n"
        "            ),\n"
        '            "area2d": (\n'
        "                EntityInspectorPanel.SECTION_AREA2D\n"
        "            ),\n"
        '            "player": (\n'
    )

    text = replace_once(
        text,
        old,
        new,
        "section map Area2D",
    )

# Duplicate collider set_context calls for area2d.
pattern = re.compile(
    r"(?P<indent>^[ \t]*)self\.collider_editor\.set_context\("
    r"(?P<body>.*?)"
    r"(?P=indent)\)\n",
    re.MULTILINE | re.DOTALL,
)

matches = list(
    pattern.finditer(text)
)

for match in reversed(matches):
    block = match.group(0)
    area_block = block.replace(
        "self.collider_editor.set_context",
        "self.area2d_editor.set_context",
        1,
    )

    after = text[
        match.end():
        min(len(text), match.end() + len(area_block) + 80)
    ]

    if "self.area2d_editor.set_context" in after:
        continue

    text = (
        text[:match.end()]
        + "\n"
        + area_block
        + text[match.end():]
    )

# Clone collider handler.
if "def _on_area2d_changed(" not in text:
    handler_pattern = re.compile(
        r"(?ms)^    def _on_collider_changed\("
        r".*?"
        r"(?=^    def )"
    )

    match = handler_pattern.search(text)

    if match is None:
        raise RuntimeError(
            "_on_collider_changed não encontrado."
        )

    handler = match.group(0)

    area_handler = handler.replace(
        "_on_collider_changed",
        "_on_area2d_changed",
        1,
    ).replace(
        "collider_editor",
        "area2d_editor",
    )

    text = (
        text[:match.end()]
        + "\n"
        + area_handler
        + text[match.end():]
    )

main_window.write_text(
    text,
    encoding="utf-8",
)

print("Patch Area2D aplicado.")
print("Backups: *.bak_area2d")
