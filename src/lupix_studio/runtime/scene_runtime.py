from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lupix_studio.scene.model import (
    SceneEntity,
    SceneResource,
)
from lupix_studio.tilemap.serializer import (
    TileMapSerializer,
)


@dataclass(slots=True)
class RuntimeInput:
    left: bool = False
    right: bool = False
    jump: bool = False


@dataclass(slots=True)
class EntityRuntimeState:
    velocity_x: float = 0.0
    velocity_y: float = 0.0

    on_ground: bool = False
    jump_was_pressed: bool = False


@dataclass(slots=True)
class CollisionRect:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height


class SceneRuntime:
    """Estado executável e independente de uma Scene."""

    def __init__(
        self,
        source_scene: SceneResource,
        project_root: Path | None = None,
    ) -> None:
        self.scene = SceneResource.from_dict(
            source_scene.to_dict()
        )

        self.project_root = (
            project_root.resolve()
            if project_root is not None
            else None
        )

        self.input = RuntimeInput()

        self.entity_states: dict[
            str,
            EntityRuntimeState,
        ] = {}

        for entity in self.scene.entities:
            self.entity_states[
                entity.id
            ] = EntityRuntimeState()

        self.collision_rects: list[
            CollisionRect
        ] = []

        self._load_tilemap_collisions()

        self.running = False

    @property
    def player(
        self,
    ) -> SceneEntity | None:
        return self.scene.player_entity()

    def start(self) -> None:
        self.running = True

        player = self.player

        if player is not None:
            state = self.state_for(
                player.id
            )

            self._update_ground_state(
                player,
                state,
            )

    def stop(self) -> None:
        self.running = False

        self.input = RuntimeInput()

    def state_for(
        self,
        entity_id: str,
    ) -> EntityRuntimeState:
        if entity_id not in self.entity_states:
            self.entity_states[
                entity_id
            ] = EntityRuntimeState()

        return self.entity_states[
            entity_id
        ]

    def update(
        self,
        delta: float,
    ) -> None:
        if not self.running:
            return

        if delta <= 0.0:
            return

        player = self.player

        if (
            player is None
            or player.player_controller is None
            or not player.player_controller.enabled
        ):
            return

        controller = (
            player.player_controller
        )

        state = self.state_for(
            player.id
        )

        self._update_horizontal_velocity(
            controller.speed,
            controller.air_control,
            state,
        )

        self._apply_jump(
            controller.jump_force,
            state,
        )

        self._apply_gravity(
            controller.gravity,
            controller.max_fall_speed,
            state,
            delta,
        )

        self._move_horizontal(
            player,
            state,
            delta,
        )

        self._move_vertical(
            player,
            state,
            delta,
        )

        self._apply_scene_horizontal_bounds(
            player,
            state,
        )

        self._apply_scene_floor(
            player,
            state,
        )

        self._refresh_ground_state(
            player,
            state,
        )

        state.jump_was_pressed = (
            self.input.jump
        )

    def _update_horizontal_velocity(
        self,
        speed: float,
        air_control: float,
        state: EntityRuntimeState,
    ) -> None:
        direction = 0.0

        if self.input.left:
            direction -= 1.0

        if self.input.right:
            direction += 1.0

        target_velocity = (
            direction
            * speed
        )

        if state.on_ground:
            state.velocity_x = (
                target_velocity
            )
            return

        control = max(
            0.0,
            min(
                1.0,
                air_control,
            ),
        )

        state.velocity_x += (
            target_velocity
            - state.velocity_x
        ) * control

    def _apply_jump(
        self,
        jump_force: float,
        state: EntityRuntimeState,
    ) -> None:
        jump_pressed_now = (
            self.input.jump
            and not state.jump_was_pressed
        )

        if (
            jump_pressed_now
            and state.on_ground
        ):
            state.velocity_y = (
                -jump_force
            )

            state.on_ground = False

    def _apply_gravity(
        self,
        gravity: float,
        max_fall_speed: float,
        state: EntityRuntimeState,
        delta: float,
    ) -> None:
        if state.on_ground:
            state.velocity_y = min(state.velocity_y, 0.0)

            return

        state.velocity_y += (
            gravity
            * delta
        )

        state.velocity_y = min(
            state.velocity_y,
            max_fall_speed,
        )

    def _move_horizontal(
        self,
        player: SceneEntity,
        state: EntityRuntimeState,
        delta: float,
    ) -> None:
        movement = (
            state.velocity_x
            * delta
        )

        if movement == 0.0:
            return

        player.transform.x += movement

        player_rect = (
            self._player_collision_rect(
                player
            )
        )

        if player_rect is None:
            return

        collisions = self._intersections(
            player_rect
        )

        for collision in collisions:
            if state.velocity_x > 0.0:
                correction = (
                    player_rect.right
                    - collision.left
                )

                player.transform.x -= (
                    correction
                )

            elif state.velocity_x < 0.0:
                correction = (
                    collision.right
                    - player_rect.left
                )

                player.transform.x += (
                    correction
                )

            state.velocity_x = 0.0

            player_rect = (
                self._player_collision_rect(
                    player
                )
            )

            if player_rect is None:
                return

    def _move_vertical(
        self,
        player: SceneEntity,
        state: EntityRuntimeState,
        delta: float,
    ) -> None:
        movement = (
            state.velocity_y
            * delta
        )

        if movement == 0.0:
            return

        player.transform.y += movement

        player_rect = (
            self._player_collision_rect(
                player
            )
        )

        if player_rect is None:
            return

        collisions = self._intersections(
            player_rect
        )

        for collision in collisions:
            if state.velocity_y > 0.0:
                correction = (
                    player_rect.bottom
                    - collision.top
                )

                player.transform.y -= (
                    correction
                )

                state.on_ground = True

            elif state.velocity_y < 0.0:
                correction = (
                    collision.bottom
                    - player_rect.top
                )

                player.transform.y += (
                    correction
                )

            state.velocity_y = 0.0

            player_rect = (
                self._player_collision_rect(
                    player
                )
            )

            if player_rect is None:
                return

    def _player_collision_rect(
        self,
        player: SceneEntity,
    ) -> CollisionRect | None:
        collider = player.collider

        if (
            collider is None
            or not collider.enabled
        ):
            return None

        center_x = (
            player.transform.x
            + collider.offset_x
        )

        center_y = (
            player.transform.y
            + collider.offset_y
        )

        return CollisionRect(
            x=(
                center_x
                - collider.width / 2.0
            ),
            y=(
                center_y
                - collider.height / 2.0
            ),
            width=collider.width,
            height=collider.height,
        )

    def _intersections(
        self,
        player_rect: CollisionRect,
    ) -> list[CollisionRect]:
        return [
            collision
            for collision in self.collision_rects
            if self._rects_intersect(
                player_rect,
                collision,
            )
        ]

    @staticmethod
    def _rects_intersect(
        first: CollisionRect,
        second: CollisionRect,
    ) -> bool:
        return (
            first.left < second.right
            and first.right > second.left
            and first.top < second.bottom
            and first.bottom > second.top
        )

    def _load_tilemap_collisions(
        self,
    ) -> None:
        self.collision_rects.clear()

        if self.project_root is None:
            return

        serializer = TileMapSerializer()

        for entity in self.scene.entities:
            tilemap_component = (
                entity.tilemap
            )

            if (
                tilemap_component is None
                or not tilemap_component.resource_path
            ):
                continue

            path = (
                self.project_root
                / tilemap_component.resource_path
            )

            if not path.exists():
                continue

            try:
                tilemap = serializer.load(
                    path
                )

            except (
                OSError,
                ValueError,
                TypeError,
            ):
                continue

            collision_layer = None

            for layer in tilemap.layers:
                if (
                    layer.name.strip().lower()
                    == "collision"
                ):
                    collision_layer = layer
                    break

            if collision_layer is None:
                continue

            for key in collision_layer.cells:
                try:
                    column_text, row_text = (
                        key.split(
                            ",",
                            maxsplit=1,
                        )
                    )

                    column = int(
                        column_text
                    )

                    row = int(
                        row_text
                    )

                except (
                    ValueError,
                    AttributeError,
                ):
                    continue

                self.collision_rects.append(
                    CollisionRect(
                        x=(
                            entity.transform.x
                            + column
                            * tilemap.tile_width
                        ),
                        y=(
                            entity.transform.y
                            + row
                            * tilemap.tile_height
                        ),
                        width=(
                            tilemap.tile_width
                        ),
                        height=(
                            tilemap.tile_height
                        ),
                    )
                )

    def _apply_scene_horizontal_bounds(
        self,
        player: SceneEntity,
        state: EntityRuntimeState,
    ) -> None:
        collider = player.collider

        if (
            collider is None
            or not collider.enabled
        ):
            return

        half_width = (
            collider.width
            / 2.0
        )

        left_limit = (
            half_width
            - collider.offset_x
        )

        right_limit = (
            self.scene.width
            - half_width
            - collider.offset_x
        )

        if player.transform.x < left_limit:
            player.transform.x = (
                left_limit
            )

            state.velocity_x = max(state.velocity_x, 0.0)

        if player.transform.x > right_limit:
            player.transform.x = (
                right_limit
            )

            state.velocity_x = min(state.velocity_x, 0.0)

    def _apply_scene_floor(
        self,
        player: SceneEntity,
        state: EntityRuntimeState,
    ) -> None:
        collider = player.collider

        if (
            collider is None
            or not collider.enabled
        ):
            return

        floor_y = (
            self.scene.height
            - collider.height / 2.0
            - collider.offset_y
        )

        if player.transform.y >= floor_y:
            player.transform.y = (
                floor_y
            )

            state.velocity_y = 0.0
            state.on_ground = True

    def _refresh_ground_state(
        self,
        player: SceneEntity,
        state: EntityRuntimeState,
    ) -> None:
        collider = player.collider

        if (
            collider is None
            or not collider.enabled
        ):
            state.on_ground = False
            return

        player_rect = (
            self._player_collision_rect(
                player
            )
        )

        if player_rect is None:
            state.on_ground = False
            return

        probe = CollisionRect(
            x=player_rect.x + 0.5,
            y=player_rect.y + 1.0,
            width=max(
                0.01,
                player_rect.width - 1.0,
            ),
            height=player_rect.height,
        )

        for collision in self.collision_rects:
            if self._rects_intersect(
                probe,
                collision,
            ):
                state.on_ground = True
                return

        floor_y = (
            self.scene.height
            - collider.height / 2.0
            - collider.offset_y
        )

        state.on_ground = (
            player.transform.y
            >= floor_y
        )

    def _update_ground_state(
        self,
        player: SceneEntity,
        state: EntityRuntimeState,
    ) -> None:
        self._apply_scene_floor(
            player,
            state,
        )

        self._refresh_ground_state(
            player,
            state,
        )