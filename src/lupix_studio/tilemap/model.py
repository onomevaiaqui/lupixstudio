from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TileLayer:
    name: str
    visible: bool = True
    opacity: float = 1.0
    cells: dict[str, int] = field(
        default_factory=dict
    )

    def set_tile(
        self,
        column: int,
        row: int,
        tile_id: int | None,
    ) -> None:
        key = f"{column},{row}"

        if tile_id is None or tile_id < 0:
            self.cells.pop(
                key,
                None,
            )
            return

        self.cells[key] = int(
            tile_id
        )

    def tile(
        self,
        column: int,
        row: int,
    ) -> int | None:
        return self.cells.get(
            f"{column},{row}"
        )

    def clear(self) -> None:
        self.cells.clear()

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "visible": self.visible,
            "opacity": self.opacity,
            "cells": dict(
                sorted(
                    self.cells.items()
                )
            ),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> TileLayer:
        raw_cells = data.get(
            "cells",
            {},
        )

        cells: dict[str, int] = {}

        if isinstance(
            raw_cells,
            dict,
        ):
            for key, value in raw_cells.items():
                cells[str(key)] = int(
                    value
                )

        return cls(
            name=str(
                data.get(
                    "name",
                    "",
                )
                or "Layer"
            ),
            visible=bool(
                data.get(
                    "visible",
                    True,
                )
            ),
            opacity=max(
                0.0,
                min(
                    1.0,
                    float(
                        data.get(
                            "opacity",
                            1.0,
                        )
                    ),
                ),
            ),
            cells=cells,
        )


@dataclass(slots=True)
class TileMapResource:
    name: str

    tileset_asset_id: str | None = None

    tile_width: int = 16
    tile_height: int = 16

    width: int = 30
    height: int = 17

    layers: list[TileLayer] = field(
        default_factory=lambda: [
            TileLayer(
                "Background"
            ),
            TileLayer(
                "Ground"
            ),
            TileLayer(
                "Decoration"
            ),
            TileLayer(
                "Collision"
            ),
        ]
    )

    format: int = 1
    type: str = "tilemap"

    def __post_init__(self) -> None:
        if self.tile_width <= 0:
            raise ValueError(
                "A largura do tile deve ser maior que zero."
            )

        if self.tile_height <= 0:
            raise ValueError(
                "A altura do tile deve ser maior que zero."
            )

        if self.width <= 0:
            raise ValueError(
                "A largura do TileMap deve ser maior que zero."
            )

        if self.height <= 0:
            raise ValueError(
                "A altura do TileMap deve ser maior que zero."
            )

        if not self.layers:
            self.layers.append(
                TileLayer(
                    "Ground"
                )
            )

    def layer(
        self,
        index: int,
    ) -> TileLayer | None:
        if (
            index < 0
            or index >= len(self.layers)
        ):
            return None

        return self.layers[index]

    def add_layer(
        self,
        name: str,
    ) -> TileLayer:
        layer = TileLayer(
            name=name
        )

        self.layers.append(
            layer
        )

        return layer

    def remove_layer(
        self,
        index: int,
    ) -> bool:
        if len(self.layers) <= 1:
            return False

        if (
            index < 0
            or index >= len(self.layers)
        ):
            return False

        del self.layers[index]

        return True

    def to_dict(self) -> dict[str, object]:
        return {
            "format": self.format,
            "type": self.type,
            "name": self.name,
            "tileset_asset_id": self.tileset_asset_id,
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
            "width": self.width,
            "height": self.height,
            "layers": [
                layer.to_dict()
                for layer in self.layers
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> TileMapResource:
        raw_layers = data.get(
            "layers",
            [],
        )

        layers: list[TileLayer] = []

        if isinstance(
            raw_layers,
            list,
        ):
            for raw_layer in raw_layers:
                if isinstance(
                    raw_layer,
                    dict,
                ):
                    layers.append(
                        TileLayer.from_dict(
                            raw_layer
                        )
                    )

        tileset_value = data.get(
            "tileset_asset_id"
        )

        tileset_asset_id: str | None

        if tileset_value:
            tileset_asset_id = str(
                tileset_value
            )
        else:
            tileset_asset_id = None

        return cls(
            name=str(
                data.get(
                    "name",
                    "",
                )
                or "TileMap"
            ),
            tileset_asset_id=tileset_asset_id,
            tile_width=int(
                data.get(
                    "tile_width",
                    16,
                )
            ),
            tile_height=int(
                data.get(
                    "tile_height",
                    16,
                )
            ),
            width=int(
                data.get(
                    "width",
                    30,
                )
            ),
            height=int(
                data.get(
                    "height",
                    17,
                )
            ),
            layers=(
                layers
                if layers
                else [
                    TileLayer(
                        "Ground"
                    )
                ]
            ),
            format=int(
                data.get(
                    "format",
                    1,
                )
            ),
            type=str(
                data.get(
                    "type",
                    "tilemap",
                )
            ),
        )