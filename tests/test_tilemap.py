from pathlib import Path

from lupix_studio.tilemap import (
    TileLayer,
    TileMapResource,
    TileMapSerializer,
)


def test_default_tilemap() -> None:
    resource = TileMapResource(
        name="Main"
    )

    assert resource.tile_width == 16
    assert resource.tile_height == 16

    assert resource.width == 30
    assert resource.height == 17

    assert len(
        resource.layers
    ) == 4


def test_set_and_remove_tile() -> None:
    layer = TileLayer(
        "Ground"
    )

    layer.set_tile(
        2,
        3,
        7,
    )

    assert layer.tile(
        2,
        3,
    ) == 7

    layer.set_tile(
        2,
        3,
        None,
    )

    assert layer.tile(
        2,
        3,
    ) is None


def test_add_layer() -> None:
    resource = TileMapResource(
        name="Main"
    )

    layer = resource.add_layer(
        "Foreground"
    )

    assert layer.name == "Foreground"

    assert len(
        resource.layers
    ) == 5


def test_remove_layer() -> None:
    resource = TileMapResource(
        name="Main"
    )

    assert resource.remove_layer(
        0
    )

    assert len(
        resource.layers
    ) == 3


def test_tilemap_roundtrip(
    tmp_path: Path,
) -> None:
    resource = TileMapResource(
        name="MapaPrincipal",
        tileset_asset_id="tileset-123",
        tile_width=16,
        tile_height=16,
        width=30,
        height=17,
    )

    ground = resource.layers[1]

    ground.set_tile(
        2,
        3,
        7,
    )

    ground.set_tile(
        3,
        3,
        8,
    )

    serializer = TileMapSerializer()

    path = serializer.save(
        resource,
        tmp_path / "Main",
    )

    loaded = serializer.load(
        path
    )

    assert path.suffix == ".tilemap"

    assert loaded.name == "MapaPrincipal"

    assert (
        loaded.tileset_asset_id
        == "tileset-123"
    )

    assert loaded.width == 30
    assert loaded.height == 17

    assert len(
        loaded.layers
    ) == 4

    assert (
        loaded.layers[1].tile(
            2,
            3,
        )
        == 7
    )

    assert (
        loaded.layers[1].tile(
            3,
            3,
        )
        == 8
    )