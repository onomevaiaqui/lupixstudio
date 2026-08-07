from pathlib import Path

from lupix_studio.tileset.model import TileSetResource
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
    assert loaded.asset_id == "asset-123"
    assert loaded.texture == (
        "assets/tilesets/dungeon.png"
    )
    assert loaded.tile_width == 16
    assert loaded.tile_height == 16