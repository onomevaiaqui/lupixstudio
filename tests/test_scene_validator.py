from pathlib import Path

from lupix_studio.scene.model import (
    CameraComponent,
    ColliderComponent,
    PlayerControllerComponent,
    SceneEntity,
    SceneResource,
    TileMapComponent,
)
from lupix_studio.scene.validator import (
    validate_scene,
)
from lupix_studio.tilemap import (
    TileMapResource,
    TileMapSerializer,
)


def test_player_without_collider_is_error() -> None:
    scene = SceneResource(
        name="Main"
    )

    scene.add_entity(
        SceneEntity(
            name="Player",
            player_controller=(
                PlayerControllerComponent()
            ),
        )
    )

    issues = validate_scene(
        scene
    )

    assert any(
        issue.level == "error"
        and "Collider" in issue.message
        for issue in issues
    )


def test_multiple_players_are_error() -> None:
    scene = SceneResource(
        name="Main"
    )

    for name in (
        "Player1",
        "Player2",
    ):
        scene.add_entity(
            SceneEntity(
                name=name,
                collider=ColliderComponent(),
                player_controller=(
                    PlayerControllerComponent()
                ),
            )
        )

    issues = validate_scene(
        scene
    )

    assert any(
        "Mais de um Player Controller"
        in issue.message
        for issue in issues
    )


def test_camera_without_active_camera_is_warning() -> None:
    scene = SceneResource(
        name="Main"
    )

    scene.add_entity(
        SceneEntity(
            name="Camera",
            camera=CameraComponent(
                active=False
            ),
        )
    )

    issues = validate_scene(
        scene
    )

    assert any(
        issue.level == "warning"
        and "nenhuma Camera está ativa"
        in issue.message
        for issue in issues
    )


def test_valid_player_has_no_player_error() -> None:
    scene = SceneResource(
        name="Main"
    )

    scene.add_entity(
        SceneEntity(
            name="Player",
            collider=ColliderComponent(),
            player_controller=(
                PlayerControllerComponent()
            ),
        )
    )

    issues = validate_scene(
        scene
    )

    assert not any(
        issue.level == "error"
        for issue in issues
    )


def test_tilemap_without_tileset_is_warning(
    tmp_path: Path,
) -> None:
    tilemap = TileMapResource(
        name="Mapa",
        width=10,
        height=10,
        tile_width=16,
        tile_height=16,
    )

    path = TileMapSerializer().save(
        tilemap,
        tmp_path / "maps" / "Mapa",
    )

    scene = SceneResource(
        name="Main"
    )

    scene.add_entity(
        SceneEntity(
            name="Mapa",
            tilemap=TileMapComponent(
                resource_path=(
                    path.relative_to(
                        tmp_path
                    ).as_posix()
                )
            ),
        )
    )

    issues = validate_scene(
        scene,
        tmp_path,
    )

    assert any(
        "não possui TileSet associado"
        in issue.message
        for issue in issues
    )


def test_empty_collision_layer_is_warning(
    tmp_path: Path,
) -> None:
    tilemap = TileMapResource(
        name="Mapa",
        width=10,
        height=10,
        tile_width=16,
        tile_height=16,
        tileset_asset_id="tileset",
    )

    path = TileMapSerializer().save(
        tilemap,
        tmp_path / "maps" / "Mapa",
    )

    scene = SceneResource(
        name="Main"
    )

    scene.add_entity(
        SceneEntity(
            name="Mapa",
            tilemap=TileMapComponent(
                resource_path=(
                    path.relative_to(
                        tmp_path
                    ).as_posix()
                )
            ),
        )
    )

    issues = validate_scene(
        scene,
        tmp_path,
    )

    assert any(
        "Collision vazia"
        in issue.message
        for issue in issues
    )