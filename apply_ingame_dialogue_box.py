import shutil
from pathlib import Path

PATH = Path(
    r".\\src\\lupix_studio\\ui\\play_preview.py"
)


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

    return text.replace(
        old,
        new,
        1,
    )


if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_dialogue_box"
)

if not backup.exists():
    shutil.copy2(
        PATH,
        backup,
    )

text = PATH.read_text(
    encoding="utf-8"
)

anchor = (
    '        self.setFocusPolicy(\n'
    '            Qt.FocusPolicy.StrongFocus\n'
    '        )\n'
)

replacement = anchor + (
    '\n'
    '        self.dialogue_label = QLabel(\n'
    '            self.viewport()\n'
    '        )\n\n'
    '        self.dialogue_label.setObjectName(\n'
    '            "PlayDialogue"\n'
    '        )\n\n'
    '        self.dialogue_label.setWordWrap(\n'
    '            True\n'
    '        )\n\n'
    '        self.dialogue_label.setAlignment(\n'
    '            Qt.AlignmentFlag.AlignLeft\n'
    '            | Qt.AlignmentFlag.AlignVCenter\n'
    '        )\n\n'
    '        self.dialogue_label.setAttribute(\n'
    '            Qt.WidgetAttribute.WA_TransparentForMouseEvents,\n'
    '            True,\n'
    '        )\n\n'
    '        self.dialogue_label.setStyleSheet(\n'
    '            "QLabel#PlayDialogue {"\n'
    '            " color: #ffffff;"\n'
    '            " background-color: rgba(8, 14, 26, 230);"\n'
    '            " border: 2px solid #d5ad38;"\n'
    '            " border-radius: 8px;"\n'
    '            " padding: 12px 16px;"\n'
    '            " font-size: 15px;"\n'
    '            " font-weight: 600;"\n'
    '            " }"\n'
    '        )\n\n'
    '        self.dialogue_label.hide()\n\n'
    '        self.dialogue_timer = QTimer(\n'
    '            self\n'
    '        )\n\n'
    '        self.dialogue_timer.setSingleShot(\n'
    '            True\n'
    '        )\n\n'
    '        self.dialogue_timer.timeout.connect(\n'
    '            self.hide_message\n'
    '        )\n'
)

text = replace_once(
    text,
    anchor,
    replacement,
    "fim do PlayCanvas.__init__",
)

anchor = (
    '    def set_runtime(\n'
    '        self,\n'
    '        project_root: Path,\n'
    '        runtime: SceneRuntime,\n'
    '    ) -> None:\n'
)

methods = (
    '    def show_message(\n'
    '        self,\n'
    '        text: str,\n'
    '        duration_ms: int = 4000,\n'
    '    ) -> None:\n'
    '        message = text.strip()\n\n'
    '        if not message:\n'
    '            return\n\n'
    '        self.dialogue_label.setText(\n'
    '            message\n'
    '        )\n\n'
    '        self._position_dialogue()\n\n'
    '        self.dialogue_label.show()\n'
    '        self.dialogue_label.raise_()\n\n'
    '        self.dialogue_timer.start(\n'
    '            max(\n'
    '                500,\n'
    '                int(duration_ms),\n'
    '            )\n'
    '        )\n\n'
    '    def hide_message(\n'
    '        self,\n'
    '    ) -> None:\n'
    '        self.dialogue_timer.stop()\n'
    '        self.dialogue_label.hide()\n\n'
    '    def _position_dialogue(\n'
    '        self,\n'
    '    ) -> None:\n'
    '        viewport = self.viewport()\n'
    '        margin = 18\n\n'
    '        width = max(\n'
    '            240,\n'
    '            min(\n'
    '                720,\n'
    '                viewport.width()\n'
    '                - margin * 2,\n'
    '            ),\n'
    '        )\n\n'
    '        self.dialogue_label.setFixedWidth(\n'
    '            width\n'
    '        )\n\n'
    '        self.dialogue_label.adjustSize()\n\n'
    '        height = max(\n'
    '            64,\n'
    '            self.dialogue_label.height(),\n'
    '        )\n\n'
    '        self.dialogue_label.setFixedHeight(\n'
    '            height\n'
    '        )\n\n'
    '        x = max(\n'
    '            margin,\n'
    '            (\n'
    '                viewport.width()\n'
    '                - width\n'
    '            ) // 2,\n'
    '        )\n\n'
    '        y = max(\n'
    '            margin,\n'
    '            viewport.height()\n'
    '            - height\n'
    '            - 24,\n'
    '        )\n\n'
    '        self.dialogue_label.move(\n'
    '            x,\n'
    '            y,\n'
    '        )\n\n'
    '    def resizeEvent(\n'
    '        self,\n'
    '        event,\n'
    '    ) -> None:\n'
    '        super().resizeEvent(\n'
    '            event\n'
    '        )\n\n'
    '        if self.dialogue_label.isVisible():\n'
    '            self._position_dialogue()\n\n'
) + anchor

text = replace_once(
    text,
    anchor,
    methods,
    "PlayCanvas.set_runtime",
)

anchor = (
    '        self.project_root = (\n'
    '            project_root.resolve()\n'
    '        )\n\n'
    '        self.runtime = runtime\n\n'
    '        self.rebuild()\n'
)

replacement = (
    '        self.hide_message()\n\n'
) + anchor

text = replace_once(
    text,
    anchor,
    replacement,
    "PlayCanvas.set_runtime body",
)

anchor = (
    '                if message_text:\n'
    '                    self.area_event.emit(\n'
    '                        f"Mensagem: {message_text}"\n'
    '                    )\n'
)

replacement = anchor + (
    '\n'
    '                    self.canvas.show_message(\n'
    '                        message_text\n'
    '                    )\n'
)

text = replace_once(
    text,
    anchor,
    replacement,
    "ação Mostrar Mensagem",
)

PATH.write_text(
    text,
    encoding="utf-8",
)

print(
    "Caixa de mensagem in-game aplicada com sucesso."
)
print(
    f"Backup: {backup}"
)
