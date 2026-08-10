from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import (
    AssetRecord,
    AssetRegistry,
)
from lupix_studio.tilemap.model import (
    TileLayer,
    TileMapResource,
)
from lupix_studio.tilemap.serializer import (
    TileMapSerializer,
)
from lupix_studio.tileset.serializer import (
    TileSetSerializer,
)


class TilePaletteCanvas(QGraphicsView):
    """Palette visual do TileSet."""

    tile_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(
            self
        )

        self.setScene(
            self.graphics_scene
        )

        self.pixmap_item: (
            QGraphicsPixmapItem | None
        ) = None

        self.tile_width = 16
        self.tile_height = 16

        self.columns = 1
        self.rows = 1

        self.selected_tile: int | None = None

        self.setBackgroundBrush(
            QColor("#151619")
        )

        self.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

    def load_tileset(
        self,
        texture_path: Path,
        tile_width: int,
        tile_height: int,
    ) -> None:
        self.graphics_scene.clear()

        self.pixmap_item = None
        self.selected_tile = None

        self.tile_width = max(
            1,
            int(tile_width),
        )

        self.tile_height = max(
            1,
            int(tile_height),
        )

        pixmap = QPixmap(
            str(texture_path)
        )

        if pixmap.isNull():
            return

        self.pixmap_item = (
            self.graphics_scene.addPixmap(
                pixmap
            )
        )

        self.columns = max(
            1,
            pixmap.width()
            // self.tile_width,
        )

        self.rows = max(
            1,
            pixmap.height()
            // self.tile_height,
        )

        self.graphics_scene.setSceneRect(
            QRectF(
                pixmap.rect()
            )
        )

        self.viewport().update()

    def clear_tileset(self) -> None:
        self.graphics_scene.clear()

        self.pixmap_item = None
        self.selected_tile = None

        self.viewport().update()

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and self.pixmap_item is not None
        ):
            scene_pos = self.mapToScene(
                event.position().toPoint()
            )

            column = int(
                scene_pos.x()
                // self.tile_width
            )

            row = int(
                scene_pos.y()
                // self.tile_height
            )

            if (
                0 <= column < self.columns
                and 0 <= row < self.rows
            ):
                tile_id = (
                    row * self.columns
                    + column
                )

                self.selected_tile = tile_id

                self.tile_selected.emit(
                    tile_id
                )

                self.viewport().update()

        super().mousePressEvent(
            event
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

        grid_pen = QPen(
            QColor(
                255,
                255,
                255,
                70,
            ),
            1,
        )

        grid_pen.setCosmetic(
            True
        )

        painter.setPen(
            grid_pen
        )

        x = 0

        while x <= pixmap.width():
            painter.drawLine(
                QPointF(x, 0),
                QPointF(
                    x,
                    pixmap.height(),
                ),
            )

            x += self.tile_width

        y = 0

        while y <= pixmap.height():
            painter.drawLine(
                QPointF(0, y),
                QPointF(
                    pixmap.width(),
                    y,
                ),
            )

            y += self.tile_height

        if self.selected_tile is None:
            return

        column = (
            self.selected_tile
            % self.columns
        )

        row = (
            self.selected_tile
            // self.columns
        )

        selection_pen = QPen(
            QColor("#ffd34e"),
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
                column * self.tile_width,
                row * self.tile_height,
                self.tile_width,
                self.tile_height,
            )
        )


class TileMapCanvas(QGraphicsView):
    """Canvas interativo do TileMap."""

    map_changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(
            self
        )

        self.setScene(
            self.graphics_scene
        )

        self.resource: TileMapResource | None = None
        self.active_layer_index = 0
        self.selected_tile_id: int | None = None

        self.tileset_pixmap: QPixmap | None = None

        self.tileset_columns = 1

        self._painting = False
        self._erasing = False
        self._last_cell: tuple[int, int] | None = None

        self.setBackgroundBrush(
            QColor("#111216")
        )

        self.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        self.setMouseTracking(
            True
        )

    def set_resource(
        self,
        resource: TileMapResource,
    ) -> None:
        self.resource = resource

        width = (
            resource.width
            * resource.tile_width
        )

        height = (
            resource.height
            * resource.tile_height
        )

        margin = 64

        self.graphics_scene.setSceneRect(
            QRectF(
                -margin,
                -margin,
                width + margin * 2,
                height + margin * 2,
            )
        )

        self.viewport().update()

    def set_tileset(
        self,
        texture_path: Path | None,
    ) -> None:
        if texture_path is None:
            self.tileset_pixmap = None
            self.tileset_columns = 1
            self.viewport().update()
            return

        pixmap = QPixmap(
            str(texture_path)
        )

        if pixmap.isNull():
            self.tileset_pixmap = None
            self.tileset_columns = 1
            self.viewport().update()
            return

        self.tileset_pixmap = pixmap

        if self.resource is not None:
            self.tileset_columns = max(
                1,
                pixmap.width()
                // self.resource.tile_width,
            )

        self.viewport().update()

    def set_active_layer(
        self,
        index: int,
    ) -> None:
        self.active_layer_index = max(
            0,
            index,
        )

        self.viewport().update()

    def set_selected_tile(
        self,
        tile_id: int | None,
    ) -> None:
        self.selected_tile_id = tile_id

    def _active_layer(
        self,
    ) -> TileLayer | None:
        if self.resource is None:
            return None

        return self.resource.layer(
            self.active_layer_index
        )

    def _cell_at_position(
        self,
        event: QMouseEvent,
    ) -> tuple[int, int] | None:
        if self.resource is None:
            return None

        position = self.mapToScene(
            event.position().toPoint()
        )

        if (
            position.x() < 0
            or position.y() < 0
        ):
            return None

        column = int(
            position.x()
            // self.resource.tile_width
        )

        row = int(
            position.y()
            // self.resource.tile_height
        )

        if (
            column < 0
            or row < 0
            or column >= self.resource.width
            or row >= self.resource.height
        ):
            return None

        return (
            column,
            row,
        )

    def _paint_cell(
        self,
        cell: tuple[int, int],
        erase: bool,
    ) -> None:
        layer = self._active_layer()

        if layer is None:
            return

        column, row = cell

        if erase:
            layer.set_tile(
                column,
                row,
                None,
            )

        else:
            if self.selected_tile_id is None:
                return

            layer.set_tile(
                column,
                row,
                self.selected_tile_id,
            )

        self.viewport().update()

        self.map_changed.emit()

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        cell = self._cell_at_position(
            event
        )

        if cell is None:
            super().mousePressEvent(
                event
            )
            return

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self._painting = True
            self._erasing = False

            self._last_cell = cell

            self._paint_cell(
                cell,
                False,
            )

            return

        if (
            event.button()
            == Qt.MouseButton.RightButton
        ):
            self._painting = False
            self._erasing = True

            self._last_cell = cell

            self._paint_cell(
                cell,
                True,
            )

            return

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if not (
            self._painting
            or self._erasing
        ):
            super().mouseMoveEvent(
                event
            )
            return

        cell = self._cell_at_position(
            event
        )

        if (
            cell is None
            or cell == self._last_cell
        ):
            return

        self._last_cell = cell

        self._paint_cell(
            cell,
            self._erasing,
        )

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            self._painting = False
            self._erasing = False
            self._last_cell = None

        super().mouseReleaseEvent(
            event
        )

    def drawBackground(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        painter.fillRect(
            rect,
            QColor("#111216"),
        )

        if self.resource is None:
            return

        map_width = (
            self.resource.width
            * self.resource.tile_width
        )

        map_height = (
            self.resource.height
            * self.resource.tile_height
        )

        map_rect = QRectF(
            0,
            0,
            map_width,
            map_height,
        )

        painter.fillRect(
            map_rect,
            QColor("#202225"),
        )

        self._draw_tiles(
            painter
        )

        grid_pen = QPen(
            QColor(
                255,
                255,
                255,
                45,
            ),
            1,
        )

        grid_pen.setCosmetic(
            True
        )

        painter.setPen(
            grid_pen
        )

        x = 0

        while x <= map_width:
            painter.drawLine(
                QPointF(
                    x,
                    0,
                ),
                QPointF(
                    x,
                    map_height,
                ),
            )

            x += self.resource.tile_width

        y = 0

        while y <= map_height:
            painter.drawLine(
                QPointF(
                    0,
                    y,
                ),
                QPointF(
                    map_width,
                    y,
                ),
            )

            y += self.resource.tile_height

        border_pen = QPen(
            QColor("#8b8e96"),
            1,
        )

        border_pen.setCosmetic(
            True
        )

        painter.setPen(
            border_pen
        )

        painter.drawRect(
            map_rect
        )

    def _draw_tiles(
        self,
        painter: QPainter,
    ) -> None:
        if (
            self.resource is None
            or self.tileset_pixmap is None
        ):
            return

        for layer in self.resource.layers:
            if not layer.visible:
                continue

            painter.save()

            painter.setOpacity(
                layer.opacity
            )

            for key, tile_id in layer.cells.items():
                try:
                    column_text, row_text = (
                        key.split(
                            ",",
                            maxsplit=1,
                        )
                    )

                    column = int(
                        column_text
                    )

                    row = int(
                        row_text
                    )

                except (
                    ValueError,
                    TypeError,
                ):
                    continue

                source_column = (
                    tile_id
                    % self.tileset_columns
                )

                source_row = (
                    tile_id
                    // self.tileset_columns
                )

                source = QRectF(
                    source_column
                    * self.resource.tile_width,
                    source_row
                    * self.resource.tile_height,
                    self.resource.tile_width,
                    self.resource.tile_height,
                )

                destination = QRectF(
                    column
                    * self.resource.tile_width,
                    row
                    * self.resource.tile_height,
                    self.resource.tile_width,
                    self.resource.tile_height,
                )

                painter.drawPixmap(
                    destination,
                    self.tileset_pixmap,
                    source,
                )

            painter.restore()


class TileMapEditor(QWidget):
    """Editor visual de TileMaps."""

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.resource_path: Path | None = None
        self.resource: TileMapResource | None = None

        self.serializer = TileMapSerializer()
        self.tileset_serializer = TileSetSerializer()

        self.selected_tile_id: int | None = None

        self.title = QLabel(
            "Nenhum TileMap aberto"
        )

        self.resource_label = QLabel(
            "-"
        )

        self.resource_label.setWordWrap(
            True
        )

        self.tileset_combo = QComboBox()
        self.layer_list = QListWidget()

        self.tile_info = QLabel(
            "Tile selecionado: nenhum"
        )

        self.tool_info = QLabel(
            "Esquerdo: pintar | Direito: apagar"
        )

        self.save_button = QPushButton(
            "Salvar TileMap"
        )

        self.palette = TilePaletteCanvas()
        self.canvas = TileMapCanvas()

        self.palette.setMinimumHeight(
            180
        )

        form = QFormLayout()

        form.addRow(
            "TileSet:",
            self.tileset_combo,
        )

        left_panel = QWidget()

        left_layout = QVBoxLayout(
            left_panel
        )

        left_layout.addWidget(
            QLabel("Camadas")
        )

        left_layout.addWidget(
            self.layer_list
        )

        left_layout.addSpacing(
            12
        )

        left_layout.addWidget(
            QLabel("Tile Palette")
        )

        left_layout.addWidget(
            self.palette
        )

        left_layout.addWidget(
            self.tile_info
        )

        left_layout.addWidget(
            self.tool_info
        )

        right_panel = QWidget()

        right_layout = QVBoxLayout(
            right_panel
        )

        right_layout.addWidget(
            self.title
        )

        right_layout.addWidget(
            self.resource_label
        )

        right_layout.addLayout(
            form
        )

        right_layout.addWidget(
            self.canvas
        )

        controls = QHBoxLayout()

        controls.addWidget(
            self.save_button
        )

        controls.addStretch()

        right_layout.addLayout(
            controls
        )

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.addWidget(
            left_panel
        )

        splitter.addWidget(
            right_panel
        )

        splitter.setStretchFactor(
            0,
            1,
        )

        splitter.setStretchFactor(
            1,
            4,
        )

        splitter.setSizes(
            [
                300,
                900,
            ]
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            splitter
        )

        self.tileset_combo.currentIndexChanged.connect(
            self._on_tileset_changed
        )

        self.layer_list.currentRowChanged.connect(
            self._on_layer_changed
        )

        self.palette.tile_selected.connect(
            self._on_tile_selected
        )

        self.canvas.map_changed.connect(
            self._on_map_changed
        )

        self.save_button.clicked.connect(
            self.save_resource
        )

    def open_tilemap(
        self,
        project_root: Path,
        resource_path: Path,
    ) -> None:
        self.project_root = (
            project_root.resolve()
        )

        self.resource_path = (
            resource_path.resolve()
        )

        self.resource = (
            self.serializer.load(
                self.resource_path
            )
        )

        self.selected_tile_id = None

        self.title.setText(
            self.resource.name
        )

        self.resource_label.setText(
            str(
                self.resource_path
            )
        )

        self._load_tilesets()
        self._load_layers()

        self.canvas.set_resource(
            self.resource
        )

        self._load_selected_tileset()

    def _load_tilesets(self) -> None:
        self.tileset_combo.blockSignals(
            True
        )

        try:
            self.tileset_combo.clear()

            self.tileset_combo.addItem(
                "Nenhum",
                "",
            )

            if self.project_root is None:
                return

            registry = AssetRegistry(
                self.project_root
            )

            records = [
                record
                for record in registry.load()
                if record.type == "tilesets"
            ]

            for record in records:
                self._add_tileset_record(
                    record
                )

            if (
                self.resource is not None
                and self.resource.tileset_asset_id
            ):
                index = (
                    self.tileset_combo.findData(
                        self.resource.tileset_asset_id
                    )
                )

                if index >= 0:
                    self.tileset_combo.setCurrentIndex(
                        index
                    )

        finally:
            self.tileset_combo.blockSignals(
                False
            )

    def _add_tileset_record(
        self,
        record: AssetRecord,
    ) -> None:
        self.tileset_combo.addItem(
            record.name,
            record.id,
        )

    def _load_layers(self) -> None:
        self.layer_list.clear()

        if self.resource is None:
            return

        for index, layer in enumerate(
            self.resource.layers
        ):
            item = QListWidgetItem(
                layer.name
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                index,
            )

            self.layer_list.addItem(
                item
            )

        if self.layer_list.count() > 0:
            default_row = min(
                1,
                self.layer_list.count() - 1,
            )

            self.layer_list.setCurrentRow(
                default_row
            )

            self.canvas.set_active_layer(
                default_row
            )

    def _on_layer_changed(
        self,
        row: int,
    ) -> None:
        if row < 0:
            return

        self.canvas.set_active_layer(
            row
        )

    def _on_tileset_changed(self) -> None:
        if self.resource is None:
            return

        value = (
            self.tileset_combo.currentData()
        )

        if value:
            self.resource.tileset_asset_id = (
                str(value)
            )
        else:
            self.resource.tileset_asset_id = (
                None
            )

        self.selected_tile_id = None

        self.canvas.set_selected_tile(
            None
        )

        self.tile_info.setText(
            "Tile selecionado: nenhum"
        )

        self._load_selected_tileset()

    def _load_selected_tileset(self) -> None:
        if (
            self.project_root is None
            or self.resource is None
            or not self.resource.tileset_asset_id
        ):
            self.palette.clear_tileset()

            self.canvas.set_tileset(
                None
            )

            return

        registry = AssetRegistry(
            self.project_root
        )

        record = registry.find_by_id(
            self.resource.tileset_asset_id
        )

        if record is None:
            self.palette.clear_tileset()

            self.canvas.set_tileset(
                None
            )

            return

        texture_path = (
            self.project_root
            / record.path
        )

        tile_width = (
            self.resource.tile_width
        )

        tile_height = (
            self.resource.tile_height
        )

        tileset_resource_path = (
            self.project_root
            / "lupix"
            / "tilesets"
            / f"{record.id}.tileset"
        )

        if tileset_resource_path.exists():
            try:
                tileset_resource = (
                    self.tileset_serializer.load(
                        tileset_resource_path
                    )
                )

                tile_width = (
                    tileset_resource.tile_width
                )

                tile_height = (
                    tileset_resource.tile_height
                )

            except (
                OSError,
                ValueError,
                TypeError,
            ):
                pass

        self.resource.tile_width = (
            tile_width
        )

        self.resource.tile_height = (
            tile_height
        )

        self.palette.load_tileset(
            texture_path,
            tile_width,
            tile_height,
        )

        self.canvas.set_resource(
            self.resource
        )

        self.canvas.set_tileset(
            texture_path
        )

    def _on_tile_selected(
        self,
        tile_id: int,
    ) -> None:
        self.selected_tile_id = (
            tile_id
        )

        self.canvas.set_selected_tile(
            tile_id
        )

        columns = (
            self.palette.columns
        )

        column = (
            tile_id
            % columns
        )

        row = (
            tile_id
            // columns
        )

        self.tile_info.setText(
            f"Tile selecionado: {tile_id} "
            f"(col {column}, lin {row})"
        )

    def _on_map_changed(self) -> None:
        self.save_resource()

    def save_resource(self) -> None:
        if (
            self.resource is None
            or self.resource_path is None
        ):
            return

        self.serializer.save(
            self.resource,
            self.resource_path,
        )