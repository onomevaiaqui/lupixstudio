import shutil
from pathlib import Path

MODEL = Path(r".\src\lupix_studio\scene\model.py")
EDITOR = Path(r".\src\lupix_studio\ui\area2d_component_editor.py")
PREVIEW = Path(r".\src\lupix_studio\ui\play_preview.py")
RUNTIME = Path(r".\src\lupix_studio\runtime\scene_runtime.py")

for path in (MODEL, EDITOR, PREVIEW, RUNTIME):
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")


def backup(path: Path, suffix: str) -> None:
    target = path.with_suffix(path.suffix + suffix)
    if not target.exists():
        shutil.copy2(path, target)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(
            f"Bloco não encontrado: {label}. "
            "Nenhum arquivo foi alterado nesta etapa."
        )
    return text.replace(old, new, 1)


backup(MODEL, ".bak_set_collider")
text = MODEL.read_text(encoding="utf-8")

if "target_entity_id: str = " not in text:
    text = replace_once(
        text,
        "    player_y: float = 0.0\n",
        "    player_y: float = 0.0\n"
        '    target_entity_id: str = ""\n'
        "    collider_enabled: bool = True\n",
        "campos Area2DAction",
    )

if '"target_entity_id": self.target_entity_id' not in text:
    text = replace_once(
        text,
        '            "player_y": self.player_y,\n',
        '            "player_y": self.player_y,\n'
        '            "target_entity_id": self.target_entity_id,\n'
        '            "collider_enabled": self.collider_enabled,\n',
        "to_dict Area2DAction",
    )

if 'data.get(\n                    "target_entity_id",' not in text:
    anchor = (
        "            player_y=float(\n"
        "                data.get(\n"
        '                    "player_y",\n'
        "                    0.0,\n"
        "                )\n"
        "                or 0.0\n"
        "            ),\n"
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + "            target_entity_id=str(\n"
        + "                data.get(\n"
        + '                    "target_entity_id",\n'
        + '                    "",\n'
        + "                )\n"
        + '                or ""\n'
        + "            ),\n"
        + "            collider_enabled=bool(\n"
        + "                data.get(\n"
        + '                    "collider_enabled",\n'
        + "                    True,\n"
        + "                )\n"
        + "            ),\n",
        "from_dict Area2DAction",
    )

MODEL.write_text(text, encoding="utf-8")


backup(EDITOR, ".bak_set_collider")
text = EDITOR.read_text(encoding="utf-8")

if '"Alterar Collider"' not in text:
    anchor = (
        '        action_combo.addItem(\n'
        '            "Teleportar jogador",\n'
        '            "teleport_player",\n'
        '        )\n'
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + '        action_combo.addItem(\n'
        + '            "Alterar Collider",\n'
        + '            "set_collider",\n'
        + '        )\n',
        "opção Alterar Collider",
    )

if "collider_entity_combo = QComboBox()" not in text:
    anchor = "        scene_combo = QComboBox()\n"
    block = (
        "        collider_entity_combo = QComboBox()\n"
        "        collider_entity_combo.setMinimumWidth(180)\n"
        "        collider_entity_combo.addItem(\n"
        '            "Selecione uma entidade...",\n'
        '            "",\n'
        "        )\n\n"
        "        if self.scene is not None:\n"
        "            selected_entity_index = 0\n"
        "            for scene_entity in self.scene.entities:\n"
        "                if scene_entity.collider is None:\n"
        "                    continue\n\n"
        "                collider_entity_combo.addItem(\n"
        "                    scene_entity.name,\n"
        "                    scene_entity.id,\n"
        "                )\n\n"
        "                if (\n"
        "                    scene_entity.id\n"
        "                    == action.target_entity_id\n"
        "                ):\n"
        "                    selected_entity_index = (\n"
        "                        collider_entity_combo.count() - 1\n"
        "                    )\n\n"
        "            collider_entity_combo.setCurrentIndex(\n"
        "                selected_entity_index\n"
        "            )\n\n"
        "        collider_state_combo = QComboBox()\n"
        "        collider_state_combo.addItem(\n"
        '            "Ativar",\n'
        "            True,\n"
        "        )\n"
        "        collider_state_combo.addItem(\n"
        '            "Desativar",\n'
        "            False,\n"
        "        )\n"
        "        collider_state_combo.setCurrentIndex(\n"
        "            0 if action.collider_enabled else 1\n"
        "        )\n\n"
    )
    text = replace_once(
        text,
        anchor,
        block + anchor,
        "controles Alterar Collider",
    )

if '"Entidade:"' not in text:
    anchor = (
        '        details_layout.addRow(\n'
        '            "Cena destino:",\n'
        '            scene_combo,\n'
        '        )\n'
    )
    block = (
        '        details_layout.addRow(\n'
        '            "Entidade:",\n'
        "            collider_entity_combo,\n"
        "        )\n"
        '        details_layout.addRow(\n'
        '            "Collider:",\n'
        "            collider_state_combo,\n"
        "        )\n"
    )
    text = replace_once(
        text,
        anchor,
        block + anchor,
        "linhas Alterar Collider",
    )

if 'kind == "set_collider"' not in text:
    anchor = (
        "            scene_combo.setVisible(\n"
        '                kind == "change_scene"\n'
        "            )\n"
    )
    block = (
        "            collider_entity_combo.setVisible(\n"
        '                kind == "set_collider"\n'
        "            )\n"
        "            details_layout.labelForField(\n"
        "                collider_entity_combo\n"
        "            ).setVisible(\n"
        '                kind == "set_collider"\n'
        "            )\n\n"
        "            collider_state_combo.setVisible(\n"
        '                kind == "set_collider"\n'
        "            )\n"
        "            details_layout.labelForField(\n"
        "                collider_state_combo\n"
        "            ).setVisible(\n"
        '                kind == "set_collider"\n'
        "            )\n\n"
    )
    text = replace_once(
        text,
        anchor,
        block + anchor,
        "visibilidade Alterar Collider",
    )

if "current.target_entity_id =" not in text:
    anchor = (
        "            current.player_y = (\n"
        "                player_y_spin.value()\n"
        "            )\n"
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + "            current.target_entity_id = str(\n"
        + "                collider_entity_combo.currentData()\n"
        + '                or ""\n'
        + "            )\n"
        + "            current.collider_enabled = bool(\n"
        + "                collider_state_combo.currentData()\n"
        + "            )\n",
        "salvamento Alterar Collider",
    )

if "collider_entity_combo.currentIndexChanged.connect" not in text:
    anchor = (
        "        player_y_spin.valueChanged.connect(\n"
        "            save_row\n"
        "        )\n"
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + "        collider_entity_combo.currentIndexChanged.connect(\n"
        + "            save_row\n"
        + "        )\n"
        + "        collider_state_combo.currentIndexChanged.connect(\n"
        + "            save_row\n"
        + "        )\n",
        "signals Alterar Collider",
    )

EDITOR.write_text(text, encoding="utf-8")


backup(RUNTIME, ".bak_set_collider")
text = RUNTIME.read_text(encoding="utf-8")

if "        self.refresh_collisions()\n" not in text:
    text = replace_once(
        text,
        "        self._load_tilemap_collisions()\n",
        "        self.refresh_collisions()\n",
        "inicialização das colisões",
    )

if "    def refresh_collisions(" not in text:
    marker = "    def _apply_scene_horizontal_bounds(\n"
    method = (
        "    def refresh_collisions(self) -> None:\n"
        "        self._load_tilemap_collisions()\n\n"
        "        player = self.player\n\n"
        "        for entity in self.scene.entities:\n"
        "            if (\n"
        "                player is not None\n"
        "                and entity.id == player.id\n"
        "            ):\n"
        "                continue\n\n"
        "            collider = entity.collider\n\n"
        "            if (\n"
        "                collider is None\n"
        "                or not collider.enabled\n"
        "                or not collider.solid\n"
        "            ):\n"
        "                continue\n\n"
        "            center_x = (\n"
        "                entity.transform.x\n"
        "                + collider.offset_x\n"
        "            )\n"
        "            center_y = (\n"
        "                entity.transform.y\n"
        "                + collider.offset_y\n"
        "            )\n\n"
        "            self.collision_rects.append(\n"
        "                CollisionRect(\n"
        "                    x=(\n"
        "                        center_x\n"
        "                        - collider.width / 2.0\n"
        "                    ),\n"
        "                    y=(\n"
        "                        center_y\n"
        "                        - collider.height / 2.0\n"
        "                    ),\n"
        "                    width=collider.width,\n"
        "                    height=collider.height,\n"
        "                )\n"
        "            )\n\n"
    )

    if marker not in text:
        raise RuntimeError(
            "Ponto para refresh_collisions não encontrado."
        )

    text = text.replace(
        marker,
        method + marker,
        1,
    )

RUNTIME.write_text(text, encoding="utf-8")


backup(PREVIEW, ".bak_set_collider")
text = PREVIEW.read_text(encoding="utf-8")

if 'action_type == "set_collider"' not in text:
    anchor = '        if action_type == "change_scene":\n'
    block = (
        '        if action_type == "set_collider":\n'
        '            if self.runtime is None:\n'
        '                self._finish_area_sequence(\n'
        '                    area_id\n'
        '                )\n'
        '                return\n\n'
        '            target_entity_id = str(\n'
        '                getattr(\n'
        '                    action,\n'
        '                    "target_entity_id",\n'
        '                    "",\n'
        '                )\n'
        '                or ""\n'
        '            )\n\n'
        '            target_entity = (\n'
        '                self.runtime.scene.entity(\n'
        '                    target_entity_id\n'
        '                )\n'
        '            )\n\n'
        '            if (\n'
        '                target_entity is not None\n'
        '                and target_entity.collider is not None\n'
        '            ):\n'
        '                enabled = bool(\n'
        '                    getattr(\n'
        '                        action,\n'
        '                        "collider_enabled",\n'
        '                        True,\n'
        '                    )\n'
        '                )\n\n'
        '                target_entity.collider.enabled = enabled\n'
        '                self.runtime.refresh_collisions()\n\n'
        '                state_text = (\n'
        '                    "ativado"\n'
        '                    if enabled\n'
        '                    else "desativado"\n'
        '                )\n\n'
        '                self.area_event.emit(\n'
        '                    f"Collider {state_text}: "\n'
        '                    f"{target_entity.name}"\n'
        '                )\n\n'
        '                self.canvas.refresh()\n\n'
        '            self._run_area_actions(\n'
        '                area_id,\n'
        '                actions,\n'
        '                index + 1,\n'
        '            )\n'
        '            return\n\n'
    )
    text = replace_once(
        text,
        anchor,
        block + anchor,
        "runtime set_collider",
    )

PREVIEW.write_text(text, encoding="utf-8")

print("Ação 'Alterar Collider' adicionada.")
print("Também foram habilitados Colliders de entidades no runtime.")
