from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class UITheme:
    project_root: Path | None = None
    font: str = ""
    text_color: str = "#ffffff"
    accent_color: str = "#d5ad38"
    hud_label: str = "VIDA"
    hud_font_size: int = 14
    hud_text_color: str = "#ffffff"
    hud_background_color: str = "rgba(8, 14, 26, 210)"
    hud_background_image: str = ""
    death_font_size: int = 28
    death_text_color: str = "#ffffff"
    death_background_color: str = "rgba(0, 0, 0, 235)"
    death_background_image: str = ""
    continue_prompt: str = "Continuar?"
    yes_text: str = "Sim"
    no_text: str = "Não"
    button_font_size: int = 15
    button_text_color: str = "#ffffff"
    button_background_color: str = "#252a34"
    button_selected_color: str = "#d5ad38"
    button_background_image: str = ""
    button_selected_image: str = ""

    @classmethod
    def load(cls, project_root: Path) -> UITheme:
        root = project_root.resolve()
        path = root / "ui" / "theme.json"
        theme = cls(project_root=root)
        if not path.is_file():
            return theme
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return theme
        if not isinstance(data, dict):
            return theme
        hud = data.get("hud") if isinstance(data.get("hud"), dict) else {}
        death = data.get("death_screen") if isinstance(data.get("death_screen"), dict) else {}
        buttons = data.get("buttons") if isinstance(data.get("buttons"), dict) else {}
        theme.font = str(data.get("font", "") or "")
        theme.text_color = str(data.get("text_color", theme.text_color))
        theme.accent_color = str(data.get("accent_color", theme.accent_color))
        theme.hud_label = str(hud.get("label", theme.hud_label))
        theme.hud_font_size = max(8, int(hud.get("font_size", theme.hud_font_size)))
        theme.hud_text_color = str(hud.get("text_color", theme.hud_text_color))
        theme.hud_background_color = str(hud.get("background_color", theme.hud_background_color))
        theme.hud_background_image = str(hud.get("background_image", "") or "")
        theme.death_font_size = max(8, int(death.get("font_size", theme.death_font_size)))
        theme.death_text_color = str(death.get("text_color", theme.death_text_color))
        theme.death_background_color = str(death.get("background_color", theme.death_background_color))
        theme.death_background_image = str(death.get("background_image", "") or "")
        theme.continue_prompt = str(death.get("continue_prompt", theme.continue_prompt))
        theme.yes_text = str(buttons.get("yes_text", theme.yes_text))
        theme.no_text = str(buttons.get("no_text", theme.no_text))
        theme.button_font_size = max(8, int(buttons.get("font_size", theme.button_font_size)))
        theme.button_text_color = str(buttons.get("text_color", theme.button_text_color))
        theme.button_background_color = str(buttons.get("background_color", theme.button_background_color))
        theme.button_selected_color = str(buttons.get("selected_color", theme.button_selected_color))
        theme.button_background_image = str(buttons.get("background_image", "") or "")
        theme.button_selected_image = str(buttons.get("selected_image", "") or "")
        return theme

    def asset(self, value: str) -> str:
        if not value or self.project_root is None:
            return ""
        path = Path(value)
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve().as_posix() if path.is_file() else ""
