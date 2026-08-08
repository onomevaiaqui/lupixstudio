from lupix_studio.scene.model import (
    SceneEntity,
    TileMapComponent,
)


def test_tilemap_component_can_be_attached() -> None:
    entity = SceneEntity(
        name="Mapa"
    )

    entity.tilemap = TileMapComponent(
        resource_path="maps/Main.tilemap"
    )

    entity.refresh_kind()

    assert entity.tilemap is not None

    assert (
        entity.tilemap.resource_path
        == "maps/Main.tilemap"
    )

    assert entity.kind == "tilemap"