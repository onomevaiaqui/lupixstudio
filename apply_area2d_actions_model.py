import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\scene\model.py")

if not PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PATH}"
    )

backup = PATH.with_suffix(
    PATH.suffix + ".bak_area2d_actions"
)

if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(
    encoding="utf-8"
)

start_marker = (
    "@dataclass(slots=True)\n"
    "class Area2DComponent:\n"
)

end_marker = (
    "\n\n@dataclass(slots=True)\n"
    "class ColliderComponent:"
)

start = text.find(start_marker)
end = text.find(end_marker, start)

if start < 0:
    raise RuntimeError(
        "Area2DComponent não encontrado em model.py."
    )

if end < 0:
    raise RuntimeError(
        "ColliderComponent não encontrado após Area2DComponent."
    )

replacement = '@dataclass(slots=True)\nclass Area2DAction:\n    """Uma ação executada por um evento de Area2D."""\n\n    action: str = "none"\n    message_text: str = ""\n    target_scene: str = ""\n    wait_seconds: float = 0.0\n\n    def to_dict(self) -> dict[str, object]:\n        return {\n            "action": self.action,\n            "message_text": self.message_text,\n            "target_scene": self.target_scene,\n            "wait_seconds": self.wait_seconds,\n        }\n\n    @classmethod\n    def from_dict(\n        cls,\n        data: dict[str, object],\n    ) -> Area2DAction:\n        return cls(\n            action=str(\n                data.get("action", "none")\n                or "none"\n            ),\n            message_text=str(\n                data.get("message_text", "")\n                or ""\n            ),\n            target_scene=str(\n                data.get("target_scene", "")\n                or ""\n            ),\n            wait_seconds=max(\n                0.0,\n                float(\n                    data.get(\n                        "wait_seconds",\n                        0.0,\n                    )\n                    or 0.0\n                ),\n            ),\n        )\n\n\n@dataclass(slots=True)\nclass Area2DComponent:\n    """Área de detecção 2D sem colisão física."""\n\n    enabled: bool = True\n    width: float = 64.0\n    height: float = 64.0\n    offset_x: float = 0.0\n    offset_y: float = 0.0\n    detect_player: bool = True\n    debug_visible: bool = True\n\n    on_enter_actions: list[Area2DAction] = field(\n        default_factory=list\n    )\n\n    trigger_once: bool = False\n\n    # Compatibilidade temporária com o sistema antigo.\n    on_enter_action: str = "none"\n    target_scene: str = ""\n    message_text: str = ""\n\n    def to_dict(self) -> dict[str, object]:\n        return {\n            "enabled": self.enabled,\n            "width": self.width,\n            "height": self.height,\n            "offset": {\n                "x": self.offset_x,\n                "y": self.offset_y,\n            },\n            "detect_player": self.detect_player,\n            "debug_visible": self.debug_visible,\n            "on_enter": {\n                "actions": [\n                    action.to_dict()\n                    for action\n                    in self.on_enter_actions\n                ],\n                "trigger_once": self.trigger_once,\n\n                # Formato legado mantido nesta etapa.\n                "action": self.on_enter_action,\n                "target_scene": self.target_scene,\n                "message_text": self.message_text,\n            },\n        }\n\n    @classmethod\n    def from_dict(\n        cls,\n        data: dict[str, object],\n    ) -> Area2DComponent:\n        offset = data.get(\n            "offset",\n            {},\n        )\n\n        if not isinstance(offset, dict):\n            offset = {}\n\n        on_enter = data.get(\n            "on_enter",\n            {},\n        )\n\n        if not isinstance(on_enter, dict):\n            on_enter = {}\n\n        legacy_action = str(\n            on_enter.get(\n                "action",\n                "none",\n            )\n            or "none"\n        )\n\n        legacy_target_scene = str(\n            on_enter.get(\n                "target_scene",\n                "",\n            )\n            or ""\n        )\n\n        legacy_message_text = str(\n            on_enter.get(\n                "message_text",\n                "",\n            )\n            or ""\n        )\n\n        actions_data = on_enter.get(\n            "actions",\n            [],\n        )\n\n        actions: list[Area2DAction] = []\n\n        if isinstance(actions_data, list):\n            for item in actions_data:\n                if not isinstance(item, dict):\n                    continue\n\n                action = Area2DAction.from_dict(\n                    item\n                )\n\n                if action.action != "none":\n                    actions.append(action)\n\n        # Migração automática das cenas antigas.\n        if not actions:\n            if legacy_action == "change_scene":\n                actions.append(\n                    Area2DAction(\n                        action="change_scene",\n                        target_scene=legacy_target_scene,\n                    )\n                )\n\n            elif legacy_action == "show_message":\n                actions.append(\n                    Area2DAction(\n                        action="show_message",\n                        message_text=legacy_message_text,\n                    )\n                )\n\n            elif (\n                legacy_action\n                == "message_change_scene"\n            ):\n                actions.extend(\n                    [\n                        Area2DAction(\n                            action="show_message",\n                            message_text=legacy_message_text,\n                        ),\n                        Area2DAction(\n                            action="wait",\n                            wait_seconds=3.0,\n                        ),\n                        Area2DAction(\n                            action="change_scene",\n                            target_scene=legacy_target_scene,\n                        ),\n                    ]\n                )\n\n        return cls(\n            enabled=bool(\n                data.get("enabled", True)\n            ),\n            width=max(\n                0.0,\n                float(\n                    data.get(\n                        "width",\n                        64.0,\n                    )\n                ),\n            ),\n            height=max(\n                0.0,\n                float(\n                    data.get(\n                        "height",\n                        64.0,\n                    )\n                ),\n            ),\n            offset_x=float(\n                offset.get("x", 0.0)\n            ),\n            offset_y=float(\n                offset.get("y", 0.0)\n            ),\n            detect_player=bool(\n                data.get(\n                    "detect_player",\n                    True,\n                )\n            ),\n            debug_visible=bool(\n                data.get(\n                    "debug_visible",\n                    True,\n                )\n            ),\n            on_enter_actions=actions,\n            trigger_once=bool(\n                on_enter.get(\n                    "trigger_once",\n                    False,\n                )\n            ),\n            on_enter_action=legacy_action,\n            target_scene=legacy_target_scene,\n            message_text=legacy_message_text,\n        )\n'

text = (
    text[:start]
    + replacement
    + text[end:]
)

PATH.write_text(
    text,
    encoding="utf-8",
)

print("Modelo Area2D migrado para lista de ações.")
print("Classe adicionada: Area2DAction")
print("Campo adicionado: on_enter_actions")
print("Cenas antigas continuam compatíveis.")
print(f"Backup: {backup}")
