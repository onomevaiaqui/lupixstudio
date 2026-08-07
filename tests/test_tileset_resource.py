from pathlib import Path

from lupix_studio.tileset.model import (
    TilePattern,
    TileSetResource,
)
from lupix_studio.tileset.serializer import TileSetSerializer


def test_tileset_resource_roundtrip(
    tmp_path: Path,
) -> None:
    resource = TileSetResource(
        name="Dungeon",
        asset_id="asset-123",
        texture="assets/tilesets/dungeon.png",
        tile_width=16,
        tile_height=16,
        patterns=[
            TilePattern(
                name="Parede",
                column=2,
                row=3,
                width=2,
                height=2,
            )
        ],
    )

    path = (
        tmp_path
        / "dungeon.tileset"
    )

    serializer = TileSetSerializer()

    serializer.save(
        resource,
        path,
    )

    loaded = serializer.load(
        path
    )

    assert loaded.name == "Dungeon"
    assert loaded.tile_width == 16
    assert loaded.tile_height == 16

    assert len(
        loaded.patterns
    ) == 1

    pattern = loaded.patterns[0]

    assert pattern.name == "Parede"
    assert pattern.column == 2
    assert pattern.row == 3
    assert pattern.width == 2
    assert pattern.height == 2