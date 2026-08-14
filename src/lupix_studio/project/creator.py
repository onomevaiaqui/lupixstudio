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
        (project_dir / directory).mkdir(
            parents=True,
            exist_ok=True,
        )

    project_data = {
        "format": 2,
        "name": config.name,
        "platform": config.platform,
        "development_mode": config.development_mode.value,
        "resolution": {
            "width": config.width,
            "height": config.height,
        },
        "entry_point": config.entry_point,
    }

    (project_dir / "lupix.project").write_text(
        json.dumps(
            project_data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    platform_name = (
        "Lupi"
        if config.platform == "lupi"
        else "PC"
    )

    game_lua = (
        "-- Gerado pelo Lupix Studio\n"
        f"-- Plataforma principal: {platform_name}\n"
        f"-- Resolução de saída: "
        f"{config.width}x{config.height}\n\n"
        "function update(frame)\n"
        "end\n"
    )

    (project_dir / config.entry_point).write_text(
        game_lua,
        encoding="utf-8",
    )

    readme = (
        f"# {config.name}\n\n"
        "Projeto criado com o Lupix Studio.\n\n"
        "## Plataforma principal\n\n"
        f"{platform_name}\n\n"
        "## Resolução de saída\n\n"
        f"{config.width}x{config.height}\n\n"
        "A resolução define apenas a área exibida ao jogador.\n"
        "O mundo e os TileMaps podem ser maiores que a saída.\n\n"
        "## Entrada\n\n"
        f"{config.entry_point}\n"
    )

    (project_dir / "README.md").write_text(
        readme,
        encoding="utf-8",
    )