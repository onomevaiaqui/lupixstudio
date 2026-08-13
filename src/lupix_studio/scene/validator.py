from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lupix_studio.scene.model import (
    SceneResource,
)
from lupix_studio.tilemap.serializer import (
    TileMapSerializer,
)


@dataclass(slots=True)
class SceneIssue:
    level: str
    message: str


def validate_scene(
    scene: SceneResource,
    project_root: Path | None = None,
) -> list[SceneIssue]:
    issues: list[SceneIssue] = []

    _validate_players(
        scene,
        issues,
    )

    _validate_cameras(
        scene,
        issues,
    )

    if project_root is not None:
        _validate_tilemaps(
            scene,
            project_root,
            issues,
        )

    return issues


def _validate_players(
    scene: SceneResource,
    issues: list[SceneIssue],
) -> None:
    active_players = []

    for entity in scene.entities:
        controller = (
            entity.player_controller
        )

        if (
            controller is None
            or not controller.enabled
        ):
            continue

        active_players.append(
            entity
        )

        if (
            entity.collider is None
            or not entity.collider.enabled
        ):
            issues.append(
                SceneIssue(
                    level="error",
                    message=(
                        f'Entidade "{entity.name}" possui '
                        "Player Controller ativo, mas não "
                        "possui Collider ativo."
                    ),
                )
            )

    if len(active_players) > 1:
        names = ", ".join(
            entity.name
            for entity in active_players
        )

        issues.append(
            SceneIssue(
                level="error",
                message=(
                    "Mais de um Player Controller "
                    f"está ativo na cena: {names}."
                ),
            )
        )


def _validate_cameras(
    scene: SceneResource,
    issues: list[SceneIssue],
) -> None:
    cameras = [
        entity
        for entity in scene.entities
        if entity.camera is not None
    ]

    if not cameras:
        return

    active_cameras = [
        entity
        for entity in cameras
        if (
            entity.camera is not None
            and entity.camera.active
        )
    ]

    if not active_cameras:
        issues.append(
            SceneIssue(
                level="warning",
                message=(
                    "A cena possui Camera, mas nenhuma "
                    "Camera está ativa."
                ),
            )
        )

    if len(active_cameras) > 1:
        names = ", ".join(
            entity.name
            for entity in active_cameras
        )

        issues.append(
            SceneIssue(
                level="error",
                message=(
                    "Mais de uma Camera está ativa "
                    f"na cena: {names}."
                ),
            )
        )


def _validate_tilemaps(
    scene: SceneResource,
    project_root: Path,
    issues: list[SceneIssue],
) -> None:
    serializer = TileMapSerializer()

    for entity in scene.entities:
        component = (
            entity.tilemap
        )

        if component is None:
            continue

        if not component.resource_path:
            issues.append(
                SceneIssue(
                    level="error",
                    message=(
                        f'Entidade "{entity.name}" possui '
                        "TileMap sem caminho de recurso."
                    ),
                )
            )
            continue

        path = (
            project_root
            / component.resource_path
        )

        if not path.exists():
            issues.append(
                SceneIssue(
                    level="error",
                    message=(
                        f'TileMap da entidade "{entity.name}" '
                        "não foi encontrado."
                    ),
                )
            )
            continue

        try:
            tilemap = serializer.load(
                path
            )

        except (
            OSError,
            ValueError,
            TypeError,
        ) as error:
            issues.append(
                SceneIssue(
                    level="error",
                    message=(
                        f'Não foi possível carregar o TileMap '
                        f'da entidade "{entity.name}": {error}'
                    ),
                )
            )
            continue

        if not tilemap.tileset_asset_id:
            issues.append(
                SceneIssue(
                    level="warning",
                    message=(
                        f'TileMap da entidade "{entity.name}" '
                        "não possui TileSet associado."
                    ),
                )
            )

        collision_layer = None

        for layer in tilemap.layers:
            if (
                layer.name.strip().lower()
                == "collision"
            ):
                collision_layer = layer
                break

        if collision_layer is None:
            issues.append(
                SceneIssue(
                    level="warning",
                    message=(
                        f'TileMap da entidade "{entity.name}" '
                        "não possui camada Collision."
                    ),
                )
            )
            continue

        if not collision_layer.cells:
            issues.append(
                SceneIssue(
                    level="warning",
                    message=(
                        f'TileMap da entidade "{entity.name}" '
                        "possui camada Collision vazia."
                    ),
                )
            )