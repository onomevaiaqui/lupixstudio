from pathlib import Path

from lupix_studio.scene.model import (
    ColliderComponent,
    PlayerControllerComponent,
    SceneEntity,
    SceneResource,
    SpriteComponent,
)
from lupix_studio.scene.serializer import (
    SceneSerializer,
)


def test_player_controller_roundtrip() -> None:
    controller = PlayerControllerComponent(
        enabled=True,
        speed=100.0,
        jump_force=250.0,
        gravity=700.0,
        max_fall_speed=550.0,
        air_control=0.5,
    )

    data = controller.to_dict()

    loaded = PlayerControllerComponent.from_dict(
        data
    )

    assert loaded.enabled is True
    assert loaded.speed == 100.0
    assert loaded.jump_force == 250.0
    assert loaded.gravity == 700.0
    assert loaded.max_fall_speed == 550.0
    assert loaded.air_control == 0.5


def test_player_controller_air_control_is_clamped() -> None:
    loaded = PlayerControllerComponent.from_dict(
        {
            "air_control": 5.0,
        }
    )

    assert loaded.air_control == 1.0


def test_player_entity() -> None:
    scene = SceneResource(
        name="Main"
    )

    player = SceneEntity(
        name="Player",
        player_controller=PlayerControllerComponent(),
    )

    scene.add_entity(
        player
    )

    assert scene.player_entity() is player


def test_components_can_coexist_on_player() -> None:
    player = SceneEntity(
        name="Player",
        sprite=SpriteComponent(
            asset_id="player"
        ),
        collider=ColliderComponent(
            width=16,
            height=28,
        ),
        player_controller=PlayerControllerComponent(),
    )

    player.refresh_kind()

    assert player.sprite is not None
    assert player.collider is not None
    assert player.player_controller is not None

    assert player.kind == "sprite"


def test_player_controller_scene_roundtrip(
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
        ),
        player_controller=PlayerControllerComponent(
            speed=90.0,
            jump_force=240.0,
            gravity=650.0,
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

    loaded_player = loaded.entities[0]

    assert loaded_player.player_controller is not None
    assert loaded_player.player_controller.speed == 90.0
    assert loaded_player.player_controller.jump_force == 240.0
    assert loaded_player.player_controller.gravity == 650.0