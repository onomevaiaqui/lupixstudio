from pathlib import Path

from lupix_studio.runtime import (
    SceneRuntime,
)
from lupix_studio.scene.model import (
    ColliderComponent,
    PlayerControllerComponent,
    SceneEntity,
    SceneResource,
    TileMapComponent,
)
from lupix_studio.tilemap import (
    TileMapResource,
    TileMapSerializer,
)


def create_runtime_scene() -> SceneResource:
    scene = SceneResource(
        name="Main",
        width=480,
        height=270,
    )

    player = SceneEntity(
        name="Player",
        collider=ColliderComponent(
            width=16,
            height=28,
        ),
        player_controller=PlayerControllerComponent(
            speed=100.0,
            jump_force=200.0,
            gravity=600.0,
            max_fall_speed=500.0,
            air_control=0.75,
        ),
    )

    player.transform.x = 100.0
    player.transform.y = 256.0

    scene.add_entity(
        player
    )

    return scene


def create_tilemap_collision_scene(
    tmp_path: Path,
) -> SceneResource:
    scene = SceneResource(
        name="Main",
        width=320,
        height=240,
    )

    tilemap = TileMapResource(
        name="Level",
        tile_width=16,
        tile_height=16,
        width=20,
        height=15,
    )

    collision_layer = None

    for layer in tilemap.layers:
        if layer.name == "Collision":
            collision_layer = layer
            break

    assert collision_layer is not None

    for column in range(20):
        collision_layer.set_tile(
            column,
            10,
            0,
        )

    collision_layer.set_tile(
        10,
        9,
        0,
    )

    collision_layer.set_tile(
        10,
        8,
        0,
    )

    path = TileMapSerializer().save(
        tilemap,
        tmp_path / "maps" / "Level",
    )

    map_entity = SceneEntity(
        name="Mapa",
        tilemap=TileMapComponent(
            resource_path=(
                path.relative_to(
                    tmp_path
                )
                .as_posix()
            )
        ),
    )

    scene.add_entity(
        map_entity
    )

    player = SceneEntity(
        name="Player",
        collider=ColliderComponent(
            width=16,
            height=28,
        ),
        player_controller=PlayerControllerComponent(
            speed=100.0,
            jump_force=200.0,
            gravity=600.0,
            max_fall_speed=500.0,
            air_control=0.75,
        ),
    )

    player.transform.x = 80.0
    player.transform.y = 80.0

    scene.add_entity(
        player
    )

    return scene


def test_runtime_copies_scene() -> None:
    scene = create_runtime_scene()

    runtime = SceneRuntime(
        scene
    )

    player = runtime.player

    assert player is not None

    player.transform.x = 200.0

    original_player = (
        scene.player_entity()
    )

    assert original_player is not None

    assert (
        original_player.transform.x
        == 100.0
    )

    assert (
        player.transform.x
        == 200.0
    )


def test_player_moves_right() -> None:
    scene = create_runtime_scene()

    runtime = SceneRuntime(
        scene
    )

    runtime.start()

    runtime.input.right = True

    runtime.update(
        0.1
    )

    player = runtime.player

    assert player is not None

    assert player.transform.x > 100.0


def test_player_moves_left() -> None:
    scene = create_runtime_scene()

    runtime = SceneRuntime(
        scene
    )

    runtime.start()

    runtime.input.left = True

    runtime.update(
        0.1
    )

    player = runtime.player

    assert player is not None

    assert player.transform.x < 100.0


def test_player_jumps() -> None:
    scene = create_runtime_scene()

    runtime = SceneRuntime(
        scene
    )

    runtime.start()

    player = runtime.player

    assert player is not None

    initial_y = (
        player.transform.y
    )

    runtime.input.jump = True

    runtime.update(
        0.05
    )

    assert (
        player.transform.y
        < initial_y
    )


def test_gravity_returns_player_to_floor() -> None:
    scene = create_runtime_scene()

    runtime = SceneRuntime(
        scene
    )

    runtime.start()

    runtime.input.jump = True

    runtime.update(
        0.05
    )

    runtime.input.jump = False

    for _ in range(200):
        runtime.update(
            1.0 / 60.0
        )

    player = runtime.player

    assert player is not None

    expected_floor = (
        270.0
        - 14.0
    )

    assert (
        player.transform.y
        == expected_floor
    )

    state = runtime.state_for(
        player.id
    )

    assert state.on_ground is True


def test_player_stays_inside_scene() -> None:
    scene = create_runtime_scene()

    runtime = SceneRuntime(
        scene
    )

    runtime.start()

    runtime.input.left = True

    for _ in range(300):
        runtime.update(
            1.0 / 60.0
        )

    player = runtime.player

    assert player is not None

    assert (
        player.transform.x
        >= 8.0
    )


def test_runtime_stop_prevents_updates() -> None:
    scene = create_runtime_scene()

    runtime = SceneRuntime(
        scene
    )

    runtime.start()
    runtime.stop()

    player = runtime.player

    assert player is not None

    initial_x = (
        player.transform.x
    )

    runtime.input.right = True

    runtime.update(
        1.0
    )

    assert (
        player.transform.x
        == initial_x
    )


def test_runtime_loads_collision_tiles(
    tmp_path: Path,
) -> None:
    scene = (
        create_tilemap_collision_scene(
            tmp_path
        )
    )

    runtime = SceneRuntime(
        scene,
        project_root=tmp_path,
    )

    assert len(
        runtime.collision_rects
    ) == 22


def test_player_lands_on_tilemap_floor(
    tmp_path: Path,
) -> None:
    scene = (
        create_tilemap_collision_scene(
            tmp_path
        )
    )

    runtime = SceneRuntime(
        scene,
        project_root=tmp_path,
    )

    runtime.start()

    for _ in range(200):
        runtime.update(
            1.0 / 60.0
        )

    player = runtime.player

    assert player is not None

    floor_top = (
        10 * 16
    )

    expected_y = (
        floor_top
        - 14
    )

    assert abs(
        player.transform.y
        - expected_y
    ) < 0.01

    state = runtime.state_for(
        player.id
    )

    assert state.on_ground is True


def test_player_stops_at_tilemap_wall(
    tmp_path: Path,
) -> None:
    scene = (
        create_tilemap_collision_scene(
            tmp_path
        )
    )

    runtime = SceneRuntime(
        scene,
        project_root=tmp_path,
    )

    runtime.start()

    player = runtime.player

    assert player is not None

    player.transform.y = 130.0

    runtime.input.right = True

    for _ in range(200):
        runtime.update(
            1.0 / 60.0
        )

    wall_left = (
        10 * 16
    )

    player_half_width = 8.0

    assert (
        player.transform.x
        <= wall_left
        - player_half_width
        + 0.01
    )