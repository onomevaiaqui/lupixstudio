from pathlib import Path

from lupix_studio.scene import (
    SceneEntity,
    SceneResource,
    SceneSerializer,
    Transform2D,
)
from lupix_studio.scene.model import (
    SpriteComponent,
)


def test_scene_default_resolution() -> None:
    scene = SceneResource(
        name="Main"
    )

    assert scene.width == 480
    assert scene.height == 270


def test_add_entity() -> None:
    scene = SceneResource(
        name="Main"
    )

    player = SceneEntity(
        name="Player",
        kind="sprite",
        sprite=SpriteComponent(
            asset_id="player-asset"
        ),
    )

    scene.add_entity(
        player
    )

    assert len(
        scene.entities
    ) == 1

    assert (
        scene.entities[0].name
        == "Player"
    )


def test_find_entity() -> None:
    scene = SceneResource(
        name="Main"
    )

    player = SceneEntity(
        name="Player"
    )

    scene.add_entity(
        player
    )

    assert scene.entity(
        player.id
    ) is player


def test_remove_entity() -> None:
    scene = SceneResource(
        name="Main"
    )

    player = SceneEntity(
        name="Player"
    )

    scene.add_entity(
        player
    )

    assert scene.remove_entity(
        player.id
    )

    assert scene.entities == []


def test_scene_roundtrip(
    tmp_path: Path,
) -> None:
    scene = SceneResource(
        name="Main",
        width=480,
        height=270,
    )

    player = SceneEntity(
        name="Player",
        transform=Transform2D(
            x=120,
            y=180,
            scale_x=2,
            scale_y=2,
        ),
        sprite=SpriteComponent(
            asset_id="player-asset",
            opacity=1.0,
            flip_x=False,
            flip_y=False,
            layer=2,
        ),
    )

    player.refresh_kind()

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

    assert path.suffix == ".scene"

    assert loaded.name == "Main"
    assert loaded.width == 480
    assert loaded.height == 270

    assert len(
        loaded.entities
    ) == 1

    loaded_player = (
        loaded.entities[0]
    )

    assert (
        loaded_player.name
        == "Player"
    )

    assert (
        loaded_player.kind
        == "sprite"
    )

    assert (
        loaded_player.transform.x
        == 120
    )

    assert (
        loaded_player.transform.y
        == 180
    )

    assert (
        loaded_player.transform.scale_x
        == 2
    )

    assert (
        loaded_player.transform.scale_y
        == 2
    )

    assert (
        loaded_player.sprite
        is not None
    )

    assert (
        loaded_player.sprite.asset_id
        == "player-asset"
    )

    assert (
        loaded_player.sprite.layer
        == 2
    )