from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from lupix_studio.animation import AnimationComponent


@dataclass(slots=True)
class Transform2D:
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0

    def to_dict(self) -> dict[str, object]:
        return {
            "position": {
                "x": self.x,
                "y": self.y,
            },
            "rotation": self.rotation,
            "scale": {
                "x": self.scale_x,
                "y": self.scale_y,
            },
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> Transform2D:
        position = data.get(
            "position",
            {},
        )

        scale = data.get(
            "scale",
            {},
        )

        if not isinstance(
            position,
            dict,
        ):
            position = {}

        if not isinstance(
            scale,
            dict,
        ):
            scale = {}

        return cls(
            x=float(
                position.get(
                    "x",
                    0.0,
                )
            ),
            y=float(
                position.get(
                    "y",
                    0.0,
                )
            ),
            rotation=float(
                data.get(
                    "rotation",
                    0.0,
                )
            ),
            scale_x=float(
                scale.get(
                    "x",
                    1.0,
                )
            ),
            scale_y=float(
                scale.get(
                    "y",
                    1.0,
                )
            ),
        )


@dataclass(slots=True)
class SpriteComponent:
    asset_id: str = ""
    opacity: float = 1.0
    flip_x: bool = False
    flip_y: bool = False
    layer: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "opacity": self.opacity,
            "flip_x": self.flip_x,
            "flip_y": self.flip_y,
            "layer": self.layer,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> SpriteComponent:
        return cls(
            asset_id=str(
                data.get(
                    "asset_id",
                    "",
                )
                or ""
            ),
            opacity=float(
                data.get(
                    "opacity",
                    1.0,
                )
            ),
            flip_x=bool(
                data.get(
                    "flip_x",
                    False,
                )
            ),
            flip_y=bool(
                data.get(
                    "flip_y",
                    False,
                )
            ),
            layer=int(
                data.get(
                    "layer",
                    0,
                )
            ),
        )


@dataclass(slots=True)
class CameraComponent:
    """Camera 2D associada à própria entidade."""

    active: bool = False

    # Área lógica visível antes do zoom.
    width: int = 480
    height: int = 270

    zoom: float = 1.0

    # Deslocamento da câmera em relação ao Transform
    # da entidade que possui o componente.
    offset_x: float = 0.0
    offset_y: float = 0.0

    # Limita a câmera ao mundo/fase.
    limit_to_scene: bool = True

    # Limites personalizados opcionais.
    custom_limits_enabled: bool = False
    limit_left: float = 0.0
    limit_top: float = 0.0
    limit_right: float = 480.0
    limit_bottom: float = 270.0

    # Dead Zone: o alvo pode se mover dentro desta área
    # sem deslocar imediatamente a câmera.
    dead_zone_enabled: bool = False
    dead_zone_width: float = 80.0
    dead_zone_height: float = 50.0

    # Suavização do acompanhamento.
    smoothing_enabled: bool = False
    smoothing_speed: float = 5.0

    def to_dict(self) -> dict[str, object]:
        return {
            "active": self.active,
            "width": self.width,
            "height": self.height,
            "zoom": self.zoom,
            "offset": {
                "x": self.offset_x,
                "y": self.offset_y,
            },
            "limit_to_scene": self.limit_to_scene,
            "limits": {
                "custom_enabled": (
                    self.custom_limits_enabled
                ),
                "left": self.limit_left,
                "top": self.limit_top,
                "right": self.limit_right,
                "bottom": self.limit_bottom,
            },
            "dead_zone": {
                "enabled": self.dead_zone_enabled,
                "width": self.dead_zone_width,
                "height": self.dead_zone_height,
            },
            "smoothing": {
                "enabled": self.smoothing_enabled,
                "speed": self.smoothing_speed,
            },
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> CameraComponent:
        offset = data.get(
            "offset",
            {},
        )

        if not isinstance(
            offset,
            dict,
        ):
            offset = {}

        limits = data.get(
            "limits",
            {},
        )

        if not isinstance(
            limits,
            dict,
        ):
            limits = {}

        dead_zone = data.get(
            "dead_zone",
            {},
        )

        if not isinstance(
            dead_zone,
            dict,
        ):
            dead_zone = {}

        smoothing = data.get(
            "smoothing",
            {},
        )

        if not isinstance(
            smoothing,
            dict,
        ):
            smoothing = {}

        return cls(
            active=bool(
                data.get(
                    "active",
                    False,
                )
            ),
            width=max(
                1,
                int(
                    data.get(
                        "width",
                        480,
                    )
                ),
            ),
            height=max(
                1,
                int(
                    data.get(
                        "height",
                        270,
                    )
                ),
            ),
            zoom=max(
                0.01,
                float(
                    data.get(
                        "zoom",
                        1.0,
                    )
                ),
            ),
            offset_x=float(
                offset.get(
                    "x",
                    0.0,
                )
            ),
            offset_y=float(
                offset.get(
                    "y",
                    0.0,
                )
            ),
            limit_to_scene=bool(
                data.get(
                    "limit_to_scene",
                    True,
                )
            ),
            custom_limits_enabled=bool(
                limits.get(
                    "custom_enabled",
                    False,
                )
            ),
            limit_left=float(
                limits.get(
                    "left",
                    0.0,
                )
            ),
            limit_top=float(
                limits.get(
                    "top",
                    0.0,
                )
            ),
            limit_right=float(
                limits.get(
                    "right",
                    data.get(
                        "width",
                        480,
                    ),
                )
            ),
            limit_bottom=float(
                limits.get(
                    "bottom",
                    data.get(
                        "height",
                        270,
                    ),
                )
            ),
            dead_zone_enabled=bool(
                dead_zone.get(
                    "enabled",
                    False,
                )
            ),
            dead_zone_width=max(
                0.0,
                float(
                    dead_zone.get(
                        "width",
                        80.0,
                    )
                ),
            ),
            dead_zone_height=max(
                0.0,
                float(
                    dead_zone.get(
                        "height",
                        50.0,
                    )
                ),
            ),
            smoothing_enabled=bool(
                smoothing.get(
                    "enabled",
                    False,
                )
            ),
            smoothing_speed=max(
                0.01,
                float(
                    smoothing.get(
                        "speed",
                        5.0,
                    )
                ),
            ),
        )


@dataclass(slots=True)
class TileMapComponent:
    resource_path: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "resource_path": self.resource_path,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> TileMapComponent:
        return cls(
            resource_path=str(
                data.get(
                    "resource_path",
                    "",
                )
                or ""
            ),
        )


@dataclass(slots=True)
class ColliderComponent:
    enabled: bool = True
    width: float = 16.0
    height: float = 16.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    solid: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "width": self.width,
            "height": self.height,
            "offset": {
                "x": self.offset_x,
                "y": self.offset_y,
            },
            "solid": self.solid,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> ColliderComponent:
        offset = data.get(
            "offset",
            {},
        )

        if not isinstance(
            offset,
            dict,
        ):
            offset = {}

        return cls(
            enabled=bool(
                data.get(
                    "enabled",
                    True,
                )
            ),
            width=max(
                0.01,
                float(
                    data.get(
                        "width",
                        16.0,
                    )
                ),
            ),
            height=max(
                0.01,
                float(
                    data.get(
                        "height",
                        16.0,
                    )
                ),
            ),
            offset_x=float(
                offset.get(
                    "x",
                    0.0,
                )
            ),
            offset_y=float(
                offset.get(
                    "y",
                    0.0,
                )
            ),
            solid=bool(
                data.get(
                    "solid",
                    True,
                )
            ),
        )


@dataclass(slots=True)
class PlayerControllerComponent:
    enabled: bool = True
    speed: float = 80.0
    jump_force: float = 220.0
    gravity: float = 600.0
    max_fall_speed: float = 500.0
    air_control: float = 0.75

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "speed": self.speed,
            "jump_force": self.jump_force,
            "gravity": self.gravity,
            "max_fall_speed": self.max_fall_speed,
            "air_control": self.air_control,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> PlayerControllerComponent:
        return cls(
            enabled=bool(
                data.get(
                    "enabled",
                    True,
                )
            ),
            speed=max(
                0.0,
                float(
                    data.get(
                        "speed",
                        80.0,
                    )
                ),
            ),
            jump_force=max(
                0.0,
                float(
                    data.get(
                        "jump_force",
                        220.0,
                    )
                ),
            ),
            gravity=max(
                0.0,
                float(
                    data.get(
                        "gravity",
                        600.0,
                    )
                ),
            ),
            max_fall_speed=max(
                0.0,
                float(
                    data.get(
                        "max_fall_speed",
                        500.0,
                    )
                ),
            ),
            air_control=max(
                0.0,
                min(
                    1.0,
                    float(
                        data.get(
                            "air_control",
                            0.75,
                        )
                    ),
                ),
            ),
        )


@dataclass(slots=True)
class SceneEntity:
    name: str

    id: str = field(
        default_factory=lambda: uuid4().hex
    )

    kind: str = "empty"

    transform: Transform2D = field(
        default_factory=Transform2D
    )

    sprite: SpriteComponent | None = None
    animation: AnimationComponent | None = None
    camera: CameraComponent | None = None
    tilemap: TileMapComponent | None = None
    collider: ColliderComponent | None = None
    player_controller: PlayerControllerComponent | None = None

    def refresh_kind(self) -> None:
        if self.tilemap is not None:
            self.kind = "tilemap"
            return

        if self.camera is not None:
            self.kind = "camera"
            return

        if self.sprite is not None:
            self.kind = "sprite"
            return

        if self.collider is not None:
            self.kind = "collider"
            return

        if self.player_controller is not None:
            self.kind = "player"
            return

        self.kind = "empty"

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "transform": self.transform.to_dict(),
        }

        if self.sprite is not None:
            data["sprite"] = (
                self.sprite.to_dict()
            )

        if self.animation is not None:
            data["animation"] = (
                self.animation.to_dict()
            )

        if self.camera is not None:
            data["camera"] = (
                self.camera.to_dict()
            )

        if self.tilemap is not None:
            data["tilemap"] = (
                self.tilemap.to_dict()
            )

        if self.collider is not None:
            data["collider"] = (
                self.collider.to_dict()
            )

        if self.player_controller is not None:
            data["player_controller"] = (
                self.player_controller.to_dict()
            )

        return data

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> SceneEntity:
        transform_data = data.get(
            "transform",
            {},
        )

        if not isinstance(
            transform_data,
            dict,
        ):
            transform_data = {}

        sprite_data = data.get(
            "sprite"
        )

        animation_data = data.get(
            "animation"
        )

        camera_data = data.get(
            "camera"
        )

        tilemap_data = data.get(
            "tilemap"
        )

        collider_data = data.get(
            "collider"
        )

        controller_data = data.get(
            "player_controller"
        )

        sprite: SpriteComponent | None = None
        animation: AnimationComponent | None = None
        camera: CameraComponent | None = None
        tilemap: TileMapComponent | None = None
        collider: ColliderComponent | None = None
        player_controller: PlayerControllerComponent | None = None

        if isinstance(
            sprite_data,
            dict,
        ):
            sprite = SpriteComponent.from_dict(
                sprite_data
            )

        if isinstance(
            animation_data,
            dict,
        ):
            animation = (
                AnimationComponent.from_dict(
                    animation_data
                )
            )

        if isinstance(
            camera_data,
            dict,
        ):
            camera = CameraComponent.from_dict(
                camera_data
            )

        if isinstance(
            tilemap_data,
            dict,
        ):
            tilemap = TileMapComponent.from_dict(
                tilemap_data
            )

        if isinstance(
            collider_data,
            dict,
        ):
            collider = ColliderComponent.from_dict(
                collider_data
            )

        if isinstance(
            controller_data,
            dict,
        ):
            player_controller = (
                PlayerControllerComponent.from_dict(
                    controller_data
                )
            )

        entity = cls(
            id=str(
                data.get(
                    "id",
                    "",
                )
                or uuid4().hex
            ),
            name=str(
                data.get(
                    "name",
                    "",
                )
                or "Entity"
            ),
            kind=str(
                data.get(
                    "kind",
                    "",
                )
                or "empty"
            ),
            transform=Transform2D.from_dict(
                transform_data
            ),
            sprite=sprite,
            animation=animation,
            camera=camera,
            tilemap=tilemap,
            collider=collider,
            player_controller=player_controller,
        )

        entity.refresh_kind()

        return entity


@dataclass(slots=True)
class SceneResource:
    name: str
    width: int = 480
    height: int = 270

    entities: list[SceneEntity] = field(
        default_factory=list
    )

    format: int = 7
    type: str = "scene"

    def add_entity(
        self,
        entity: SceneEntity,
    ) -> None:
        self.entities.append(
            entity
        )

    def remove_entity(
        self,
        entity_id: str,
    ) -> bool:
        for index, entity in enumerate(
            self.entities
        ):
            if entity.id == entity_id:
                del self.entities[index]
                return True

        return False

    def entity(
        self,
        entity_id: str,
    ) -> SceneEntity | None:
        for entity in self.entities:
            if entity.id == entity_id:
                return entity

        return None

    def active_camera(
        self,
    ) -> SceneEntity | None:
        for entity in self.entities:
            if (
                entity.camera is not None
                and entity.camera.active
            ):
                return entity

        return None

    def activate_camera(
        self,
        entity_id: str,
    ) -> None:
        for entity in self.entities:
            if entity.camera is None:
                continue

            entity.camera.active = (
                entity.id == entity_id
            )

    def player_entity(
        self,
    ) -> SceneEntity | None:
        for entity in self.entities:
            if (
                entity.player_controller is not None
                and entity.player_controller.enabled
            ):
                return entity

        return None

    def to_dict(self) -> dict[str, object]:
        return {
            "format": self.format,
            "type": self.type,
            "name": self.name,
            "resolution": {
                "width": self.width,
                "height": self.height,
            },
            "entities": [
                entity.to_dict()
                for entity in self.entities
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> SceneResource:
        resolution = data.get(
            "resolution",
            {},
        )

        if not isinstance(
            resolution,
            dict,
        ):
            resolution = {}

        raw_entities = data.get(
            "entities",
            [],
        )

        entities: list[
            SceneEntity
        ] = []

        if isinstance(
            raw_entities,
            list,
        ):
            for raw_entity in raw_entities:
                if not isinstance(
                    raw_entity,
                    dict,
                ):
                    continue

                entities.append(
                    SceneEntity.from_dict(
                        raw_entity
                    )
                )

        return cls(
            name=str(
                data.get(
                    "name",
                    "",
                )
                or "Scene"
            ),
            width=max(
                1,
                int(
                    resolution.get(
                        "width",
                        480,
                    )
                ),
            ),
            height=max(
                1,
                int(
                    resolution.get(
                        "height",
                        270,
                    )
                ),
            ),
            entities=entities,
            format=int(
                data.get(
                    "format",
                    7,
                )
            ),
            type=str(
                data.get(
                    "type",
                    "scene",
                )
            ),
        )