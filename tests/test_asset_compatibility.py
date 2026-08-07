from pathlib import Path

from PySide6.QtGui import QColor, QImage

from lupix_studio.assets.compatibility import (
    CompatibilityStatus,
    analyze_png,
    rgb555_roundtrip,
)


def test_rgb555_black_and_white() -> None:
    assert rgb555_roundtrip(0, 0, 0) == (0, 0, 0)
    assert rgb555_roundtrip(255, 255, 255) == (255, 255, 255)


def test_compatible_image(
    tmp_path: Path,
) -> None:
    path = tmp_path / "compatible.png"

    image = QImage(
        16,
        16,
        QImage.Format.Format_ARGB32,
    )

    image.fill(
        QColor(255, 255, 255)
    )

    assert image.save(str(path))

    result = analyze_png(path)

    assert result.status == CompatibilityStatus.COMPATIBLE
    assert result.color_count == 1


def test_image_requiring_rgb555_conversion(
    tmp_path: Path,
) -> None:
    path = tmp_path / "conversion.png"

    image = QImage(
        16,
        16,
        QImage.Format.Format_ARGB32,
    )

    image.fill(
        QColor(123, 45, 67)
    )

    assert image.save(str(path))

    result = analyze_png(path)

    assert result.status == CompatibilityStatus.CONVERSION_REQUIRED


def test_oversized_image_is_invalid(
    tmp_path: Path,
) -> None:
    path = tmp_path / "large.png"

    image = QImage(
        513,
        32,
        QImage.Format.Format_ARGB32,
    )

    image.fill(
        QColor(255, 255, 255)
    )

    assert image.save(str(path))

    result = analyze_png(path)

    assert result.status == CompatibilityStatus.INVALID