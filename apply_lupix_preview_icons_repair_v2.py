import shutil
from pathlib import Path

ROOT = Path(r".\src\lupix_studio")
EDITOR = ROOT / "ui" / "area2d_component_editor.py"
PREVIEW = ROOT / "ui" / "play_preview.py"


def backup(path: Path, suffix: str) -> None:
    target = path.with_suffix(path.suffix + suffix)
    if not target.exists():
        shutil.copy2(path, target)


def replace_once(
    text: str,
    old: str,
    new: str,
    label: str,
) -> str:
    if old not in text:
        raise RuntimeError(
            f"Bloco não encontrado: {label}"
        )
    return text.replace(old, new, 1)


# ==========================================================
# 1. AREA2D EDITOR — ícones reais e campo de mensagem estável
# ==========================================================

if not EDITOR.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {EDITOR}"
    )

backup(
    EDITOR,
    ".bak_preview_icons_v2",
)

text = EDITOR.read_text(
    encoding="utf-8",
)

# Imports necessários.
if "    QStyle,\n" not in text:
    text = replace_once(
        text,
        "    QScrollArea,\n",
        "    QScrollArea,\n"
        "    QStyle,\n"
        "    QToolButton,\n",
        "imports QStyle/QToolButton",
    )

# Se veio do reparo anterior com botões em texto.
text = text.replace(
    '        up_button = QPushButton("Subir")\n'
    '        down_button = QPushButton("Descer")\n'
    '        remove_button = QPushButton("Remover")\n',
    '        up_button = QToolButton()\n'
    '        down_button = QToolButton()\n'
    '        remove_button = QToolButton()\n'
)

# Se ainda estiver na versão original com símbolos.
text = text.replace(
    '        up_button = QPushButton("↑")\n'
    '        down_button = QPushButton("↓")\n'
    '        remove_button = QPushButton("×")\n',
    '        up_button = QToolButton()\n'
    '        down_button = QToolButton()\n'
    '        remove_button = QToolButton()\n'
)

# Substitui largura textual por configuração de ícones.
for old_block in (
    """        up_button.setFixedWidth(52)
        down_button.setFixedWidth(60)
        remove_button.setFixedWidth(68)
""",
    """        for button in (
            up_button,
            down_button,
            remove_button,
        ):
            button.setFixedWidth(30)
""",
):
    if old_block in text:
        text = text.replace(
            old_block,
            """        up_button.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_ArrowUp
            )
        )
        down_button.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_ArrowDown
            )
        )
        remove_button.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_TrashIcon
            )
        )

        up_button.setToolTip("Mover ação para cima")
        down_button.setToolTip("Mover ação para baixo")
        remove_button.setToolTip("Excluir ação")

        for button in (
            up_button,
            down_button,
            remove_button,
        ):
            button.setFixedSize(
                34,
                30,
            )
""",
            1,
        )
        break

# Caso ainda não exista configuração de ícones.
if "SP_ArrowUp" not in text:
    anchor = (
        '        remove_button = QToolButton()\n'
    )
    text = replace_once(
        text,
        anchor,
        anchor
        + """
        up_button.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_ArrowUp
            )
        )
        down_button.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_ArrowDown
            )
        )
        remove_button.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_TrashIcon
            )
        )

        up_button.setToolTip("Mover ação para cima")
        down_button.setToolTip("Mover ação para baixo")
        remove_button.setToolTip("Excluir ação")

        for button in (
            up_button,
            down_button,
            remove_button,
        ):
            button.setFixedSize(
                34,
                30,
            )
""",
        "configuração dos ícones",
    )

# Campo de mensagem só salva quando termina a edição,
# evitando reconstrução do Inspector a cada caractere.
text = text.replace(
    """        message_edit.textChanged.connect(
            save_row
        )
""",
    """        message_edit.editingFinished.connect(
            save_row
        )
"""
)

EDITOR.write_text(
    text,
    encoding="utf-8",
)


# ==========================================================
# 2. PLAY PREVIEW — restaura execução e sequência de ações
# ==========================================================

if not PREVIEW.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PREVIEW}"
    )

backup(
    PREVIEW,
    ".bak_preview_icons_v2",
)

text = PREVIEW.read_text(
    encoding="utf-8",
)

play_class = text.find(
    "class PlayPreview(QWidget):"
)

if play_class < 0:
    raise RuntimeError(
        "class PlayPreview(QWidget) não encontrada."
    )

before_play = text[:play_class]
play_text = text[play_class:]

# Remove eventual active_area_sequences colocado por engano
# antes da classe PlayPreview (por exemplo, dentro de PlayCanvas).
before_play = before_play.replace(
    "\n        self.active_area_sequences: set[str] = set()\n",
    "\n",
)

# Garante atributo no __init__ da classe correta.
runtime_decl = (
    "        self.project_root: Path | None = None\n"
    "        self.runtime: SceneRuntime | None = None\n"
)

if runtime_decl not in play_text:
    raise RuntimeError(
        "Atributos project_root/runtime não encontrados "
        "no PlayPreview.__init__."
    )

init_zone = play_text.split(
    "    def start(",
    1,
)[0]

if "self.active_area_sequences" not in init_zone:
    play_text = play_text.replace(
        runtime_decl,
        runtime_decl
        + "\n"
        + "        self.active_area_sequences: set[str] = set()\n",
        1,
    )

# Limpa sequências sempre que um novo preview/cena começa.
start_marker = "    def start(\n"
start_pos = play_text.find(start_marker)

if start_pos < 0:
    raise RuntimeError(
        "PlayPreview.start não encontrado."
    )

next_def = play_text.find(
    "\n    def ",
    start_pos + len(start_marker),
)

if next_def < 0:
    next_def = len(play_text)

start_block = play_text[
    start_pos:next_def
]

if "self.active_area_sequences.clear()" not in start_block:
    project_root_assign = (
        "        self.project_root = (\n"
        "            project_root.resolve()\n"
        "        )\n"
    )

    if project_root_assign not in start_block:
        raise RuntimeError(
            "Atribuição project_root não encontrada em start()."
        )

    start_block = start_block.replace(
        project_root_assign,
        "        self.active_area_sequences.clear()\n\n"
        + project_root_assign,
        1,
    )

    play_text = (
        play_text[:start_pos]
        + start_block
        + play_text[next_def:]
    )

# Substitui o runtime por uma versão íntegra e compatível.
update_start = play_text.find(
    "    def _update_runtime(self) -> None:\n"
)

change_start = play_text.find(
    "    def _change_scene(\n",
    update_start,
)

if update_start < 0 or change_start < 0:
    raise RuntimeError(
        "Não foi possível localizar _update_runtime/_change_scene."
    )

runtime_block = """    def _update_runtime(self) -> None:
        if self.runtime is None:
            return

        self.runtime.update(
            1.0 / 60.0
        )

        for area_event in (
            self.runtime.consume_area_events()
        ):
            area_entity = (
                self.runtime.scene.entity(
                    area_event.area_id
                )
            )

            area_name = (
                area_entity.name
                if area_entity is not None
                else area_event.area_id
            )

            if area_event.event == "entered":
                message = (
                    f"Area2D entered: {area_name}"
                )
            elif area_event.event == "exited":
                message = (
                    f"Area2D exited: {area_name}"
                )
            else:
                message = (
                    f"Area2D {area_event.event}: "
                    f"{area_name}"
                )

            self.area_event.emit(
                message
            )

            if (
                area_event.event != "entered"
                or area_entity is None
                or area_entity.area2d is None
            ):
                continue

            actions = list(
                area_entity.area2d.on_enter_actions
            )

            if actions:
                area_id = area_entity.id

                if (
                    area_id
                    in self.active_area_sequences
                ):
                    continue

                self.active_area_sequences.add(
                    area_id
                )

                self._run_area_actions(
                    area_id,
                    actions,
                    0,
                )
                continue

            # Compatibilidade com cenas antigas.
            legacy_action = (
                area_entity.area2d.on_enter_action
            )

            if legacy_action == "show_message":
                message_text = (
                    area_entity.area2d.message_text.strip()
                )

                if message_text:
                    self.area_event.emit(
                        f"Mensagem: {message_text}"
                    )
                    self.canvas.show_message(
                        message_text
                    )

            elif legacy_action == "change_scene":
                target_scene = (
                    area_entity.area2d.target_scene.strip()
                )

                if (
                    target_scene
                    and self._change_scene(
                        target_scene
                    )
                ):
                    return

            elif (
                legacy_action
                == "message_change_scene"
            ):
                message_text = (
                    area_entity.area2d.message_text.strip()
                )
                target_scene = (
                    area_entity.area2d.target_scene.strip()
                )

                if message_text:
                    self.area_event.emit(
                        f"Mensagem: {message_text}"
                    )
                    self.canvas.show_message(
                        message_text,
                        duration_ms=3000,
                    )

                if target_scene:
                    QTimer.singleShot(
                        3000,
                        lambda scene=target_scene: (
                            self._change_scene(
                                scene
                            )
                        ),
                    )
                    return

        self.canvas.refresh()

    def _finish_area_sequence(
        self,
        area_id: str,
    ) -> None:
        self.active_area_sequences.discard(
            area_id
        )

    def _run_area_actions(
        self,
        area_id: str,
        actions: list[object],
        index: int = 0,
    ) -> None:
        if index >= len(actions):
            self._finish_area_sequence(
                area_id
            )
            return

        action = actions[index]

        action_type = str(
            getattr(
                action,
                "action",
                "none",
            )
            or "none"
        )

        if action_type == "show_message":
            message_text = str(
                getattr(
                    action,
                    "message_text",
                    "",
                )
                or ""
            ).strip()

            if message_text:
                self.area_event.emit(
                    f"Mensagem: {message_text}"
                )

                self.canvas.show_message(
                    message_text
                )

            self._run_area_actions(
                area_id,
                actions,
                index + 1,
            )
            return

        if action_type == "wait":
            wait_seconds = max(
                0.0,
                float(
                    getattr(
                        action,
                        "wait_seconds",
                        0.0,
                    )
                    or 0.0
                ),
            )

            QTimer.singleShot(
                int(
                    wait_seconds
                    * 1000
                ),
                lambda: self._run_area_actions(
                    area_id,
                    actions,
                    index + 1,
                ),
            )
            return

        if action_type == "change_scene":
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

        self._run_area_actions(
            area_id,
            actions,
            index + 1,
        )

"""

play_text = (
    play_text[:update_start]
    + runtime_block
    + play_text[change_start:]
)

text = before_play + play_text

PREVIEW.write_text(
    text,
    encoding="utf-8",
)

print()
print("Reparo V2 aplicado.")
print()
print("Area2D:")
print("- setas são ícones reais do Qt;")
print("- excluir ação usa ícone de lixeira do Qt;")
print("- mensagem não perde foco a cada caractere.")
print()
print("Preview:")
print("- active_area_sequences está no PlayPreview;")
print("- _update_runtime foi reconstruído;")
print("- sequência Mostrar mensagem/Aguardar/Trocar cena restaurada;")
print("- fallback para cenas antigas mantido.")
print()
print("O layout principal não foi alterado:")
print("- Hierarquia continua à esquerda;")
print("- Inspector continua à direita.")
