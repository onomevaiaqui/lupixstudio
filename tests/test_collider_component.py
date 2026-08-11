from pathlib import Path

from lupix_studio.scene.model import (
    ColliderComponent,
    SceneEntity,
    SceneResource,
)
from lupix_studio.scene.serializer import (
    SceneSerializer,
)


def test_collider_component_roundtrip() -> None:
    collider = ColliderComponent(
        enabled=True,
        width=32,
        height=48,
        offset_x=2,
        offset_y=-4,
        solid=True,
    )

    data = collider.to_dict()

    loaded = ColliderComponent.from_dict(
        data
    )

    assert loaded.enabled is True
    assert loaded.width == 32
    assert loaded.height == 48
    assert loaded.offset_x == 2
    assert loaded.offset_y == -4
    assert loaded.solid is True


def test_entity_can_have_collider() -> None:
    entity = SceneEntity(
        name="Caixa",
        collider=ColliderComponent(
            width=32,
            height=32,
        ),
    )

    entity.refresh_kind()

    assert entity.collider is not None
    assert entity.kind == "collider"


def test_sprite_and_collider_can_coexist() -> None:
    from lupix_studio.scene.model import (
        SpriteComponent,
    )

    entity = SceneEntity(
        name="Player",
        sprite=SpriteComponent(
            asset_id="player"
        ),
        collider=ColliderComponent(
            width=16,
            height=28,
        ),
    )

    entity.refresh_kind()

    assert entity.sprite is not None
    assert entity.collider is not None

    assert entity.kind == "sprite"


def test_collider_scene_roundtrip(
    tmp_path: Path,
) -> None:
    scene = SceneResource(
        name="Main"
    )

    player = SceneEntity(
        name="Player",
        collider=ColliderComponent(
            width=16,
            height=28,
            offset_y=2,
        ),
    )

    scene.add_entity(
        player
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

    entity = loaded.entities[0]

    assert entity.collider is not None
    assert entity.collider.width == 16
    assert entity.collider.height == 28
    assert entity.collider.offset_y == 2