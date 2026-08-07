from dataclasses import dataclass, field


@dataclass(slots=True)
class TilePattern:
    name: str
    column: int
    row: int
    width: int
    height: int

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "column": self.column,
            "row": self.row,
            "width": self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TilePattern":
        return cls(
            name=str(
                data.get("name")
                or "Pattern"
            ),
            column=int(
                data.get("column", 0)
            ),
            row=int(
                data.get("row", 0)
            ),
            width=max(
                1,
                int(data.get("width", 1)),
            ),
            height=max(
                1,
                int(data.get("height", 1)),
            ),
        )


@dataclass(slots=True)
class TileSetResource:
    name: str
    asset_id: str
    texture: str
    tile_width: int = 16
    tile_height: int = 16
    patterns: list[TilePattern] = field(
        default_factory=list
    )
    format: int = 2

    def to_dict(self) -> dict[str, object]:
        return {
            "format": self.format,
            "type": "tileset",
            "name": self.name,
            "asset_id": self.asset_id,
            "texture": self.texture,
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
            "patterns": [
                pattern.to_dict()
                for pattern in self.patterns
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TileSetResource":
        if data.get("type") not in {
            None,
            "tileset",
        }:
            raise ValueError(
                "O arquivo não contém um TileSet Lupix."
            )

        raw_patterns = data.get(
            "patterns",
            [],
        )

        patterns: list[TilePattern] = []

        if isinstance(
            raw_patterns,
            list,
        ):
            for item in raw_patterns:
                if isinstance(
                    item,
                    dict,
                ):
                    patterns.append(
                        TilePattern.from_dict(
                            item
                        )
                    )

        return cls(
            name=str(
                data.get("name")
                or "TileSet"
            ),
            asset_id=str(
                data.get("asset_id")
                or ""
            ),
            texture=str(
                data.get("texture")
                or ""
            ),
            tile_width=int(
                data.get("tile_width", 16)
            ),
            tile_height=int(
                data.get("tile_height", 16)
            ),
            patterns=patterns,
            format=int(
                data.get("format", 1)
            ),
        )