from dataclasses import dataclass
from pathlib import Path

from lupix_studio.project.loader import LoadedProject

REQUIRED_DIRECTORIES = (
    "assets",
    "assets/sprites",
    "assets/tilesets",
    "assets/audio",
    "maps",
    "scenes",
    "scripts",
    "lupix",
    "lupix/blueprints",
)


@dataclass(slots=True)
class ValidationIssue:
    level: str
    message: str


def validate_project(
    project: LoadedProject,
) -> list[ValidationIssue]:
    """Valida a estrutura mínima de um projeto Lupix."""

    issues: list[ValidationIssue] = []

    if project.platform != "lupi":
        issues.append(
            ValidationIssue(
                level="error",
                message="A plataforma principal deve ser Lupi.",
            )
        )

    if project.width != 480 or project.height != 270:
        issues.append(
            ValidationIssue(
                level="warning",
                message=(
                    "A resolução recomendada para o Lupi é 480x270."
                ),
            )
        )

    entry_point = project.root / project.entry_point

    if not entry_point.exists():
        issues.append(
            ValidationIssue(
                level="error",
                message=(
                    f"Arquivo de entrada não encontrado: "
                    f"{project.entry_point}"
                ),
            )
        )

    for directory in REQUIRED_DIRECTORIES:
        path = project.root / directory

        if not path.exists():
            issues.append(
                ValidationIssue(
                    level="error",
                    message=(
                        f"Diretório obrigatório ausente: "
                        f"{directory}"
                    ),
                )
            )

    return issues


def is_project_valid(
    project: LoadedProject,
) -> bool:
    """Retorna True quando não há erros estruturais."""

    return not any(
        issue.level == "error"
        for issue in validate_project(project)
    )


def validate_project_path(
    path: Path,
) -> bool:
    """Validação simples de existência do arquivo principal."""

    return (
        path.is_dir()
        and (path / "lupix.project").exists()
        and (path / "game.lua").exists()
    )