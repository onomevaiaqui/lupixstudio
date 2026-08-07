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

    @property
    def project_dir(self) -> Path:
        return self.root / self.name