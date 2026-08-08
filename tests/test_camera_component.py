from lupix_studio.scene.model import (
    CameraComponent,
    SceneEntity,
    SceneResource,
)


def test_camera_component_roundtrip() -> None:
    entity = SceneEntity(
        name="Camera",
        camera=CameraComponent(
            active=True,
            width=480,
            height=270,
            zoom=2.0,
        ),
    )

    entity.refresh_kind()

    data = entity.to_dict()

    loaded = SceneEntity.from_dict(
        data
    )

    assert loaded.camera is not None
    assert loaded.camera.active is True
    assert loaded.camera.width == 480
    assert loaded.camera.height == 270
    assert loaded.camera.zoom == 2.0
    assert loaded.kind == "camera"


def test_only_one_camera_is_active() -> None:
    scene = SceneResource(
        name="Main"
    )

    camera_a = SceneEntity(
        name="CameraA",
        camera=CameraComponent(
            active=True
        ),
    )

    camera_b = SceneEntity(
        name="CameraB",
        camera=CameraComponent(),
    )

    scene.add_entity(
        camera_a
    )

    scene.add_entity(
        camera_b
    )

    scene.activate_camera(
        camera_b.id
    )

    assert camera_a.camera is not None
    assert camera_b.camera is not None

    assert camera_a.camera.active is False
    assert camera_b.camera.active is True

    assert scene.active_camera() is camera_b