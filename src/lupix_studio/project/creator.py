import json

from lupix_studio.project.model import ProjectConfig

PROJECT_DIRECTORIES = (
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


def create_project(config: ProjectConfig) -> None:
    """Cria a estrutura inicial de um projeto Lupix."""

    project_dir = config.project_dir

    if project_dir.exists():
        raise FileExistsError(
            f"O diretório do projeto já existe: {project_dir}"
        )

    project_dir.mkdir(parents=True)

    for directory in PROJECT_DIRECTORIES:
        (project_dir / directory).mkdir(parents=True, exist_ok=True)

    project_data = {
        "format": 1,
        "name": config.name,
        "platform": "lupi",
        "development_mode": config.development_mode.value,
        "resolution": {
            "width": config.width,
            "height": config.height,
        },
        "entry_point": "game.lua",
    }

    (project_dir / "lupix.project").write_text(
        json.dumps(project_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    game_lua = """-- Gerado pelo Lupix Studio

function update(frame)
end
"""

    (project_dir / "game.lua").write_text(
        game_lua,
        encoding="utf-8",
    )