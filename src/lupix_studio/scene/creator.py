from __future__ import annotations

import re
from pathlib import Path

from lupix_studio.scene.model import SceneEntity, SceneResource
from lupix_studio.scene.serializer import SceneSerializer


def sanitize_scene_name(
    name: str,
) -> str:
    """Converte um nome de cena em um nome de arquivo seguro."""

    name = name.strip()

    if not name:
        raise ValueError(
            "Informe um nome para a cena."
        )

    safe_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        name,
    )

    safe_name = safe_name.strip("_")

    if not safe_name:
        raise ValueError(
            "O nome da cena é inválido."
        )

    return safe_name


def create_scene(
    project_root: Path,
    name: str,
    width: int = 480,
    height: int = 270,
    scene_type: str = "scene",
) -> Path:
    """Cria uma nova cena dentro da pasta scenes."""

    project_root = Path(
        project_root
    ).resolve()

    if scene_type not in {"scene", "interface"}:
        raise ValueError("Tipo de cena inválido.")

    if width <= 0 or height <= 0:
        raise ValueError(
            "A resolução da cena deve ser maior que zero."
        )

    safe_name = sanitize_scene_name(
        name
    )

    scenes_directory = (
        project_root
        / "scenes"
    )

    scenes_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        scenes_directory
        / f"{safe_name}.scene"
    )

    if path.exists():
        raise FileExistsError(
            f"A cena '{safe_name}' já existe."
        )

    entities = (
        [SceneEntity(name="UI", kind="ui_canvas")]
        if scene_type == "interface"
        else []
    )
    resource = SceneResource(
        name=name.strip(),
        width=width,
        height=height,
        entities=entities,
        type=scene_type,
    )

    serializer = SceneSerializer()

    return serializer.save(
        resource,
        path,
    )