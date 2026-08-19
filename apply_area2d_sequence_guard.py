import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\ui\play_preview.py")

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_sequence_guard"
)

if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(encoding="utf-8")


def replace_once(
    source: str,
    old: str,
    new: str,
    label: str,
) -> str:
    if old not in source:
        raise RuntimeError(
            f"Bloco não encontrado: {label}"
        )

    return source.replace(
        old,
        new,
        1,
    )


old = """        self.project_root: Path | None = None
        self.runtime: SceneRuntime | None = None
"""

new = """        self.project_root: Path | None = None
        self.runtime: SceneRuntime | None = None

        self.active_area_sequences: set[str] = set()
"""

text = replace_once(
    text,
    old,
    new,
    "atributos do PlayPreview",
)


old = """        self.project_root = (
            project_root.resolve()
        )

        self.runtime = SceneRuntime(
"""

new = """        self.active_area_sequences.clear()

        self.project_root = (
            project_root.resolve()
        )

        self.runtime = SceneRuntime(
"""

text = replace_once(
    text,
    old,
    new,
    "início do runtime",
)


old = """            if actions:
                self._run_area_actions(
                    actions,
                    0,
                )
                continue
"""

new = """            if actions:
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
"""

text = replace_once(
    text,
    old,
    new,
    "início da sequência Area2D",
)


start_marker = "    def _run_area_actions(\n"
end_marker = "    def _change_scene(\n"

start = text.find(start_marker)
end = text.find(end_marker, start)

if start < 0:
    raise RuntimeError(
        "_run_area_actions não encontrado."
    )

if end < 0:
    raise RuntimeError(
        "_change_scene não encontrado após _run_area_actions."
    )

replacement = """    def _finish_area_sequence(
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

text = (
    text[:start]
    + replacement
    + text[end:]
)

PATH.write_text(
    text,
    encoding="utf-8",
)

print("Proteção de sequência Area2D aplicada.")
print(f"Backup: {backup}")
