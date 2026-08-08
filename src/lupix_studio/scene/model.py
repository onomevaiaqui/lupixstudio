from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


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
    active: bool = False
    width: int = 480
    height: int = 270
    zoom: float = 1.0

    def to_dict(self) -> dict[str, object]:
        return {
            "active": self.active,
            "width": self.width,
            "height": self.height,
            "zoom": self.zoom,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> CameraComponent:
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
    camera: CameraComponent | None = None

    def refresh_kind(self) -> None:
        if self.camera is not None:
            self.kind = "camera"
            return

        if self.sprite is not None:
            self.kind = "sprite"
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

        if self.camera is not None:
            data["camera"] = (
                self.camera.to_dict()
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

        camera_data = data.get(
            "camera"
        )

        sprite: SpriteComponent | None = None
        camera: CameraComponent | None = None

        if isinstance(
            sprite_data,
            dict,
        ):
            sprite = (
                SpriteComponent.from_dict(
                    sprite_data
                )
            )

        if isinstance(
            camera_data,
            dict,
        ):
            camera = (
                CameraComponent.from_dict(
                    camera_data
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
            camera=camera,
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

    format: int = 3
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
                del self.entities[
                    index
                ]
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

        entities: list[SceneEntity] = []

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
                    1,
                )
            ),
            type=str(
                data.get(
                    "type",
                    "scene",
                )
            ),
        )