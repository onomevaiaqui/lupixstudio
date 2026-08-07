from dataclasses import dataclass


@dataclass(slots=True)
class TileSetResource:
    name: str
    asset_id: str
    texture: str
    tile_width: int = 16
    tile_height: int = 16
    format: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "format": self.format,
            "type": "tileset",
            "name": self.name,
            "asset_id": self.asset_id,
            "texture": self.texture,
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
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
            format=int(
                data.get("format", 1)
            ),
        )