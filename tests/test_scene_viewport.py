from lupix_studio.scene.model import SceneResource
from lupix_studio.ui.scene_viewport import (
    SceneCanvas,
    SceneViewport,
)


def test_scene_viewport_classes_exist() -> None:
    assert SceneCanvas.__name__ == "SceneCanvas"
    assert SceneViewport.__name__ == "SceneViewport"


def test_scene_resource_resolution() -> None:
    scene = SceneResource(
        name="Main",
        width=480,
        height=270,
    )

    assert scene.width == 480
    assert scene.height == 270