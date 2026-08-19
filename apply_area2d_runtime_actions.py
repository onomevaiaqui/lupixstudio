import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\ui\play_preview.py")

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_actions_runtime"
)

if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(encoding="utf-8")

start_marker = (
    "    def _update_runtime(self) -> None:\n"
)
end_marker = (
    "    def _change_scene(\n"
)

start = text.find(start_marker)
end = text.find(end_marker, start)

if start < 0:
    raise RuntimeError(
        "_update_runtime não encontrado."
    )

if end < 0:
    raise RuntimeError(
        "_change_scene não encontrado após _update_runtime."
    )

replacement = '    def _update_runtime(self) -> None:\n        if self.runtime is None:\n            return\n\n        self.runtime.update(\n            1.0 / 60.0\n        )\n\n        for area_event in (\n            self.runtime.consume_area_events()\n        ):\n            area_entity = (\n                self.runtime.scene.entity(\n                    area_event.area_id\n                )\n            )\n\n            area_name = (\n                area_entity.name\n                if area_entity is not None\n                else area_event.area_id\n            )\n\n            if area_event.event == "entered":\n                message = (\n                    f"Area2D entered: {area_name}"\n                )\n            elif area_event.event == "exited":\n                message = (\n                    f"Area2D exited: {area_name}"\n                )\n            else:\n                message = (\n                    f"Area2D {area_event.event}: "\n                    f"{area_name}"\n                )\n\n            self.area_event.emit(message)\n\n            if (\n                area_event.event != "entered"\n                or area_entity is None\n                or area_entity.area2d is None\n            ):\n                continue\n\n            actions = list(\n                area_entity.area2d.on_enter_actions\n            )\n\n            if actions:\n                self._run_area_actions(\n                    actions,\n                    0,\n                )\n                continue\n\n            legacy_action = (\n                area_entity.area2d.on_enter_action\n            )\n\n            if legacy_action == "show_message":\n                message_text = (\n                    area_entity.area2d.message_text.strip()\n                )\n\n                if message_text:\n                    self.area_event.emit(\n                        f"Mensagem: {message_text}"\n                    )\n                    self.canvas.show_message(\n                        message_text\n                    )\n\n            elif legacy_action == "change_scene":\n                target_scene = (\n                    area_entity.area2d.target_scene.strip()\n                )\n\n                if (\n                    target_scene\n                    and self._change_scene(\n                        target_scene\n                    )\n                ):\n                    return\n\n            elif (\n                legacy_action\n                == "message_change_scene"\n            ):\n                message_text = (\n                    area_entity.area2d.message_text.strip()\n                )\n                target_scene = (\n                    area_entity.area2d.target_scene.strip()\n                )\n\n                if message_text:\n                    self.area_event.emit(\n                        f"Mensagem: {message_text}"\n                    )\n                    self.canvas.show_message(\n                        message_text,\n                        duration_ms=3000,\n                    )\n\n                if target_scene:\n                    QTimer.singleShot(\n                        3000,\n                        lambda scene=target_scene: (\n                            self._change_scene(scene)\n                        ),\n                    )\n                    return\n\n        self.canvas.refresh()\n\n    def _run_area_actions(\n        self,\n        actions: list[object],\n        index: int = 0,\n    ) -> None:\n        if index >= len(actions):\n            return\n\n        action = actions[index]\n\n        action_type = str(\n            getattr(\n                action,\n                "action",\n                "none",\n            )\n            or "none"\n        )\n\n        if action_type == "show_message":\n            message_text = str(\n                getattr(\n                    action,\n                    "message_text",\n                    "",\n                )\n                or ""\n            ).strip()\n\n            if message_text:\n                self.area_event.emit(\n                    f"Mensagem: {message_text}"\n                )\n                self.canvas.show_message(\n                    message_text\n                )\n\n            self._run_area_actions(\n                actions,\n                index + 1,\n            )\n            return\n\n        if action_type == "wait":\n            wait_seconds = max(\n                0.0,\n                float(\n                    getattr(\n                        action,\n                        "wait_seconds",\n                        0.0,\n                    )\n                    or 0.0\n                ),\n            )\n\n            QTimer.singleShot(\n                int(wait_seconds * 1000),\n                lambda: self._run_area_actions(\n                    actions,\n                    index + 1,\n                ),\n            )\n            return\n\n        if action_type == "change_scene":\n            target_scene = str(\n                getattr(\n                    action,\n                    "target_scene",\n                    "",\n                )\n                or ""\n            ).strip()\n\n            if target_scene:\n                self._change_scene(\n                    target_scene\n                )\n\n            return\n\n        self._run_area_actions(\n            actions,\n            index + 1,\n        )\n\n'

text = (
    text[:start]
    + replacement
    + text[end:]
)

PATH.write_text(
    text,
    encoding="utf-8",
)

print("Runtime de ações Area2D atualizado.")
print("Sequência suportada:")
print("  Mostrar mensagem")
print("  Aguardar")
print("  Trocar cena")
print("Fallback legado mantido.")
print(f"Backup: {backup}")
