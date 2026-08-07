from pathlib import Path

from lupix_studio.project.creator import create_project
from lupix_studio.project.model import DevelopmentMode, ProjectConfig


def test_create_project(tmp_path: Path) -> None:
    config = ProjectConfig(
        name="TesteLupi",
        root=tmp_path,
        development_mode=DevelopmentMode.SCRIPT,
    )

    create_project(config)

    project = tmp_path / "TesteLupi"

    assert project.exists()
    assert (project / "game.lua").exists()
    assert (project / "lupix.project").exists()
    assert (project / "assets" / "sprites").exists()
    assert (project / "assets" / "tilesets").exists()
    assert (project / "maps").exists()
    assert (project / "scripts").exists()
    assert (project / "lupix" / "blueprints").exists()