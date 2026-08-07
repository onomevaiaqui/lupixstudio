from pathlib import Path

from PySide6.QtGui import QImage

from lupix_studio.tileset.model import (
    TilePattern,
    TileSetResource,
)
from lupix_studio.tileset.validator import (
    pattern_is_inside,
    tileset_columns,
    tileset_rows,
    validate_tileset,
)


def test_grid_size_helpers() -> None:
    assert tileset_columns(160, 16) == 10
    assert tileset_rows(80, 16) == 5


def test_pattern_inside_grid() -> None:
    pattern = TilePattern(
        name="Parede",
        column=2,
        row=1,
        width=2,
        height=2,
    )

    assert pattern_is_inside(
        pattern,
        columns=10,
        rows=5,
    )


def test_pattern_outside_grid() -> None:
    pattern = TilePattern(
        name="Fora",
        column=9,
        row=4,
        width=2,
        height=2,
    )

    assert not pattern_is_inside(
        pattern,
        columns=10,
        rows=5,
    )


def test_valid_tileset(
    tmp_path: Path,
) -> None:
    texture = (
        tmp_path
        / "assets"
        / "tilesets"
        / "tiles.png"
    )

    texture.parent.mkdir(
        parents=True
    )

    image = QImage(
        160,
        80,
        QImage.Format.Format_ARGB32,
    )

    image.fill(
        0xFFFFFFFF
    )

    assert image.save(
        str(texture)
    )

    resource = TileSetResource(
        name="Teste",
        asset_id="abc",
        texture="assets/tilesets/tiles.png",
        tile_width=16,
        tile_height=16,
        patterns=[
            TilePattern(
                name="Parede",
                column=1,
                row=1,
                width=2,
                height=2,
            )
        ],
    )

    issues = validate_tileset(
        resource,
        tmp_path,
    )

    assert issues == []


def test_invalid_pattern_is_detected(
    tmp_path: Path,
) -> None:
    texture = (
        tmp_path
        / "assets"
        / "tilesets"
        / "tiles.png"
    )

    texture.parent.mkdir(
        parents=True
    )

    image = QImage(
        32,
        32,
        QImage.Format.Format_ARGB32,
    )

    image.fill(
        0xFFFFFFFF
    )

    assert image.save(
        str(texture)
    )

    resource = TileSetResource(
        name="Teste",
        asset_id="abc",
        texture="assets/tilesets/tiles.png",
        tile_width=16,
        tile_height=16,
        patterns=[
            TilePattern(
                name="Fora",
                column=1,
                row=1,
                width=2,
                height=2,
            )
        ],
    )

    issues = validate_tileset(
        resource,
        tmp_path,
    )

    assert any(
        issue.level == "error"
        for issue in issues
    )