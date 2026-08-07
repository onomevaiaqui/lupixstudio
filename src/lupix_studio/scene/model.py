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
        position = data.get("position", {})
        scale = data.get("scale", {})

        if not isinstance(position, dict):
            position = {}

        if not isinstance(scale, dict):
            scale = {}

        return cls(
            x=float(position.get("x", 0.0)),
            y=float(position.get("y", 0.0)),
            rotation=float(data.get("rotation", 0.0)),
            scale_x=float(scale.get("x", 1.0)),
            scale_y=float(scale.get("y", 1.0)),
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

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "transform": self.transform.to_dict(),
        }

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

        return cls(
            id=str(
                data.get("id")
                or uuid4().hex
            ),
            name=str(
                data.get("name")
                or "Entity"
            ),
            kind=str(
                data.get("kind")
                or "empty"
            ),
            transform=Transform2D.from_dict(
                transform_data
            ),
        )


@dataclass(slots=True)
class SceneResource:
    name: str

    width: int = 480
    height: int = 270

    entities: list[SceneEntity] = field(
        default_factory=list
    )

    format: int = 1
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
                if isinstance(
                    raw_entity,
                    dict,
                ):
                    entities.append(
                        SceneEntity.from_dict(
                            raw_entity
                        )
                    )

        return cls(
            name=str(
                data.get("name")
                or "Scene"
            ),
            width=int(
                resolution.get(
                    "width",
                    480,
                )
            ),
            height=int(
                resolution.get(
                    "height",
                    270,
                )
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