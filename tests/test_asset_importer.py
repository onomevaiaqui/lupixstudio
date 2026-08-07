from pathlib import Path

from PySide6.QtGui import QImage

from lupix_studio.assets.importer import import_png


def test_import_png(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.png"

    image = QImage(
        16,
        16,
        QImage.Format.Format_ARGB32,
    )

    image.fill(0xFFFFFFFF)

    assert image.save(str(source))

    project = tmp_path / "project"

    result = import_png(
        source,
        project,
        "sprites",
    )

    assert result.destination.exists()

    assert (
        result.destination
        == project
        / "assets"
        / "sprites"
        / "source.png"
    )