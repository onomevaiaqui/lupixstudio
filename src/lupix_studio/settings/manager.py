import json
from dataclasses import asdict, dataclass

from lupix_studio.core.paths import ensure_directories, settings_file


@dataclass
class StudioSettings:
    theme: str = "dark"
    language: str = "pt_BR"
    recent_projects_limit: int = 10


class SettingsManager:
    """Gerencia as configurações persistentes do Studio."""

    def load(self) -> StudioSettings:
        ensure_directories()

        path = settings_file()

        if not path.exists():
            settings = StudioSettings()
            self.save(settings)
            return settings

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return StudioSettings()

        return StudioSettings(
            theme=str(data.get("theme", "dark")),
            language=str(data.get("language", "pt_BR")),
            recent_projects_limit=int(data.get("recent_projects_limit", 10)),
        )

    def save(self, settings: StudioSettings) -> None:
        ensure_directories()

        settings_file().write_text(
            json.dumps(asdict(settings), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )