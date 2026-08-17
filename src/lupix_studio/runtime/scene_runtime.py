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

    animation_name: str = ""
    animation_frame_index: int = 0
    animation_elapsed: float = 0.0
    animation_frame: int = 0


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


@dataclass(slots=True)
class Area2DEvent:
    """Evento gerado quando o Player entra ou sai de uma Area2D."""

    area_id: str
    event: str


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

        self.area_inside: dict[
            str,
            bool,
        ] = {}

        self.area_events: list[
            Area2DEvent
        ] = []

        for entity in self.scene.entities:
            if entity.area2d is not None:
                self.area_inside[
                    entity.id
                ] = False

        self.world_left = 0.0
        self.world_top = 0.0
        self.world_right = float(
            self.scene.width
        )
        self.world_bottom = float(
            self.scene.height
        )

        self._load_world_bounds()
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

            self._update_player_animation(
                player,
                state,
                0.0,
                force_reset=True,
            )

            self._sync_area2d_state(
                player
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

        self._update_player_animation(
            player,
            state,
            delta,
        )

        self._update_area2d_events(
            player
        )

        state.jump_was_pressed = (
            self.input.jump
        )

    def animation_frame_for(
        self,
        entity_id: str,
    ) -> int:
        """Retorna o frame atual da animação de uma entidade."""

        return self.state_for(
            entity_id
        ).animation_frame

    def animation_name_for(
        self,
        entity_id: str,
    ) -> str:
        """Retorna o nome da animação atual de uma entidade."""

        return self.state_for(
            entity_id
        ).animation_name

    def _update_player_animation(
        self,
        player: SceneEntity,
        state: EntityRuntimeState,
        delta: float,
        *,
        force_reset: bool = False,
    ) -> None:
        animation = player.animation

        if (
            animation is None
            or not animation.enabled
        ):
            state.animation_name = ""
            state.animation_frame_index = 0
            state.animation_elapsed = 0.0
            state.animation_frame = 0
            return

        if player.sprite is not None:
            if state.velocity_x < -0.01:
                player.sprite.flip_x = True

            elif state.velocity_x > 0.01:
                player.sprite.flip_x = False

        animation_name = (
            self._desired_player_animation(
                animation,
                state,
            )
        )

        if not animation_name:
            state.animation_name = ""
            state.animation_frame_index = 0
            state.animation_elapsed = 0.0
            state.animation_frame = 0
            return

        clip = animation.clip(
            animation_name
        )

        if clip is None:
            state.animation_name = ""
            state.animation_frame_index = 0
            state.animation_elapsed = 0.0
            state.animation_frame = 0
            return

        #
        # O runtime precisa trabalhar com a mesma fonte de frames
        # usada pelo Animation Editor.
        #
        # Em animações por regiões, projetos convertidos podem ter
        # regiões válidas mesmo quando a lista antiga `frames` está
        # vazia ou incompleta. Nesse caso usamos a ordem das regiões.
        #
        runtime_frames = list(
            clip.frames
        )

        if (
            not runtime_frames
            and clip.regions
        ):
            runtime_frames = list(
                clip.regions.keys()
            )

        if not runtime_frames:
            state.animation_name = animation_name
            state.animation_frame_index = 0
            state.animation_elapsed = 0.0
            state.animation_frame = 0
            return

        changed = (
            animation_name
            != state.animation_name
        )

        if (
            changed
            or force_reset
        ):
            state.animation_name = (
                animation_name
            )
            state.animation_frame_index = 0
            state.animation_elapsed = 0.0
            state.animation_frame = (
                runtime_frames[0]
            )

            if delta <= 0.0:
                return

        fps = max(
            0.01,
            float(clip.fps),
        )

        frame_duration = (
            1.0
            / fps
        )

        state.animation_elapsed += max(
            0.0,
            delta,
        )

        while (
            state.animation_elapsed
            >= frame_duration
        ):
            state.animation_elapsed -= (
                frame_duration
            )

            next_index = (
                state.animation_frame_index
                + 1
            )

            if next_index >= len(
                runtime_frames
            ):
                if clip.loop:
                    next_index = 0

                else:
                    next_index = (
                        len(runtime_frames)
                        - 1
                    )
                    state.animation_elapsed = 0.0

            state.animation_frame_index = (
                next_index
            )
            state.animation_frame = (
                runtime_frames[
                    state.animation_frame_index
                ]
            )

            if (
                not clip.loop
                and state.animation_frame_index
                == len(runtime_frames) - 1
            ):
                break

    @staticmethod
    def _desired_player_animation(
        animation,
        state: EntityRuntimeState,
    ) -> str:
        """
        Escolhe a animação que pode realmente ser renderizada.

        No modo de regiões, um clip só é considerado válido quando
        possui pelo menos uma região associada à sua sequência.

        Isso evita trocar de idle para run/jump/fall antigos que ainda
        possuem apenas índices da grade, o que fazia o Play exibir
        pedaços do spritesheet ou o atlas completo ao mover o Player.
        """

        candidates: list[str] = []

        if not state.on_ground:
            if state.velocity_y < -0.01:
                candidates.append(
                    "jump"
                )

            else:
                candidates.append(
                    "fall"
                )

        elif abs(
            state.velocity_x
        ) > 0.01:
            candidates.append(
                "run"
            )

        else:
            candidates.append(
                "idle"
            )

        default_animation = str(
            animation.default_animation
            or ""
        ).strip()

        if default_animation:
            candidates.append(
                default_animation
            )

        for name in animation.clips:
            candidates.append(
                str(name)
            )

        #
        # Se qualquer clip já utiliza regiões, tratamos o componente
        # como animação por regiões. Isso também cobre cenas antigas
        # cujo frame_mode ainda possa estar salvo como "grid".
        #
        uses_regions = (
            getattr(
                animation,
                "frame_mode",
                "grid",
            )
            == "regions"
            or any(
                bool(
                    getattr(
                        clip,
                        "regions",
                        {},
                    )
                )
                for clip in animation.clips.values()
            )
        )

        seen: set[str] = set()

        for name in candidates:
            if (
                not name
                or name in seen
            ):
                continue

            seen.add(
                name
            )

            clip = animation.clip(
                name
            )

            if clip is None:
                continue

            if uses_regions:
                runtime_frames = list(
                    clip.frames
                )

                if (
                    not runtime_frames
                    and clip.regions
                ):
                    runtime_frames = list(
                        clip.regions.keys()
                    )

                if not runtime_frames:
                    continue

                has_valid_region = any(
                    clip.region(
                        frame_id
                    )
                    is not None
                    for frame_id in runtime_frames
                )

                if has_valid_region:
                    return name

                continue

            if clip.frames:
                return name

        return ""

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

    def consume_area_events(
        self,
    ) -> list[Area2DEvent]:
        """Retorna os eventos pendentes e limpa a fila."""

        events = list(
            self.area_events
        )

        self.area_events.clear()

        return events

    def _area2d_rect(
        self,
        entity: SceneEntity,
    ) -> CollisionRect | None:
        area = entity.area2d

        if (
            area is None
            or not area.enabled
            or not area.detect_player
        ):
            return None

        center_x = (
            entity.transform.x
            + area.offset_x
        )

        center_y = (
            entity.transform.y
            + area.offset_y
        )

        return CollisionRect(
            x=(
                center_x
                - area.width / 2.0
            ),
            y=(
                center_y
                - area.height / 2.0
            ),
            width=area.width,
            height=area.height,
        )

    def _player_area_probe(
        self,
        player: SceneEntity,
    ) -> CollisionRect:
        player_rect = (
            self._player_collision_rect(
                player
            )
        )

        if player_rect is not None:
            return player_rect

        return CollisionRect(
            x=player.transform.x - 0.5,
            y=player.transform.y - 0.5,
            width=1.0,
            height=1.0,
        )

    def _sync_area2d_state(
        self,
        player: SceneEntity,
    ) -> None:
        probe = self._player_area_probe(
            player
        )

        for entity in self.scene.entities:
            if entity.area2d is None:
                continue

            area_rect = self._area2d_rect(
                entity
            )

            inside = False

            if area_rect is not None:
                inside = (
                    self._rects_intersect(
                        probe,
                        area_rect,
                    )
                )

            self.area_inside[
                entity.id
            ] = inside

    def _update_area2d_events(
        self,
        player: SceneEntity,
    ) -> None:
        probe = self._player_area_probe(
            player
        )

        for entity in self.scene.entities:
            if entity.area2d is None:
                continue

            area_rect = self._area2d_rect(
                entity
            )

            inside_now = False

            if area_rect is not None:
                inside_now = (
                    self._rects_intersect(
                        probe,
                        area_rect,
                    )
                )

            inside_before = (
                self.area_inside.get(
                    entity.id,
                    False,
                )
            )

            if (
                inside_now
                and not inside_before
            ):
                self.area_events.append(
                    Area2DEvent(
                        area_id=entity.id,
                        event="entered",
                    )
                )

            elif (
                inside_before
                and not inside_now
            ):
                self.area_events.append(
                    Area2DEvent(
                        area_id=entity.id,
                        event="exited",
                    )
                )

            self.area_inside[
                entity.id
            ] = inside_now

    def _load_world_bounds(
        self,
    ) -> None:
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

            #
            # O TileMap Editor expande width/height automaticamente
            # conforme o usuário pinta a fase.
            #
            # Essas dimensões representam o tamanho lógico atual
            # do mundo, enquanto a resolução do projeto representa
            # apenas a área de saída exibida ao jogador.
            #
            map_width = (
                tilemap.width
                * tilemap.tile_width
                * entity.transform.scale_x
            )

            map_height = (
                tilemap.height
                * tilemap.tile_height
                * entity.transform.scale_y
            )

            x1 = float(
                entity.transform.x
            )

            y1 = float(
                entity.transform.y
            )

            x2 = (
                x1
                + float(map_width)
            )

            y2 = (
                y1
                + float(map_height)
            )

            #
            # min/max também mantém o cálculo correto caso uma
            # entidade use escala negativa.
            #
            left = min(
                x1,
                x2,
            )

            right = max(
                x1,
                x2,
            )

            top = min(
                y1,
                y2,
            )

            bottom = max(
                y1,
                y2,
            )

            self.world_left = min(
                self.world_left,
                left,
            )

            self.world_top = min(
                self.world_top,
                top,
            )

            self.world_right = max(
                self.world_right,
                right,
            )

            self.world_bottom = max(
                self.world_bottom,
                bottom,
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
            self.world_left
            + half_width
            - collider.offset_x
        )

        right_limit = (
            self.world_right
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
            self.world_bottom
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
            self.world_bottom
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