from pathlib import Path

from PySide6.QtGui import QImage

from lupix_studio.assets.importer import import_png
from lupix_studio.assets.registry import AssetRegistry


def test_import_png(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.png"

    image = QImage(
        16,
        16,
        QImage.Format.Format_ARGB32,
    )

    image.fill(
        0xFFFFFFFF
    )

    assert image.save(
        str(source)
    )

    project = (
        tmp_path
        / "project"
    )

    result = import_png(
        source,
        project,
        "sprites",
    )

    assert result.destination.exists()

    assert result.destination == (
        project
        / "assets"
        / "sprites"
        / "source.png"
    )

    assert result.record.id
    assert result.record.type == "sprites"

    registry = AssetRegistry(
        project
    )

    records = registry.load()

    assert len(records) == 1
    assert records[0].id == result.record.id