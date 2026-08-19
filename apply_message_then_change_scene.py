import shutil
from pathlib import Path

ROOT = Path(r".\\src\\lupix_studio")
EDITOR = ROOT / "ui" / "area2d_component_editor.py"
PREVIEW = ROOT / "ui" / "play_preview.py"


def backup(path: Path) -> None:
    backup_path = path.with_suffix(
        path.suffix + ".bak_message_change_scene"
    )
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def replace_once(
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    if old not in text:
        raise RuntimeError(
            f"Não encontrei o bloco: {description}"
        )
    return text.replace(old, new, 1)


def patch_editor() -> None:
    backup(EDITOR)
    text = EDITOR.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '        self.enter_action_combo.addItem(\n'
        '            "Mostrar Mensagem",\n'
        '            "show_message",\n'
        '        )\n\n'
        '        self.target_scene_combo = QComboBox()\n',
        '        self.enter_action_combo.addItem(\n'
        '            "Mostrar Mensagem",\n'
        '            "show_message",\n'
        '        )\n'
        '        self.enter_action_combo.addItem(\n'
        '            "Mostrar Mensagem + Trocar Cena",\n'
        '            "message_change_scene",\n'
        '        )\n\n'
        '        self.target_scene_combo = QComboBox()\n',
        "nova ação combinada",
    )

    text = replace_once(
        text,
        '        scene_enabled = (\n'
        '            action == "change_scene"\n'
        '        )\n\n'
        '        message_enabled = (\n'
        '            action == "show_message"\n'
        '        )\n',
        '        scene_enabled = (\n'
        '            action in (\n'
        '                "change_scene",\n'
        '                "message_change_scene",\n'
        '            )\n'
        '        )\n\n'
        '        message_enabled = (\n'
        '            action in (\n'
        '                "show_message",\n'
        '                "message_change_scene",\n'
        '            )\n'
        '        )\n',
        "habilitação dos campos",
    )

    EDITOR.write_text(
        text,
        encoding="utf-8",
    )


def patch_preview() -> None:
    backup(PREVIEW)
    text = PREVIEW.read_text(encoding="utf-8")

    marker = (
        '            if (\n'
        '                area_event.event == "entered"\n'
        '                and area_entity is not None\n'
        '                and area_entity.area2d is not None\n'
        '                and area_entity.area2d.on_enter_action\n'
        '                == "change_scene"\n'
        '            ):\n'
    )

    if marker not in text:
        raise RuntimeError(
            "Bloco change_scene não encontrado em play_preview.py"
        )

    combined = (
        '            if (\n'
        '                area_event.event == "entered"\n'
        '                and area_entity is not None\n'
        '                and area_entity.area2d is not None\n'
        '                and area_entity.area2d.on_enter_action\n'
        '                == "message_change_scene"\n'
        '            ):\n'
        '                message_text = (\n'
        '                    area_entity.area2d.message_text.strip()\n'
        '                )\n\n'
        '                target_scene = (\n'
        '                    area_entity.area2d.target_scene.strip()\n'
        '                )\n\n'
        '                if message_text:\n'
        '                    self.area_event.emit(\n'
        '                        f"Mensagem: {message_text}"\n'
        '                    )\n\n'
        '                    self.canvas.show_message(\n'
        '                        message_text,\n'
        '                        duration_ms=3000,\n'
        '                    )\n\n'
        '                if target_scene:\n'
        '                    if self.runtime is not None:\n'
        '                        self.runtime.running = False\n\n'
        '                    QTimer.singleShot(\n'
        '                        3000,\n'
        '                        lambda scene=target_scene: (\n'
        '                            self._change_scene(scene)\n'
        '                        ),\n'
        '                    )\n\n'
        '                    return\n\n'
    )

    text = text.replace(
        marker,
        combined + marker,
        1,
    )

    PREVIEW.write_text(
        text,
        encoding="utf-8",
    )


def main() -> None:
    for path in (EDITOR, PREVIEW):
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}"
            )

    patch_editor()
    patch_preview()

    print(
        "Ação 'Mostrar Mensagem + Trocar Cena' aplicada."
    )
    print(
        "A mensagem fica 3 segundos na tela e então a cena é trocada."
    )


if __name__ == "__main__":
    main()
