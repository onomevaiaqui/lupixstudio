from pathlib import Path

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class TileSetCanvas(QGraphicsView):
    """Canvas pixel-perfect para visualização de TileSets."""

    def __init__(self) -> None:
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item: QGraphicsPixmapItem | None = None

        self.tile_width = 16
        self.tile_height = 16
        self.zoom_factor = 1.0

        self.setBackgroundBrush(QColor("#151619"))

        self.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )

    def load_image(self, path: Path) -> None:
        self.scene.clear()

        pixmap = QPixmap(str(path))

        if pixmap.isNull():
            self.pixmap_item = None
            return

        self.pixmap_item = self.scene.addPixmap(pixmap)

        self.scene.setSceneRect(
            QRectF(pixmap.rect())
        )

        self.resetTransform()
        self.zoom_factor = 1.0

        self.viewport().update()

    def set_grid_size(
        self,
        tile_width: int,
        tile_height: int,
    ) -> None:
        self.tile_width = max(1, tile_width)
        self.tile_height = max(1, tile_height)
        self.viewport().update()

    def set_zoom(self, factor: float) -> None:
        self.zoom_factor = factor

        self.resetTransform()
        self.scale(factor, factor)

    def drawForeground(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        super().drawForeground(
            painter,
            rect,
        )

        if self.pixmap_item is None:
            return

        pixmap = self.pixmap_item.pixmap()

        width = pixmap.width()
        height = pixmap.height()

        pen = QPen(
            QColor(255, 255, 255, 80)
        )

        pen.setCosmetic(True)

        painter.setPen(pen)

        x = 0

        while x <= width:
            painter.drawLine(
                QPointF(x, 0),
                QPointF(x, height),
            )

            x += self.tile_width

        y = 0

        while y <= height:
            painter.drawLine(
                QPointF(0, y),
                QPointF(width, y),
            )

            y += self.tile_height


class TileSetEditor(QWidget):
    """Editor inicial de TileSets."""

    def __init__(self) -> None:
        super().__init__()

        self.current_path: Path | None = None

        self.title = QLabel(
            "Nenhum TileSet aberto"
        )

        self.path_label = QLabel("-")
        self.path_label.setWordWrap(True)

        self.tile_width_spin = QSpinBox()
        self.tile_width_spin.setRange(
            1,
            512,
        )
        self.tile_width_spin.setValue(16)

        self.tile_height_spin = QSpinBox()
        self.tile_height_spin.setRange(
            1,
            512,
        )
        self.tile_height_spin.setValue(16)

        self.zoom_combo = QComboBox()

        for label, factor in (
            ("25%", 0.25),
            ("50%", 0.5),
            ("100%", 1.0),
            ("200%", 2.0),
            ("400%", 4.0),
            ("800%", 8.0),
            ("1600%", 16.0),
        ):
            self.zoom_combo.addItem(
                label,
                factor,
            )

        self.zoom_combo.setCurrentText(
            "400%"
        )

        self.canvas = TileSetCanvas()

        controls = QHBoxLayout()

        controls.addWidget(
            QLabel("Tile:")
        )

        controls.addWidget(
            self.tile_width_spin
        )

        controls.addWidget(
            QLabel("×")
        )

        controls.addWidget(
            self.tile_height_spin
        )

        controls.addSpacing(20)

        controls.addWidget(
            QLabel("Zoom:")
        )

        controls.addWidget(
            self.zoom_combo
        )

        controls.addStretch()

        layout = QVBoxLayout(self)

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.path_label
        )

        layout.addLayout(
            controls
        )

        layout.addWidget(
            self.canvas
        )

        self.tile_width_spin.valueChanged.connect(
            self._update_grid
        )

        self.tile_height_spin.valueChanged.connect(
            self._update_grid
        )

        self.zoom_combo.currentIndexChanged.connect(
            self._update_zoom
        )

        self._update_grid()
        self._update_zoom()

    def open_tileset(
        self,
        path: Path,
    ) -> None:
        self.current_path = path.resolve()

        self.title.setText(
            self.current_path.name
        )

        self.path_label.setText(
            str(self.current_path)
        )

        self.canvas.load_image(
            self.current_path
        )

        self._update_grid()
        self._update_zoom()

    def _update_grid(self) -> None:
        self.canvas.set_grid_size(
            self.tile_width_spin.value(),
            self.tile_height_spin.value(),
        )

    def _update_zoom(self) -> None:
        factor = float(
            self.zoom_combo.currentData()
        )

        self.canvas.set_zoom(
            factor
        )