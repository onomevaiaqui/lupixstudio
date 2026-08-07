from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRecord
from lupix_studio.tileset.model import TileSetResource
from lupix_studio.tileset.serializer import TileSetSerializer


class TileSetCanvas(QGraphicsView):
    """Canvas pixel-perfect para TileSets."""

    tile_selected = Signal(int, int, int)

    def __init__(self) -> None:
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item: QGraphicsPixmapItem | None = None

        self.tile_width = 16
        self.tile_height = 16

        self.selected_column: int | None = None
        self.selected_row: int | None = None
        self.selected_index: int | None = None

        self.setBackgroundBrush(
            QColor("#151619")
        )

        self.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

    def load_image(
        self,
        path: Path,
    ) -> None:
        self.scene.clear()

        pixmap = QPixmap(
            str(path)
        )

        if pixmap.isNull():
            self.pixmap_item = None
            return

        self.pixmap_item = self.scene.addPixmap(
            pixmap
        )

        self.scene.setSceneRect(
            QRectF(
                pixmap.rect()
            )
        )

        self.clear_selection()

    def clear_selection(self) -> None:
        self.selected_column = None
        self.selected_row = None
        self.selected_index = None

        self.viewport().update()

    def set_grid_size(
        self,
        tile_width: int,
        tile_height: int,
    ) -> None:
        self.tile_width = max(
            1,
            tile_width,
        )

        self.tile_height = max(
            1,
            tile_height,
        )

        self.clear_selection()

    def set_zoom(
        self,
        factor: float,
    ) -> None:
        self.resetTransform()

        self.scale(
            factor,
            factor,
        )

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            scene_pos = self.mapToScene(
                event.position().toPoint()
            )

            self._select_tile_at(
                scene_pos
            )

        super().mousePressEvent(
            event
        )

    def _select_tile_at(
        self,
        scene_pos: QPointF,
    ) -> None:
        if self.pixmap_item is None:
            return

        pixmap = self.pixmap_item.pixmap()

        x = scene_pos.x()
        y = scene_pos.y()

        if (
            x < 0
            or y < 0
            or x >= pixmap.width()
            or y >= pixmap.height()
        ):
            return

        column = int(
            x // self.tile_width
        )

        row = int(
            y // self.tile_height
        )

        columns = max(
            1,
            pixmap.width()
            // self.tile_width,
        )

        tile_index = (
            row * columns
            + column
        )

        self.selected_column = column
        self.selected_row = row
        self.selected_index = tile_index

        self.viewport().update()

        self.tile_selected.emit(
            column,
            row,
            tile_index,
        )

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

        grid_pen = QPen(
            QColor(
                255,
                255,
                255,
                80,
            )
        )

        grid_pen.setCosmetic(
            True
        )

        painter.setPen(
            grid_pen
        )

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

        if (
            self.selected_column is None
            or self.selected_row is None
        ):
            return

        selection_pen = QPen(
            QColor(
                255,
                210,
                60,
            ),
            2,
        )

        selection_pen.setCosmetic(
            True
        )

        painter.setPen(
            selection_pen
        )

        painter.drawRect(
            QRectF(
                self.selected_column
                * self.tile_width,
                self.selected_row
                * self.tile_height,
                self.tile_width,
                self.tile_height,
            )
        )


class TileSetEditor(QWidget):
    """Editor de TileSets persistentes."""

    tile_selected = Signal(int, int, int)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.asset_record: AssetRecord | None = None
        self.resource_path: Path | None = None
        self.resource: TileSetResource | None = None

        self.serializer = TileSetSerializer()

        self.title = QLabel(
            "Nenhum TileSet aberto"
        )

        self.path_label = QLabel(
            "-"
        )

        self.path_label.setWordWrap(
            True
        )

        self.tile_width_spin = QSpinBox()
        self.tile_width_spin.setRange(
            1,
            512,
        )
        self.tile_width_spin.setValue(
            16
        )

        self.tile_height_spin = QSpinBox()
        self.tile_height_spin.setRange(
            1,
            512,
        )
        self.tile_height_spin.setValue(
            16
        )

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

        self.save_button = QPushButton(
            "Salvar TileSet"
        )

        self.column_value = QLabel("-")
        self.row_value = QLabel("-")
        self.index_value = QLabel("-")

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

        controls.addSpacing(
            20
        )

        controls.addWidget(
            QLabel("Zoom:")
        )

        controls.addWidget(
            self.zoom_combo
        )

        controls.addSpacing(
            20
        )

        controls.addWidget(
            self.save_button
        )

        controls.addStretch()

        selection_info = QHBoxLayout()

        selection_info.addWidget(
            QLabel("Coluna:")
        )

        selection_info.addWidget(
            self.column_value
        )

        selection_info.addSpacing(
            12
        )

        selection_info.addWidget(
            QLabel("Linha:")
        )

        selection_info.addWidget(
            self.row_value
        )

        selection_info.addSpacing(
            12
        )

        selection_info.addWidget(
            QLabel("Tile ID:")
        )

        selection_info.addWidget(
            self.index_value
        )

        selection_info.addStretch()

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

        layout.addLayout(
            selection_info
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

        self.save_button.clicked.connect(
            self.save_resource
        )

        self.canvas.tile_selected.connect(
            self._on_tile_selected
        )

        self._update_grid()
        self._update_zoom()

    def open_tileset(
        self,
        project_root: Path,
        asset_record: AssetRecord,
    ) -> None:
        self.project_root = project_root.resolve()
        self.asset_record = asset_record

        texture_path = (
            self.project_root
            / asset_record.path
        )

        self.resource_path = (
            self.project_root
            / "lupix"
            / "tilesets"
            / f"{asset_record.id}.tileset"
        )

        if self.resource_path.exists():
            self.resource = self.serializer.load(
                self.resource_path
            )
        else:
            self.resource = TileSetResource(
                name=asset_record.name,
                asset_id=asset_record.id,
                texture=asset_record.path,
                tile_width=16,
                tile_height=16,
            )

        self.title.setText(
            self.resource.name
        )

        self.path_label.setText(
            self.resource.texture
        )

        self.tile_width_spin.blockSignals(
            True
        )

        self.tile_height_spin.blockSignals(
            True
        )

        self.tile_width_spin.setValue(
            self.resource.tile_width
        )

        self.tile_height_spin.setValue(
            self.resource.tile_height
        )

        self.tile_width_spin.blockSignals(
            False
        )

        self.tile_height_spin.blockSignals(
            False
        )

        self.canvas.load_image(
            texture_path
        )

        self._update_grid()
        self._update_zoom()

    def save_resource(
        self,
    ) -> None:
        if (
            self.resource is None
            or self.resource_path is None
        ):
            return

        self.resource.tile_width = (
            self.tile_width_spin.value()
        )

        self.resource.tile_height = (
            self.tile_height_spin.value()
        )

        self.serializer.save(
            self.resource,
            self.resource_path,
        )

    def _update_grid(
        self,
    ) -> None:
        self.canvas.set_grid_size(
            self.tile_width_spin.value(),
            self.tile_height_spin.value(),
        )

        self.column_value.setText("-")
        self.row_value.setText("-")
        self.index_value.setText("-")

    def _update_zoom(
        self,
    ) -> None:
        factor = float(
            self.zoom_combo.currentData()
        )

        self.canvas.set_zoom(
            factor
        )

    def _on_tile_selected(
        self,
        column: int,
        row: int,
        tile_index: int,
    ) -> None:
        self.column_value.setText(
            str(column)
        )

        self.row_value.setText(
            str(row)
        )

        self.index_value.setText(
            str(tile_index)
        )

        self.tile_selected.emit(
            column,
            row,
            tile_index,
        )