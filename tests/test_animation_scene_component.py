from pathlib import Path

from lupix_studio.animation import (
    AnimationClip,
    AnimationComponent,
)
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


def create_animation_component() -> AnimationComponent:
    animation = AnimationComponent(
        enabled=True,
        frame_width=32,
        frame_height=32,
        default_animation="idle",
    )

    animation.add_clip(
        AnimationClip(
            name="idle",
            frames=[
                0,
                1,
                2,
                3,
            ],
            fps=6.0,
            loop=True,
        )
    )

    animation.add_clip(
        AnimationClip(
            name="run",
            frames=[
                4,
                5,
                6,
                7,
                8,
                9,
            ],
            fps=10.0,
            loop=True,
        )
    )

    animation.add_clip(
        AnimationClip(
            name="jump",
            frames=[
                10,
                11,
            ],
            fps=8.0,
            loop=False,
        )
    )

    animation.add_clip(
        AnimationClip(
            name="fall",
            frames=[
                12,
                13,
            ],
            fps=8.0,
            loop=True,
        )
    )

    return animation


def test_entity_accepts_animation_component() -> None:
    entity = SceneEntity(
        name="Player",
        animation=create_animation_component(),
    )

    assert entity.animation is not None

    assert (
        entity.animation.default_animation
        == "idle"
    )


def test_animation_coexists_with_player_components() -> None:
    entity = SceneEntity(
        name="Player",
        sprite=SpriteComponent(
            asset_id="player"
        ),
        animation=create_animation_component(),
        collider=ColliderComponent(
            width=16,
            height=28,
        ),
        player_controller=PlayerControllerComponent(),
    )

    entity.refresh_kind()

    assert entity.sprite is not None
    assert entity.animation is not None
    assert entity.collider is not None

    assert (
        entity.player_controller
        is not None
    )

    assert entity.kind == "sprite"


def test_animation_entity_roundtrip() -> None:
    entity = SceneEntity(
        name="Player",
        sprite=SpriteComponent(
            asset_id="player"
        ),
        animation=create_animation_component(),
    )

    data = entity.to_dict()

    loaded = SceneEntity.from_dict(
        data
    )

    assert loaded.animation is not None

    assert (
        loaded.animation.frame_width
        == 32
    )

    assert (
        loaded.animation.frame_height
        == 32
    )

    idle = loaded.animation.clip(
        "idle"
    )

    run = loaded.animation.clip(
        "run"
    )

    assert idle is not None
    assert run is not None

    assert idle.frames == [
        0,
        1,
        2,
        3,
    ]

    assert run.frames == [
        4,
        5,
        6,
        7,
        8,
        9,
    ]


def test_animation_scene_roundtrip(
    tmp_path: Path,
) -> None:
    scene = SceneResource(
        name="Main",
        width=480,
        height=270,
    )

    player = SceneEntity(
        name="Player",
        sprite=SpriteComponent(
            asset_id="player"
        ),
        animation=create_animation_component(),
        collider=ColliderComponent(
            width=16,
            height=28,
        ),
        player_controller=PlayerControllerComponent(),
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

    loaded_player = (
        loaded.entities[0]
    )

    assert (
        loaded_player.animation
        is not None
    )

    assert (
        loaded_player.animation.default_animation
        == "idle"
    )

    idle = (
        loaded_player.animation.clip(
            "idle"
        )
    )

    jump = (
        loaded_player.animation.clip(
            "jump"
        )
    )

    assert idle is not None
    assert jump is not None

    assert idle.fps == 6.0
    assert jump.loop is False


def test_scene_without_animation_remains_compatible() -> None:
    scene = SceneResource(
        name="OldScene"
    )

    entity = SceneEntity(
        name="Entity"
    )

    scene.add_entity(
        entity
    )

    data = scene.to_dict()

    loaded = SceneResource.from_dict(
        data
    )

    assert (
        loaded.entities[0].animation
        is None
    )