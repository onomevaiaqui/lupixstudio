from pathlib import Path

from lupix_studio.scene.model import (
    CameraComponent,
    SceneEntity,
    SceneResource,
    SpriteComponent,
    TileMapComponent,
)
from lupix_studio.scene.serializer import (
    SceneSerializer,
)


def test_tilemap_component_roundtrip() -> None:
    component = TileMapComponent(
        resource_path="maps/Main.tilemap"
    )

    data = component.to_dict()

    loaded = TileMapComponent.from_dict(
        data
    )

    assert (
        loaded.resource_path
        == "maps/Main.tilemap"
    )


def test_entity_with_tilemap() -> None:
    entity = SceneEntity(
        name="Mapa",
        tilemap=TileMapComponent(
            resource_path="maps/Main.tilemap"
        ),
    )

    entity.refresh_kind()

    assert entity.kind == "tilemap"
    assert entity.tilemap is not None

    assert (
        entity.tilemap.resource_path
        == "maps/Main.tilemap"
    )


def test_components_can_coexist() -> None:
    entity = SceneEntity(
        name="World",
        sprite=SpriteComponent(
            asset_id="sprite-123"
        ),
        camera=CameraComponent(
            active=True
        ),
        tilemap=TileMapComponent(
            resource_path="maps/Main.tilemap"
        ),
    )

    assert entity.sprite is not None
    assert entity.camera is not None
    assert entity.tilemap is not None

    entity.refresh_kind()

    assert entity.kind == "tilemap"


def test_scene_tilemap_roundtrip(
    tmp_path: Path,
) -> None:
    scene = SceneResource(
        name="Main"
    )

    entity = SceneEntity(
        name="Mapa",
        tilemap=TileMapComponent(
            resource_path=(
                "maps/Main.tilemap"
            )
        ),
    )

    entity.refresh_kind()

    scene.add_entity(
        entity
    )

    serializer = SceneSerializer()

    path = serializer.save(
        scene,
        tmp_path / "Main",
    )

    loaded = serializer.load(
        path
    )

    assert len(
        loaded.entities
    ) == 1

    loaded_entity = (
        loaded.entities[0]
    )

    assert (
        loaded_entity.kind
        == "tilemap"
    )

    assert (
        loaded_entity.tilemap
        is not None
    )

    assert (
        loaded_entity.tilemap.resource_path
        == "maps/Main.tilemap"
    )