from pathlib import Path

from lupix_studio.project.creator import create_project
from lupix_studio.project.loader import load_project
from lupix_studio.project.model import (
    DevelopmentMode,
    ProjectConfig,
)


def test_load_project(tmp_path: Path) -> None:
    config = ProjectConfig(
        name="MeuJogo",
        root=tmp_path,
        development_mode=DevelopmentMode.BLUEPRINT,
    )

    create_project(config)

    project = load_project(
        tmp_path / "MeuJogo"
    )

    assert project.name == "MeuJogo"
    assert project.platform == "lupi"
    assert project.width == 480
    assert project.height == 270
    assert project.entry_point == "game.lua"