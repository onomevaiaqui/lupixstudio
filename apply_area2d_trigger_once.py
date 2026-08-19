import shutil
from pathlib import Path

ROOT = Path(r".\src\lupix_studio")
MODEL = ROOT / "scene" / "model.py"
EDITOR = ROOT / "ui" / "area2d_component_editor.py"
RUNTIME = ROOT / "runtime" / "scene_runtime.py"


def backup(path: Path) -> None:
    backup_path = path.with_suffix(path.suffix + ".bak_trigger_once")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def replace_once(text: str, old: str, new: str, description: str) -> str:
    if old not in text:
        raise RuntimeError(f"Não encontrei o bloco: {description}")
    return text.replace(old, new, 1)


def patch_model() -> None:
    backup(MODEL)
    text = MODEL.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '    on_enter_action: str = "none"\n    target_scene: str = ""\n',
        '    on_enter_action: str = "none"\n'
        '    target_scene: str = ""\n'
        '    trigger_once: bool = False\n',
        "campos do Area2DComponent",
    )

    text = replace_once(
        text,
        '                "action": self.on_enter_action,\n'
        '                "target_scene": self.target_scene,\n',
        '                "action": self.on_enter_action,\n'
        '                "target_scene": self.target_scene,\n'
        '                "trigger_once": self.trigger_once,\n',
        "serialização on_enter",
    )

    text = replace_once(
        text,
        '            target_scene=str(\n'
        '                on_enter.get(\n'
        '                    "target_scene",\n'
        '                    "",\n'
        '                )\n'
        '                or ""\n'
        '            ),\n',
        '            target_scene=str(\n'
        '                on_enter.get(\n'
        '                    "target_scene",\n'
        '                    "",\n'
        '                )\n'
        '                or ""\n'
        '            ),\n'
        '            trigger_once=bool(\n'
        '                on_enter.get(\n'
        '                    "trigger_once",\n'
        '                    False,\n'
        '                )\n'
        '            ),\n',
        "desserialização on_enter",
    )

    MODEL.write_text(text, encoding="utf-8")


def patch_editor() -> None:
    backup(EDITOR)
    text = EDITOR.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '        self.events_title = QLabel("Eventos")\n'
        '        self.events_title.setStyleSheet(\n'
        '            "font-weight: 600; margin-top: 8px;"\n'
        '        )\n\n'
        '        self.enter_action_combo = QComboBox()\n',
        '        self.events_title = QLabel("Eventos")\n'
        '        self.events_title.setStyleSheet(\n'
        '            "font-weight: 600; margin-top: 8px;"\n'
        '        )\n\n'
        '        self.trigger_once_checkbox = QCheckBox(\n'
        '            "Executar apenas uma vez"\n'
        '        )\n\n'
        '        self.trigger_once_checkbox.setToolTip(\n'
        '            "Quando ativo, o evento Ao entrar só é "\n'
        '            "disparado na primeira entrada durante a execução."\n'
        '        )\n\n'
        '        self.enter_action_combo = QComboBox()\n',
        "criação do checkbox",
    )

    text = replace_once(
        text,
        '        layout.addWidget(self.events_title)\n'
        '        layout.addLayout(event_form)\n'
        '        layout.addWidget(self.hint_label)\n',
        '        layout.addWidget(self.events_title)\n'
        '        layout.addLayout(event_form)\n'
        '        layout.addWidget(self.trigger_once_checkbox)\n'
        '        layout.addWidget(self.hint_label)\n',
        "checkbox no layout",
    )

    text = replace_once(
        text,
        '        self.target_scene_combo.currentIndexChanged.connect(\n'
        '            self._apply\n'
        '        )\n'
        '        self.refresh_scenes_button.clicked.connect(\n',
        '        self.target_scene_combo.currentIndexChanged.connect(\n'
        '            self._apply\n'
        '        )\n'
        '        self.trigger_once_checkbox.toggled.connect(\n'
        '            self._apply\n'
        '        )\n'
        '        self.refresh_scenes_button.clicked.connect(\n',
        "conexão do checkbox",
    )

    text = replace_once(
        text,
        '            self._populate_scene_combo(\n'
        '                area.target_scene\n'
        '            )\n\n'
        '            self._update_target_scene_state()\n',
        '            self._populate_scene_combo(\n'
        '                area.target_scene\n'
        '            )\n\n'
        '            self.trigger_once_checkbox.setChecked(\n'
        '                area.trigger_once\n'
        '            )\n\n'
        '            self._update_target_scene_state()\n',
        "carregamento do checkbox",
    )

    text = replace_once(
        text,
        '            self.enter_action_combo,\n'
        '            self.target_scene_combo,\n'
        '            self.refresh_scenes_button,\n'
        '            self.hint_label,\n',
        '            self.enter_action_combo,\n'
        '            self.target_scene_combo,\n'
        '            self.refresh_scenes_button,\n'
        '            self.trigger_once_checkbox,\n'
        '            self.hint_label,\n',
        "visibilidade do checkbox",
    )

    text = replace_once(
        text,
        '        area.target_scene = str(\n'
        '            self.target_scene_combo.currentData()\n'
        '            or ""\n'
        '        )\n\n'
        '        self.area2d_changed.emit(\n',
        '        area.target_scene = str(\n'
        '            self.target_scene_combo.currentData()\n'
        '            or ""\n'
        '        )\n\n'
        '        area.trigger_once = (\n'
        '            self.trigger_once_checkbox.isChecked()\n'
        '        )\n\n'
        '        self.area2d_changed.emit(\n',
        "salvamento do checkbox",
    )

    EDITOR.write_text(text, encoding="utf-8")


def patch_runtime() -> None:
    backup(RUNTIME)
    text = RUNTIME.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '        self.area_events: list[\n'
        '            Area2DEvent\n'
        '        ] = []\n\n'
        '        for entity in self.scene.entities:\n',
        '        self.area_events: list[\n'
        '            Area2DEvent\n'
        '        ] = []\n\n'
        '        self.area_triggered_once: set[str] = set()\n\n'
        '        for entity in self.scene.entities:\n',
        "estado trigger_once no runtime",
    )

    text = replace_once(
        text,
        '            if (\n'
        '                inside_now\n'
        '                and not inside_before\n'
        '            ):\n'
        '                self.area_events.append(\n'
        '                    Area2DEvent(\n'
        '                        area_id=entity.id,\n'
        '                        event="entered",\n'
        '                    )\n'
        '                )\n\n'
        '            elif (\n',
        '            if (\n'
        '                inside_now\n'
        '                and not inside_before\n'
        '            ):\n'
        '                area = entity.area2d\n\n'
        '                already_triggered = (\n'
        '                    area.trigger_once\n'
        '                    and entity.id\n'
        '                    in self.area_triggered_once\n'
        '                )\n\n'
        '                if not already_triggered:\n'
        '                    self.area_events.append(\n'
        '                        Area2DEvent(\n'
        '                            area_id=entity.id,\n'
        '                            event="entered",\n'
        '                        )\n'
        '                    )\n\n'
        '                    if area.trigger_once:\n'
        '                        self.area_triggered_once.add(\n'
        '                            entity.id\n'
        '                        )\n\n'
        '            elif (\n',
        "evento entered com trigger_once",
    )

    RUNTIME.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (MODEL, EDITOR, RUNTIME):
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    patch_model()
    patch_editor()
    patch_runtime()

    print("Area2D trigger_once aplicado com sucesso.")
    print("Backups .bak_trigger_once foram criados.")


if __name__ == "__main__":
    main()
