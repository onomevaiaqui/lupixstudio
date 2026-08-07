from pathlib import Path

import pytest

from lupix_studio.scene.creator import (
    create_scene,
    sanitize_scene_name,
)
from lupix_studio.scene.serializer import SceneSerializer


def test_sanitize_scene_name() -> None:
    assert sanitize_scene_name(
        "Main"
    ) == "Main"

    assert sanitize_scene_name(
        "Fase 01"
    ) == "Fase_01"


def test_create_scene(
    tmp_path: Path,
) -> None:
    path = create_scene(
        project_root=tmp_path,
        name="Main",
        width=480,
        height=270,
    )

    assert path.exists()

    assert path == (
        tmp_path
        / "scenes"
        / "Main.scene"
    )

    resource = SceneSerializer().load(
        path
    )

    assert resource.name == "Main"
    assert resource.width == 480
    assert resource.height == 270
    assert resource.entities == []


def test_duplicate_scene_is_rejected(
    tmp_path: Path,
) -> None:
    create_scene(
        tmp_path,
        "Main",
    )

    with pytest.raises(
        FileExistsError
    ):
        create_scene(
            tmp_path,
            "Main",
        )