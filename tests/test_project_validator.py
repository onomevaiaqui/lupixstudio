from pathlib import Path

from lupix_studio.project.creator import create_project
from lupix_studio.project.loader import load_project
from lupix_studio.project.model import (
    DevelopmentMode,
    ProjectConfig,
)
from lupix_studio.project.validator import (
    is_project_valid,
    validate_project,
)


def test_new_project_is_valid(
    tmp_path: Path,
) -> None:
    config = ProjectConfig(
        name="ProjetoValido",
        root=tmp_path,
        development_mode=DevelopmentMode.SCRIPT,
    )

    create_project(config)

    project = load_project(
        tmp_path / "ProjetoValido"
    )

    issues = validate_project(project)

    assert issues == []
    assert is_project_valid(project)


def test_missing_game_lua_is_invalid(
    tmp_path: Path,
) -> None:
    config = ProjectConfig(
        name="ProjetoInvalido",
        root=tmp_path,
    )

    create_project(config)

    project_dir = tmp_path / "ProjetoInvalido"

    (project_dir / "game.lua").unlink()

    project = load_project(project_dir)

    issues = validate_project(project)

    assert not is_project_valid(project)

    assert any(
        "Arquivo de entrada não encontrado"
        in issue.message
        for issue in issues
    )