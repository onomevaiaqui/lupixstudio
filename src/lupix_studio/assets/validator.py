from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QImage

MAX_IMAGE_WIDTH = 512
MAX_IMAGE_HEIGHT = 512
MAX_COLORS = 256


@dataclass(slots=True)
class AssetValidationIssue:
    level: str
    message: str


def validate_png(path: Path) -> list[AssetValidationIssue]:
    """Valida um PNG contra os limites básicos do Lupi."""

    issues: list[AssetValidationIssue] = []

    image = QImage(str(path))

    if image.isNull():
        return [
            AssetValidationIssue(
                level="error",
                message="Não foi possível carregar a imagem.",
            )
        ]

    if image.width() > MAX_IMAGE_WIDTH or image.height() > MAX_IMAGE_HEIGHT:
        issues.append(
            AssetValidationIssue(
                level="error",
                message=(
                    "A imagem excede o limite de 512x512 pixels do Lupi."
                ),
            )
        )

    colors: set[int] = set()

    for y in range(image.height()):
        for x in range(image.width()):
            colors.add(image.pixel(x, y))

            if len(colors) > MAX_COLORS:
                issues.append(
                    AssetValidationIssue(
                        level="warning",
                        message=(
                            "A imagem possui mais de 256 cores "
                            "e precisará ser convertida."
                        ),
                    )
                )
                return issues

    return issues