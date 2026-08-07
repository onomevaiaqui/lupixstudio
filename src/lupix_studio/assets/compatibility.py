from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from PySide6.QtGui import QColor, QImage

from lupix_studio.assets.validator import (
    MAX_COLORS,
    MAX_IMAGE_HEIGHT,
    MAX_IMAGE_WIDTH,
)


class CompatibilityStatus(StrEnum):
    COMPATIBLE = "compatible"
    CONVERSION_REQUIRED = "conversion_required"
    INVALID = "invalid"


@dataclass(slots=True)
class ImageCompatibility:
    path: Path
    width: int
    height: int
    color_count: int
    status: CompatibilityStatus
    reasons: list[str]


def channel_to_5bit(value: int) -> int:
    """Converte um canal de 8 bits para 5 bits."""
    value = max(0, min(255, int(value)))
    return round(value * 31 / 255)


def channel_from_5bit(value: int) -> int:
    """Converte um canal de 5 bits para representação visual de 8 bits."""
    value = max(0, min(31, int(value)))
    return round(value * 255 / 31)


def rgb555_roundtrip(
    red: int,
    green: int,
    blue: int,
) -> tuple[int, int, int]:
    """Simula a redução de uma cor RGB888 para 5 bits por canal."""

    return (
        channel_from_5bit(channel_to_5bit(red)),
        channel_from_5bit(channel_to_5bit(green)),
        channel_from_5bit(channel_to_5bit(blue)),
    )


def analyze_png(path: Path) -> ImageCompatibility:
    """Analisa um PNG quanto à compatibilidade gráfica com o Lupi."""

    path = path.resolve()
    image = QImage(str(path))

    if image.isNull():
        return ImageCompatibility(
            path=path,
            width=0,
            height=0,
            color_count=0,
            status=CompatibilityStatus.INVALID,
            reasons=["Não foi possível carregar a imagem."],
        )

    reasons: list[str] = []

    if (
        image.width() > MAX_IMAGE_WIDTH
        or image.height() > MAX_IMAGE_HEIGHT
    ):
        reasons.append(
            "A imagem excede o limite de 512x512 pixels."
        )

        return ImageCompatibility(
            path=path,
            width=image.width(),
            height=image.height(),
            color_count=0,
            status=CompatibilityStatus.INVALID,
            reasons=reasons,
        )

    colors: set[int] = set()
    requires_rgb555_conversion = False

    for y in range(image.height()):
        for x in range(image.width()):
            pixel = image.pixelColor(x, y)

            rgba_key = pixel.rgba()
            colors.add(rgba_key)

            converted = rgb555_roundtrip(
                pixel.red(),
                pixel.green(),
                pixel.blue(),
            )

            if converted != (
                pixel.red(),
                pixel.green(),
                pixel.blue(),
            ):
                requires_rgb555_conversion = True

    if len(colors) > MAX_COLORS:
        reasons.append(
            "A imagem possui mais de 256 cores."
        )

    if requires_rgb555_conversion:
        reasons.append(
            "Algumas cores serão ajustadas para 5 bits por canal."
        )

    if len(colors) > MAX_COLORS or requires_rgb555_conversion:
        status = CompatibilityStatus.CONVERSION_REQUIRED
    else:
        status = CompatibilityStatus.COMPATIBLE

    return ImageCompatibility(
        path=path,
        width=image.width(),
        height=image.height(),
        color_count=len(colors),
        status=status,
        reasons=reasons,
    )


def create_rgb555_preview(
    source: Path,
) -> QImage:
    """Cria preview visual da redução RGB555 sem alterar o arquivo original."""

    image = QImage(str(source))

    if image.isNull():
        return QImage()

    preview = image.convertToFormat(
        QImage.Format.Format_ARGB32
    )

    for y in range(preview.height()):
        for x in range(preview.width()):
            original = preview.pixelColor(x, y)

            red, green, blue = rgb555_roundtrip(
                original.red(),
                original.green(),
                original.blue(),
            )

            preview.setPixelColor(
                x,
                y,
                QColor(
                    red,
                    green,
                    blue,
                    original.alpha(),
                ),
            )

    return preview