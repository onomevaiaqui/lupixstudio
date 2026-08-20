import shutil
from pathlib import Path

MODEL = Path(r".\src\lupix_studio\scene\model.py")
EDITOR = Path(r".\src\lupix_studio\ui\area2d_component_editor.py")
PREVIEW = Path(r".\src\lupix_studio\ui\play_preview.py")

for path in (MODEL, EDITOR, PREVIEW):
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")


def backup(path: Path, suffix: str) -> None:
    target = path.with_suffix(path.suffix + suffix)
    if not target.exists():
        shutil.copy2(path, target)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(
            f"Bloco não encontrado: {label}. Nenhum arquivo foi alterado."
        )
    return text.replace(old, new, 1)


backup(MODEL, ".bak_teleport_player")
text = MODEL.read_text(encoding="utf-8")

if "player_x: float = 0.0" not in text:
    text = replace_once(
        text,
        "    wait_seconds: float = 0.0\n",
        "    wait_seconds: float = 0.0\n"
        "    player_x: float = 0.0\n"
        "    player_y: float = 0.0\n",
        "campos Area2DAction",
    )

if '"player_x": self.player_x' not in text:
    text = replace_once(
        text,
        '            "wait_seconds": self.wait_seconds,\n',
        '            "wait_seconds": self.wait_seconds,\n'
        '            "player_x": self.player_x,\n'
        '            "player_y": self.player_y,\n',
        "to_dict Area2DAction",
    )

if 'data.get(\n                    "player_x",' not in text:
    anchor = (
        "            wait_seconds=max(\n"
        "                0.0,\n"
        "                float(\n"
        "                    data.get(\n"
        '                        "wait_seconds",\n'
        "                        0.0,\n"
        "                    )\n"
        "                    or 0.0\n"
        "                ),\n"
        "            ),\n"
    )
    extra = (
        anchor
        + "            player_x=float(\n"
        + "                data.get(\n"
        + '                    "player_x",\n'
        + "                    0.0,\n"
        + "                )\n"
        + "                or 0.0\n"
        + "            ),\n"
        + "            player_y=float(\n"
        + "                data.get(\n"
        + '                    "player_y",\n'
        + "                    0.0,\n"
        + "                )\n"
        + "                or 0.0\n"
        + "            ),\n"
    )
    text = replace_once(
        text,
        anchor,
        extra,
        "from_dict Area2DAction",
    )

MODEL.write_text(text, encoding="utf-8")


backup(EDITOR, ".bak_teleport_player")
text = EDITOR.read_text(encoding="utf-8")

if '"Teleportar jogador"' not in text:
    anchor = (
        '        action_combo.addItem(\n'
        '            "Aguardar",\n'
        '            "wait",\n'
        '        )\n'
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + '        action_combo.addItem(\n'
        + '            "Teleportar jogador",\n'
        + '            "teleport_player",\n'
        + '        )\n',
        "opção teleport_player",
    )

if "player_x_spin = self._offset_spin()" not in text:
    text = replace_once(
        text,
        "        scene_combo = QComboBox()\n",
        "        player_x_spin = self._offset_spin()\n"
        "        player_y_spin = self._offset_spin()\n\n"
        "        player_x_spin.setValue(\n"
        "            action.player_x\n"
        "        )\n"
        "        player_y_spin.setValue(\n"
        "            action.player_y\n"
        "        )\n\n"
        "        scene_combo = QComboBox()\n",
        "campos teleport_player",
    )

if '"Posição X:"' not in text:
    anchor = (
        '        details_layout.addRow(\n'
        '            "Cena destino:",\n'
        '            scene_combo,\n'
        '        )\n'
    )
    text = replace_once(
        text,
        anchor,
        '        details_layout.addRow(\n'
        '            "Posição X:",\n'
        '            player_x_spin,\n'
        '        )\n'
        '        details_layout.addRow(\n'
        '            "Posição Y:",\n'
        '            player_y_spin,\n'
        '        )\n'
        + anchor,
        "linhas posição",
    )

if 'kind == "teleport_player"' not in text:
    anchor = (
        "            scene_combo.setVisible(\n"
        '                kind == "change_scene"\n'
        "            )\n"
    )
    text = replace_once(
        text,
        anchor,
        "            player_x_spin.setVisible(\n"
        '                kind == "teleport_player"\n'
        "            )\n"
        "            details_layout.labelForField(\n"
        "                player_x_spin\n"
        "            ).setVisible(\n"
        '                kind == "teleport_player"\n'
        "            )\n\n"
        "            player_y_spin.setVisible(\n"
        '                kind == "teleport_player"\n'
        "            )\n"
        "            details_layout.labelForField(\n"
        "                player_y_spin\n"
        "            ).setVisible(\n"
        '                kind == "teleport_player"\n'
        "            )\n\n"
        + anchor,
        "visibilidade posição",
    )

if "current.player_x =" not in text:
    anchor = (
        "            current.target_scene = str(\n"
        "                scene_combo.currentData()\n"
        '                or ""\n'
        "            )\n"
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + "            current.player_x = (\n"
        + "                player_x_spin.value()\n"
        + "            )\n"
        + "            current.player_y = (\n"
        + "                player_y_spin.value()\n"
        + "            )\n",
        "salvamento posição",
    )

if "player_x_spin.valueChanged.connect" not in text:
    anchor = (
        "        wait_spin.valueChanged.connect(\n"
        "            save_row\n"
        "        )\n"
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + "        player_x_spin.valueChanged.connect(\n"
        + "            save_row\n"
        + "        )\n"
        + "        player_y_spin.valueChanged.connect(\n"
        + "            save_row\n"
        + "        )\n",
        "signals posição",
    )

EDITOR.write_text(text, encoding="utf-8")


backup(PREVIEW, ".bak_teleport_player")
text = PREVIEW.read_text(encoding="utf-8")

if 'action_type == "teleport_player"' not in text:
    anchor = '        if action_type == "change_scene":\n'
    block = (
        '        if action_type == "teleport_player":\n'
        "            if self.runtime is None:\n"
        "                self._finish_area_sequence(\n"
        "                    area_id\n"
        "                )\n"
        "                return\n\n"
        "            player = self.runtime.scene.player_entity()\n\n"
        "            if player is not None:\n"
        "                player.transform.x = float(\n"
        "                    getattr(action, \"player_x\", 0.0)\n"
        "                    or 0.0\n"
        "                )\n"
        "                player.transform.y = float(\n"
        "                    getattr(action, \"player_y\", 0.0)\n"
        "                    or 0.0\n"
        "                )\n\n"
        "                self.area_event.emit(\n"
        '                    "Jogador teleportado para "\n'
        '                    f"({player.transform.x:.1f}, "\n'
        '                    f"{player.transform.y:.1f})"\n'
        "                )\n"
        "                self.canvas.refresh()\n\n"
        "            self._run_area_actions(\n"
        "                area_id,\n"
        "                actions,\n"
        "                index + 1,\n"
        "            )\n"
        "            return\n\n"
    )
    text = replace_once(
        text,
        anchor,
        block + anchor,
        "runtime teleport_player",
    )

PREVIEW.write_text(text, encoding="utf-8")

print("Ação 'Teleportar jogador' adicionada.")
print("Arquivos alterados:")
print("- scene/model.py")
print("- ui/area2d_component_editor.py")
print("- ui/play_preview.py")
