import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

REGISTRY_RELATIVE_PATH = Path("lupix") / "assets.json"


@dataclass(slots=True)
class AssetRecord:
    id: str
    name: str
    type: str
    path: str
    width: int
    height: int
    color_count: int
    compatibility: str


class AssetRegistry:
    """Banco de metadados dos assets do projeto."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.path = self.project_root / REGISTRY_RELATIVE_PATH

    def load(self) -> list[AssetRecord]:
        if not self.path.exists():
            return []

        try:
            raw = json.loads(
                self.path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(raw, list):
            return []

        records: list[AssetRecord] = []

        for item in raw:
            if not isinstance(item, dict):
                continue

            try:
                record = AssetRecord(
                    id=str(item["id"]),
                    name=str(item["name"]),
                    type=str(item["type"]),
                    path=str(item["path"]),
                    width=int(item["width"]),
                    height=int(item["height"]),
                    color_count=int(item["color_count"]),
                    compatibility=str(item["compatibility"]),
                )
            except (KeyError, TypeError, ValueError):
                continue

            records.append(record)

        return records

    def save(
        self,
        records: list[AssetRecord],
    ) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = [
            asdict(record)
            for record in records
        ]

        self.path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def register(
        self,
        *,
        name: str,
        asset_type: str,
        path: Path,
        width: int,
        height: int,
        color_count: int,
        compatibility: str,
    ) -> AssetRecord:
        path = path.resolve()

        relative_path = path.relative_to(
            self.project_root
        ).as_posix()

        records = self.load()

        existing = next(
            (
                record
                for record in records
                if record.path == relative_path
            ),
            None,
        )

        if existing is not None:
            existing.name = name
            existing.type = asset_type
            existing.width = width
            existing.height = height
            existing.color_count = color_count
            existing.compatibility = compatibility

            self.save(records)
            return existing

        record = AssetRecord(
            id=uuid.uuid4().hex,
            name=name,
            type=asset_type,
            path=relative_path,
            width=width,
            height=height,
            color_count=color_count,
            compatibility=compatibility,
        )

        records.append(record)
        self.save(records)

        return record

    def find_by_id(
        self,
        asset_id: str,
    ) -> AssetRecord | None:
        return next(
            (
                record
                for record in self.load()
                if record.id == asset_id
            ),
            None,
        )

    def find_by_path(
        self,
        path: Path,
    ) -> AssetRecord | None:
        relative_path = (
            path.resolve()
            .relative_to(self.project_root)
            .as_posix()
        )

        return next(
            (
                record
                for record in self.load()
                if record.path == relative_path
            ),
            None,
        )