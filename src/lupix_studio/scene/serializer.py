from __future__ import annotations

import json
from pathlib import Path

from lupix_studio.scene.model import SceneResource


class SceneSerializer:
    extension = ".scene"

    def save(
        self,
        resource: SceneResource,
        path: Path,
    ) -> Path:
        path = Path(path)

        if path.suffix.lower() != self.extension:
            path = path.with_suffix(
                self.extension
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                resource.to_dict(),
                file,
                indent=2,
                ensure_ascii=False,
            )

        return path

    def load(
        self,
        path: Path,
    ) -> SceneResource:
        path = Path(path)

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Estrutura Scene inválida."
            )

        scene_type = str(data.get("type", "scene") or "scene")

        if scene_type not in {"scene", "interface"}:
            raise ValueError(
                f"Tipo de Scene desconhecido: {scene_type}."
            )

        return SceneResource.from_dict(
            data
        )