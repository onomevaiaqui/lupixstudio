from pathlib import Path

from PySide6.QtGui import QImage

from lupix_studio.assets.validator import validate_png


def test_valid_png_has_no_issues(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sprite.png"

    image = QImage(
        32,
        32,
        QImage.Format.Format_ARGB32,
    )

    image.fill(0xFFFFFFFF)

    assert image.save(str(path))

    issues = validate_png(path)

    assert issues == []