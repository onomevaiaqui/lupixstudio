from lupix_studio.animation import (
    AnimationClip,
    AnimationComponent,
)


def test_animation_clip_frame_duration() -> None:
    clip = AnimationClip(
        name="run",
        frames=[
            0,
            1,
            2,
            3,
        ],
        fps=10.0,
    )

    assert (
        clip.frame_duration
        == 0.1
    )


def test_looping_animation_frames() -> None:
    clip = AnimationClip(
        name="idle",
        frames=[
            10,
            11,
        ],
        fps=2.0,
        loop=True,
    )

    assert (
        clip.frame_at(
            0.0
        )
        == 10
    )

    assert (
        clip.frame_at(
            0.6
        )
        == 11
    )

    assert (
        clip.frame_at(
            1.1
        )
        == 10
    )


def test_non_looping_animation_stops_at_end() -> None:
    clip = AnimationClip(
        name="jump",
        frames=[
            4,
            5,
            6,
        ],
        fps=10.0,
        loop=False,
    )

    assert (
        clip.frame_at(
            100.0
        )
        == 6
    )


def test_empty_clip_returns_none() -> None:
    clip = AnimationClip(
        name="empty"
    )

    assert (
        clip.frame_at(
            0.0
        )
        is None
    )


def test_add_and_remove_clip() -> None:
    component = (
        AnimationComponent()
    )

    component.add_clip(
        AnimationClip(
            name="idle",
            frames=[
                0,
                1,
            ],
        )
    )

    assert (
        component.clip(
            "idle"
        )
        is not None
    )

    assert (
        component.remove_clip(
            "idle"
        )
        is True
    )

    assert (
        component.clip(
            "idle"
        )
        is None
    )


def test_default_clip() -> None:
    component = (
        AnimationComponent(
            default_animation="run"
        )
    )

    component.add_clip(
        AnimationClip(
            name="idle",
            frames=[
                0,
            ],
        )
    )

    component.add_clip(
        AnimationClip(
            name="run",
            frames=[
                1,
                2,
            ],
        )
    )

    clip = (
        component.default_clip()
    )

    assert clip is not None
    assert clip.name == "run"


def test_animation_roundtrip() -> None:
    component = AnimationComponent(
        enabled=True,
        frame_width=32,
        frame_height=32,
        default_animation="idle",
    )

    component.add_clip(
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

    component.add_clip(
        AnimationClip(
            name="run",
            frames=[
                4,
                5,
                6,
                7,
            ],
            fps=10.0,
            loop=True,
        )
    )

    data = component.to_dict()

    loaded = (
        AnimationComponent.from_dict(
            data
        )
    )

    assert loaded.enabled is True

    assert (
        loaded.frame_width
        == 32
    )

    assert (
        loaded.frame_height
        == 32
    )

    assert (
        loaded.default_animation
        == "idle"
    )

    idle = loaded.clip(
        "idle"
    )

    run = loaded.clip(
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

    assert idle.fps == 6.0

    assert run.frames == [
        4,
        5,
        6,
        7,
    ]

    assert run.fps == 10.0