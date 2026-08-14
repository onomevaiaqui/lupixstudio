import json
from dataclasses import dataclass
from pathlib import Path

PROJECT_FILENAME = "lupix.project"


@dataclass(slots=True)
class LoadedProject:
    name: str
    root: Path
    platform: str
    development_mode: str
    width: int
    height: int
    entry_point: str

    @property
    def project_file(self) -> Path:
        return self.root / PROJECT_FILENAME


def find_project_file(path: Path) -> Path:
    """Localiza o lupix.project a partir de um arquivo ou diretório."""
    path = path.resolve()

    if path.is_file():
        if path.name != PROJECT_FILENAME:
            raise ValueError("O arquivo selecionado não é um projeto Lupix.")
        return path

    project_file = path / PROJECT_FILENAME

    if not project_file.exists():
        raise FileNotFoundError(
            f"Não foi encontrado {PROJECT_FILENAME} em {path}"
        )

    return project_file


def load_project(path: Path) -> LoadedProject:
    """Carrega e valida um projeto Lupix."""
    project_file = find_project_file(path)

    try:
        data = json.loads(project_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("O arquivo lupix.project é inválido.") from error

    name = str(data.get("name", "")).strip()

    if not name:
        raise ValueError("O projeto não possui um nome válido.")

    platform = str(
        data.get(
            "platform",
            "lupi",
        )
    ).strip().lower()

    if platform not in {
        "lupi",
        "pc",
    }:
        platform = "lupi"

    resolution = data.get(
        "resolution",
        {},
    )

    if not isinstance(
        resolution,
        dict,
    ):
        raise TypeError(
            "A resolução do projeto é inválida."
        )

    width = max(
        1,
        int(
            resolution.get(
                "width",
                480,
            )
        ),
    )

    height = max(
        1,
        int(
            resolution.get(
                "height",
                270,
            )
        ),
    )

    if platform == "lupi":
        width = 480
        height = 270

    return LoadedProject(
        name=name,
        root=project_file.parent,
        platform=platform,
        development_mode=str(
            data.get("development_mode", "blueprint")
        ),
        width=width,
        height=height,
        entry_point=str(data.get("entry_point", "game.lua")),
    )