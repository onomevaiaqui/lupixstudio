import shutil
from pathlib import Path

ROOT = Path(r".\src\lupix_studio")
MODEL = ROOT / "scene" / "model.py"
EDITOR = ROOT / "ui" / "area2d_component_editor.py"
PREVIEW = ROOT / "ui" / "play_preview.py"


def backup(path: Path) -> None:
    backup_path = path.with_suffix(path.suffix + ".bak_show_message")
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
        '    on_enter_action: str = "none"\n'
        '    target_scene: str = ""\n'
        '    trigger_once: bool = False\n',
        '    on_enter_action: str = "none"\n'
        '    target_scene: str = ""\n'
        '    message_text: str = ""\n'
        '    trigger_once: bool = False\n',
        "campos Area2DComponent",
    )

    text = replace_once(
        text,
        '                "action": self.on_enter_action,\n'
        '                "target_scene": self.target_scene,\n'
        '                "trigger_once": self.trigger_once,\n',
        '                "action": self.on_enter_action,\n'
        '                "target_scene": self.target_scene,\n'
        '                "message_text": self.message_text,\n'
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
        '            ),\n'
        '            trigger_once=bool(\n',
        '            target_scene=str(\n'
        '                on_enter.get(\n'
        '                    "target_scene",\n'
        '                    "",\n'
        '                )\n'
        '                or ""\n'
        '            ),\n'
        '            message_text=str(\n'
        '                on_enter.get(\n'
        '                    "message_text",\n'
        '                    "",\n'
        '                )\n'
        '                or ""\n'
        '            ),\n'
        '            trigger_once=bool(\n',
        "desserialização message_text",
    )

    MODEL.write_text(text, encoding="utf-8")


def patch_editor() -> None:
    backup(EDITOR)
    text = EDITOR.read_text(encoding="utf-8")

    if "    QLineEdit,\n" not in text:
        text = replace_once(
            text,
            '    QLabel,\n'
            '    QPushButton,\n',
            '    QLabel,\n'
            '    QLineEdit,\n'
            '    QPushButton,\n',
            "import QLineEdit",
        )

    text = replace_once(
        text,
        '        self.enter_action_combo.addItem(\n'
        '            "Trocar Cena",\n'
        '            "change_scene",\n'
        '        )\n\n'
        '        self.target_scene_combo = QComboBox()\n',
        '        self.enter_action_combo.addItem(\n'
        '            "Trocar Cena",\n'
        '            "change_scene",\n'
        '        )\n'
        '        self.enter_action_combo.addItem(\n'
        '            "Mostrar Mensagem",\n'
        '            "show_message",\n'
        '        )\n\n'
        '        self.target_scene_combo = QComboBox()\n',
        "ação Mostrar Mensagem",
    )

    text = replace_once(
        text,
        '        self.target_scene_combo = QComboBox()\n'
        '        self.target_scene_combo.setMinimumWidth(180)\n',
        '        self.target_scene_combo = QComboBox()\n'
        '        self.target_scene_combo.setMinimumWidth(180)\n\n'
        '        self.message_edit = QLineEdit()\n'
        '        self.message_edit.setPlaceholderText(\n'
        '            "Mensagem exibida ao entrar na área"\n'
        '        )\n',
        "campo message_edit",
    )

    text = replace_once(
        text,
        '        event_form.addRow(\n'
        '            "Cena destino:",\n'
        '            selector_widget,\n'
        '        )\n',
        '        event_form.addRow(\n'
        '            "Cena destino:",\n'
        '            selector_widget,\n'
        '        )\n'
        '        event_form.addRow(\n'
        '            "Mensagem:",\n'
        '            self.message_edit,\n'
        '        )\n',
        "linha Mensagem",
    )

    text = replace_once(
        text,
        '        self.target_scene_combo.currentIndexChanged.connect(\n'
        '            self._apply\n'
        '        )\n'
        '        self.trigger_once_checkbox.toggled.connect(\n',
        '        self.target_scene_combo.currentIndexChanged.connect(\n'
        '            self._apply\n'
        '        )\n'
        '        self.message_edit.textChanged.connect(\n'
        '            self._apply\n'
        '        )\n'
        '        self.trigger_once_checkbox.toggled.connect(\n',
        "conexão message_edit",
    )

    text = replace_once(
        text,
        '            self.trigger_once_checkbox.setChecked(\n'
        '                area.trigger_once\n'
        '            )\n\n'
        '            self._update_target_scene_state()\n',
        '            self.trigger_once_checkbox.setChecked(\n'
        '                area.trigger_once\n'
        '            )\n\n'
        '            self.message_edit.setText(\n'
        '                area.message_text\n'
        '            )\n\n'
        '            self._update_target_scene_state()\n',
        "carregamento message_text",
    )

    text = replace_once(
        text,
        '            self.refresh_scenes_button,\n'
        '            self.trigger_once_checkbox,\n'
        '            self.hint_label,\n',
        '            self.refresh_scenes_button,\n'
        '            self.message_edit,\n'
        '            self.trigger_once_checkbox,\n'
        '            self.hint_label,\n',
        "visibilidade message_edit",
    )

    old_state = '''    def _update_target_scene_state(
        self,
    ) -> None:
        enabled = (
            self.enter_action_combo.currentData()
            == "change_scene"
        )

        self.target_scene_combo.setEnabled(
            enabled
        )
        self.refresh_scenes_button.setEnabled(
            enabled
        )
'''

    new_state = '''    def _update_target_scene_state(
        self,
    ) -> None:
        action = str(
            self.enter_action_combo.currentData()
            or "none"
        )

        scene_enabled = (
            action == "change_scene"
        )

        message_enabled = (
            action == "show_message"
        )

        self.target_scene_combo.setEnabled(
            scene_enabled
        )

        self.refresh_scenes_button.setEnabled(
            scene_enabled
        )

        self.message_edit.setEnabled(
            message_enabled
        )
'''

    text = replace_once(
        text,
        old_state,
        new_state,
        "estado dos campos de ação",
    )

    text = replace_once(
        text,
        '        area.trigger_once = (\n'
        '            self.trigger_once_checkbox.isChecked()\n'
        '        )\n\n'
        '        self.area2d_changed.emit(\n',
        '        area.message_text = (\n'
        '            self.message_edit.text().strip()\n'
        '        )\n\n'
        '        area.trigger_once = (\n'
        '            self.trigger_once_checkbox.isChecked()\n'
        '        )\n\n'
        '        self.area2d_changed.emit(\n',
        "salvamento message_text",
    )

    EDITOR.write_text(text, encoding="utf-8")


def patch_preview() -> None:
    backup(PREVIEW)
    text = PREVIEW.read_text(encoding="utf-8")

    marker = '''            if (
                area_event.event == "entered"
                and area_entity is not None
                and area_entity.area2d is not None
                and area_entity.area2d.on_enter_action
                == "change_scene"
            ):
'''

    if marker not in text:
        raise RuntimeError(
            "Não encontrei o bloco change_scene em play_preview.py"
        )

    show_message = '''            if (
                area_event.event == "entered"
                and area_entity is not None
                and area_entity.area2d is not None
                and area_entity.area2d.on_enter_action
                == "show_message"
            ):
                message_text = (
                    area_entity.area2d.message_text.strip()
                )

                if message_text:
                    self.area_event.emit(
                        f"Mensagem: {message_text}"
                    )

'''

    text = text.replace(
        marker,
        show_message + marker,
        1,
    )

    PREVIEW.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (MODEL, EDITOR, PREVIEW):
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    patch_model()
    patch_editor()
    patch_preview()

    print("Ação 'Mostrar Mensagem' aplicada com sucesso.")
    print("Backups .bak_show_message foram criados.")


if __name__ == "__main__":
    main()
