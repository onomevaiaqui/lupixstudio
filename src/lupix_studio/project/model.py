from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class DevelopmentMode(StrEnum):
    BLUEPRINT = "blueprint"
    HYBRID = "blueprint_script"
    SCRIPT = "script"


@dataclass(slots=True)
class ProjectConfig:
    name: str
    root: Path
    development_mode: DevelopmentMode = DevelopmentMode.BLUEPRINT
    width: int = 480
    height: int = 270
    platform: str = "lupi"
    entry_point: str = "game.lua"

    def __post_init__(self) -> None:
        self.platform = (
            str(self.platform).strip().lower()
            or "lupi"
        )

        if self.platform == "lupi":
            self.width = 480
            self.height = 270

        else:
            self.width = max(
                1,
                int(self.width),
            )

            self.height = max(
                1,
                int(self.height),
            )

    @property
    def project_dir(self) -> Path:
        return self.root / self.name