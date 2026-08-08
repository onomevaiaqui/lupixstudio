from lupix_studio.scene.model import (
    SceneEntity,
    Transform2D,
)


def test_entity_transform_values() -> None:
    entity = SceneEntity(
        name="Player",
        transform=Transform2D(
            x=120,
            y=90,
            rotation=45,
            scale_x=2,
            scale_y=1.5,
        ),
    )

    assert entity.transform.x == 120
    assert entity.transform.y == 90
    assert entity.transform.rotation == 45
    assert entity.transform.scale_x == 2
    assert entity.transform.scale_y == 1.5