from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QImage

from lupix_studio.tileset.model import TilePattern, TileSetResource


@dataclass(slots=True)
class TileSetValidationIssue:
    level: str
    message: str


def tileset_columns(
    image_width: int,
    tile_width: int,
) -> int:
    if tile_width <= 0:
        return 0

    return image_width // tile_width


def tileset_rows(
    image_height: int,
    tile_height: int,
) -> int:
    if tile_height <= 0:
        return 0

    return image_height // tile_height


def pattern_is_inside(
    pattern: TilePattern,
    columns: int,
    rows: int,
) -> bool:
    if pattern.column < 0 or pattern.row < 0:
        return False

    if pattern.width <= 0 or pattern.height <= 0:
        return False

    right = pattern.column + pattern.width
    bottom = pattern.row + pattern.height

    return (
        right <= columns
        and bottom <= rows
    )


def validate_tileset(
    resource: TileSetResource,
    project_root: Path,
) -> list[TileSetValidationIssue]:
    """Valida um recurso TileSet contra sua textura."""

    issues: list[TileSetValidationIssue] = []

    texture_path = (
        project_root.resolve()
        / resource.texture
    )

    image = QImage(
        str(texture_path)
    )

    if image.isNull():
        return [
            TileSetValidationIssue(
                level="error",
                message="Não foi possível carregar a textura do TileSet.",
            )
        ]

    if resource.tile_width <= 0 or resource.tile_height <= 0:
        issues.append(
            TileSetValidationIssue(
                level="error",
                message="O tamanho do tile deve ser maior que zero.",
            )
        )
        return issues

    if image.width() % resource.tile_width != 0:
        issues.append(
            TileSetValidationIssue(
                level="warning",
                message=(
                    "A largura da textura não é divisível "
                    "pela largura do tile."
                ),
            )
        )

    if image.height() % resource.tile_height != 0:
        issues.append(
            TileSetValidationIssue(
                level="warning",
                message=(
                    "A altura da textura não é divisível "
                    "pela altura do tile."
                ),
            )
        )

    columns = tileset_columns(
        image.width(),
        resource.tile_width,
    )

    rows = tileset_rows(
        image.height(),
        resource.tile_height,
    )

    if columns <= 0 or rows <= 0:
        issues.append(
            TileSetValidationIssue(
                level="error",
                message="A grade não produz nenhuma célula válida.",
            )
        )
        return issues

    for pattern in resource.patterns:
        if not pattern_is_inside(
            pattern,
            columns,
            rows,
        ):
            issues.append(
                TileSetValidationIssue(
                    level="error",
                    message=(
                        f"O padrão '{pattern.name}' "
                        "está fora dos limites do TileSet."
                    ),
                )
            )

    return issues