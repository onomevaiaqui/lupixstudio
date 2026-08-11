from lupix_studio.scene.model import (
    ColliderComponent,
    PlayerControllerComponent,
    SceneEntity,
    SpriteComponent,
)


def test_player_controller_can_be_added() -> None:
    entity = SceneEntity(
        name="Player"
    )

    entity.player_controller = (
        PlayerControllerComponent()
    )

    entity.refresh_kind()

    assert (
        entity.player_controller
        is not None
    )


def test_player_controller_defaults() -> None:
    controller = (
        PlayerControllerComponent()
    )

    assert controller.enabled is True
    assert controller.speed == 80.0
    assert controller.jump_force == 220.0
    assert controller.gravity == 600.0
    assert controller.max_fall_speed == 500.0
    assert controller.air_control == 0.75


def test_player_components_can_coexist() -> None:
    entity = SceneEntity(
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

    entity.refresh_kind()

    assert entity.sprite is not None
    assert entity.collider is not None
    assert (
        entity.player_controller
        is not None
    )

    assert entity.kind == "sprite"