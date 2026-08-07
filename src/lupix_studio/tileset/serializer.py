import json
from pathlib import Path

from lupix_studio.tileset.model import TileSetResource


class TileSetSerializer:
    """Salva e carrega recursos TileSet do Lupix Studio."""

    def save(
        self,
        resource: TileSetResource,
        path: Path,
    ) -> Path:
        path = path.resolve()

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
    ) -> TileSetResource:
        path = path.resolve()

        if not path.exists():
            raise FileNotFoundError(path)

        try:
            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                "Arquivo TileSet inválido."
            ) from error

        if not isinstance(data, dict):
            raise TypeError(
                "Estrutura TileSet inválida."
            )

        return TileSetResource.from_dict(
            data
        )