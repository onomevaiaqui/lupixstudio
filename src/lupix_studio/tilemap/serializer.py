from __future__ import annotations

import json
from pathlib import Path

from lupix_studio.tilemap.model import TileMapResource


class TileMapSerializer:
    extension = ".tilemap"

    def save(
        self,
        resource: TileMapResource,
        path: Path,
    ) -> Path:
        path = Path(
            path
        )

        if path.suffix.lower() != self.extension:
            path = path.with_suffix(
                self.extension
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                resource.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return path

    def load(
        self,
        path: Path,
    ) -> TileMapResource:
        path = Path(
            path
        )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Estrutura TileMap inválida."
            )

        if data.get(
            "type"
        ) != "tilemap":
            raise ValueError(
                "O arquivo não contém um TileMap Lupix."
            )

        return TileMapResource.from_dict(
            data
        )