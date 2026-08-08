from lupix_studio.scene.model import (
    SceneEntity,
    SpriteComponent,
)


def test_sprite_component_roundtrip() -> None:
    entity = SceneEntity(
        name="Player",
        kind="sprite",
        sprite=SpriteComponent(
            asset_id="asset-123",
            opacity=0.75,
            flip_x=True,
            flip_y=False,
            layer=3,
        ),
    )

    data = entity.to_dict()

    loaded = SceneEntity.from_dict(
        data
    )

    assert loaded.sprite is not None
    assert loaded.sprite.asset_id == "asset-123"
    assert loaded.sprite.opacity == 0.75
    assert loaded.sprite.flip_x is True
    assert loaded.sprite.flip_y is False
    assert loaded.sprite.layer == 3