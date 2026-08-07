import shutil
from dataclasses import dataclass
from pathlib import Path

from lupix_studio.assets.validator import (
    AssetValidationIssue,
    validate_png,
)


@dataclass(slots=True)
class ImportedAsset:
    source: Path
    destination: Path
    asset_type: str
    issues: list[AssetValidationIssue]


def import_png(
    source: Path,
    project_root: Path,
    asset_type: str = "sprites",
) -> ImportedAsset:
    """Importa um PNG para um projeto Lupix."""

    source = source.resolve()
    project_root = project_root.resolve()

    if source.suffix.lower() != ".png":
        raise ValueError("Somente arquivos PNG são suportados nesta etapa.")

    if not source.exists():
        raise FileNotFoundError(source)

    if asset_type not in {"sprites", "tilesets"}:
        raise ValueError("Tipo de asset inválido.")

    destination_dir = (
        project_root
        / "assets"
        / asset_type
    )

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = destination_dir / source.name

    shutil.copy2(
        source,
        destination,
    )

    issues = validate_png(destination)

    return ImportedAsset(
        source=source,
        destination=destination,
        asset_type=asset_type,
        issues=issues,
    )