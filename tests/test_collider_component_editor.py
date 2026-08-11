from lupix_studio.scene.model import (
    ColliderComponent,
    SceneEntity,
)


def test_collider_can_be_added_to_entity() -> None:
    entity = SceneEntity(
        name="Player"
    )

    entity.collider = ColliderComponent(
        width=16,
        height=28,
    )

    entity.refresh_kind()

    assert entity.collider is not None
    assert entity.collider.width == 16
    assert entity.collider.height == 28


def test_collider_can_coexist_with_other_components() -> None:
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