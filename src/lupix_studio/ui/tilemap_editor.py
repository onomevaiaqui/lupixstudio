from __future__ import annotations

from collections import deque
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, Signal
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
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import (
    AssetRecord,
    AssetRegistry,
)
from lupix_studio.project.loader import load_project
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

    def select_tile(
        self,
        tile_id: int,
    ) -> None:
        maximum = (
            self.columns
            * self.rows
        )

        if not (
            0 <= tile_id < maximum
        ):
            return

        self.selected_tile = tile_id
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
                QPointF(
                    x,
                    0,
                ),
                QPointF(
                    x,
                    pixmap.height(),
                ),
            )

            x += self.tile_width

        y = 0

        while y <= pixmap.height():
            painter.drawLine(
                QPointF(
                    0,
                    y,
                ),
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
    tile_picked = Signal(int)
    cursor_cell_changed = Signal(int, int)

    TOOL_BRUSH = "brush"
    TOOL_ERASER = "eraser"
    TOOL_FILL = "fill"
    TOOL_EYEDROPPER = "eyedropper"

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(
            self
        )

        self.setScene(
            self.graphics_scene
        )

        self.resource: TileMapResource | None = None

        self.output_width = 480
        self.output_height = 270

        self.workspace_columns = 512
        self.workspace_rows = 256

        self.active_layer_index = 0
        self.selected_tile_id: int | None = None

        self.tileset_pixmap: QPixmap | None = None
        self.tileset_columns = 1

        self.active_tool = self.TOOL_BRUSH

        self._painting = False
        self._erasing = False
        self._last_cell: tuple[int, int] | None = None

        self._panning = False
        self._pan_start = QPoint()

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

        self._update_workspace_rect()

        self.viewport().update()

    def set_output_size(
        self,
        width: int,
        height: int,
    ) -> None:
        self.output_width = max(
            1,
            int(width),
        )

        self.output_height = max(
            1,
            int(height),
        )

        self._update_workspace_rect()
        self.viewport().update()

    def _update_workspace_rect(
        self,
    ) -> None:
        if self.resource is None:
            return

        tile_width = max(
            1,
            self.resource.tile_width,
        )

        tile_height = max(
            1,
            self.resource.tile_height,
        )

        used_width = max(
            self.resource.width
            * tile_width,
            self.output_width,
        )

        used_height = max(
            self.resource.height
            * tile_height,
            self.output_height,
        )

        workspace_width = max(
            self.workspace_columns
            * tile_width,
            self.output_width * 4,
            used_width + 2048,
        )

        workspace_height = max(
            self.workspace_rows
            * tile_height,
            self.output_height * 4,
            used_height + 1024,
        )

        self.graphics_scene.setSceneRect(
            QRectF(
                -1024,
                -1024,
                workspace_width + 2048,
                workspace_height + 2048,
            )
        )

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

    def set_tool(
        self,
        tool: str,
    ) -> None:
        if tool not in {
            self.TOOL_BRUSH,
            self.TOOL_ERASER,
            self.TOOL_FILL,
            self.TOOL_EYEDROPPER,
        }:
            return

        self.active_tool = tool

    def set_zoom(
        self,
        factor: float,
    ) -> None:
        self.resetTransform()

        self.scale(
            factor,
            factor,
        )

    def fit_map(self) -> None:
        if self.resource is None:
            return

        output_rect = QRectF(
            0,
            0,
            self.output_width,
            self.output_height,
        )

        self.fitInView(
            output_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def _active_layer(
        self,
    ) -> TileLayer | None:
        if self.resource is None:
            return None

        return self.resource.layer(
            self.active_layer_index
        )

    def _cell_from_view_position(
        self,
        position: QPoint,
    ) -> tuple[int, int] | None:
        if self.resource is None:
            return None

        scene_position = self.mapToScene(
            position
        )

        if (
            scene_position.x() < 0
            or scene_position.y() < 0
        ):
            return None

        column = int(
            scene_position.x()
            // self.resource.tile_width
        )

        row = int(
            scene_position.y()
            // self.resource.tile_height
        )

        if (
            column < 0
            or row < 0
            or column >= self.workspace_columns
            or row >= self.workspace_rows
        ):
            return None

        return (
            column,
            row,
        )

    def _cell_at_event(
        self,
        event: QMouseEvent,
    ) -> tuple[int, int] | None:
        return self._cell_from_view_position(
            event.position().toPoint()
        )

    def _paint_cell(
        self,
        cell: tuple[int, int],
        erase: bool,
    ) -> bool:
        layer = self._active_layer()

        if layer is None:
            return False

        column, row = cell

        if not erase:
            self._ensure_resource_contains(
                column,
                row,
            )

        if erase:
            previous = layer.tile(
                column,
                row,
            )

            if previous is None:
                return False

            layer.set_tile(
                column,
                row,
                None,
            )

        else:
            is_collision_layer = (
                layer.name.strip().lower()
                == "collision"
            )

            if is_collision_layer:
                tile_id = 0

            else:
                if self.selected_tile_id is None:
                    return False

                tile_id = self.selected_tile_id

            previous = layer.tile(
                column,
                row,
            )

            if previous == tile_id:
                return False

            layer.set_tile(
                column,
                row,
                tile_id,
            )

        self.viewport().update()

        return True

    def _ensure_resource_contains(
        self,
        column: int,
        row: int,
    ) -> None:
        if self.resource is None:
            return

        changed = False

        if column >= self.resource.width:
            self.resource.width = (
                column + 1
            )
            changed = True

        if row >= self.resource.height:
            self.resource.height = (
                row + 1
            )
            changed = True

        if changed:
            self._update_workspace_rect()

    def _fill_cell(
        self,
        start: tuple[int, int],
    ) -> None:
        if self.resource is None:
            return

        layer = self._active_layer()

        if layer is None:
            return

        is_collision_layer = (
            layer.name.strip().lower()
            == "collision"
        )

        if is_collision_layer:
            replacement_tile = 0

        else:
            if self.selected_tile_id is None:
                return

            replacement_tile = (
                self.selected_tile_id
            )

        start_column, start_row = start

        target_tile = layer.tile(
            start_column,
            start_row,
        )

        if target_tile == replacement_tile:
            return

        queue: deque[
            tuple[int, int]
        ] = deque(
            [start]
        )

        visited: set[
            tuple[int, int]
        ] = set()

        changed = False

        while queue:
            column, row = queue.popleft()

            if (
                column,
                row,
            ) in visited:
                continue

            visited.add(
                (
                    column,
                    row,
                )
            )

            if (
                column < 0
                or row < 0
                or column >= self.resource.width
                or row >= self.resource.height
            ):
                continue

            current_tile = layer.tile(
                column,
                row,
            )

            if current_tile != target_tile:
                continue

            layer.set_tile(
                column,
                row,
                replacement_tile,
            )

            changed = True

            queue.append(
                (
                    column + 1,
                    row,
                )
            )

            queue.append(
                (
                    column - 1,
                    row,
                )
            )

            queue.append(
                (
                    column,
                    row + 1,
                )
            )

            queue.append(
                (
                    column,
                    row - 1,
                )
            )

        if changed:
            self.viewport().update()
            self.map_changed.emit()

    def _pick_tile(
        self,
        cell: tuple[int, int],
    ) -> None:
        layer = self._active_layer()

        if layer is None:
            return

        column, row = cell

        tile_id = layer.tile(
            column,
            row,
        )

        if tile_id is None:
            return

        self.selected_tile_id = tile_id

        self.tile_picked.emit(
            tile_id
        )

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.MiddleButton
        ):
            self._panning = True

            self._pan_start = (
                event.position().toPoint()
            )

            self.setCursor(
                Qt.CursorShape.ClosedHandCursor
            )

            event.accept()
            return

        cell = self._cell_at_event(
            event
        )

        if cell is None:
            super().mousePressEvent(
                event
            )
            return

        if (
            event.button()
            == Qt.MouseButton.RightButton
        ):
            if self._paint_cell(
                cell,
                True,
            ):
                self.map_changed.emit()

            self._erasing = True
            self._painting = False
            self._last_cell = cell

            return

        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            super().mousePressEvent(
                event
            )
            return

        if (
            self.active_tool
            == self.TOOL_BRUSH
        ):
            if self._paint_cell(
                cell,
                False,
            ):
                self.map_changed.emit()

            self._painting = True
            self._erasing = False
            self._last_cell = cell

            return

        if (
            self.active_tool
            == self.TOOL_ERASER
        ):
            if self._paint_cell(
                cell,
                True,
            ):
                self.map_changed.emit()

            self._painting = False
            self._erasing = True
            self._last_cell = cell

            return

        if (
            self.active_tool
            == self.TOOL_FILL
        ):
            self._fill_cell(
                cell
            )
            return

        if (
            self.active_tool
            == self.TOOL_EYEDROPPER
        ):
            self._pick_tile(
                cell
            )
            return

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if self._panning:
            current = (
                event.position().toPoint()
            )

            delta = (
                current
                - self._pan_start
            )

            self._pan_start = current

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value()
                - delta.x()
            )

            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value()
                - delta.y()
            )

            event.accept()
            return

        cell = self._cell_at_event(
            event
        )

        if cell is not None:
            self.cursor_cell_changed.emit(
                cell[0],
                cell[1],
            )

        if not (
            self._painting
            or self._erasing
        ):
            super().mouseMoveEvent(
                event
            )
            return

        if (
            cell is None
            or cell == self._last_cell
        ):
            return

        self._last_cell = cell

        if self._paint_cell(
            cell,
            self._erasing,
        ):
            self.map_changed.emit()

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.MiddleButton
        ):
            self._panning = False

            self.unsetCursor()

            event.accept()
            return

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

        workspace = (
            self.graphics_scene.sceneRect()
        )

        painter.fillRect(
            workspace,
            QColor("#202225"),
        )

        self._draw_tiles(
            painter
        )

        visible = rect.intersected(
            workspace
        )

        tile_width = max(
            1,
            self.resource.tile_width,
        )

        tile_height = max(
            1,
            self.resource.tile_height,
        )

        grid_pen = QPen(
            QColor(
                255,
                255,
                255,
                85,
            ),
            1,
        )

        grid_pen.setCosmetic(
            True
        )

        painter.setPen(
            grid_pen
        )

        first_column = max(
            0,
            int(
                visible.left()
                // tile_width
            ),
        )

        last_column = min(
            self.workspace_columns,
            int(
                visible.right()
                // tile_width
            ) + 1,
        )

        first_row = max(
            0,
            int(
                visible.top()
                // tile_height
            ),
        )

        last_row = min(
            self.workspace_rows,
            int(
                visible.bottom()
                // tile_height
            ) + 1,
        )

        top = 0.0
        bottom = (
            self.workspace_rows
            * tile_height
        )

        left = 0.0
        right = (
            self.workspace_columns
            * tile_width
        )

        for column in range(
            first_column,
            last_column + 1,
        ):
            x = (
                column
                * tile_width
            )

            painter.drawLine(
                QPointF(
                    x,
                    top,
                ),
                QPointF(
                    x,
                    bottom,
                ),
            )

        for row in range(
            first_row,
            last_row + 1,
        ):
            y = (
                row
                * tile_height
            )

            painter.drawLine(
                QPointF(
                    left,
                    y,
                ),
                QPointF(
                    right,
                    y,
                ),
            )

        output_rect = QRectF(
            0,
            0,
            self.output_width,
            self.output_height,
        )

        output_pen = QPen(
            QColor(
                93,
                209,
                255,
                220,
            ),
            2,
        )

        output_pen.setCosmetic(
            True
        )

        painter.setPen(
            output_pen
        )

        painter.drawRect(
            output_rect
        )

        used_rect = QRectF(
            0,
            0,
            self.resource.width
            * tile_width,
            self.resource.height
            * tile_height,
        )

        used_pen = QPen(
            QColor(
                235,
                196,
                85,
                120,
            ),
            1,
            Qt.PenStyle.DashLine,
        )

        used_pen.setCosmetic(
            True
        )

        painter.setPen(
            used_pen
        )

        painter.drawRect(
            used_rect
        )


    def _draw_tiles(
        self,
        painter: QPainter,
    ) -> None:
        if self.resource is None:
            return

        for layer in self.resource.layers:
            if not layer.visible:
                continue

            is_collision_layer = (
                layer.name.strip().lower()
                == "collision"
            )

            painter.save()

            if is_collision_layer:
                self._draw_collision_layer(
                    painter,
                    layer,
                )

                painter.restore()
                continue

            if self.tileset_pixmap is None:
                painter.restore()
                continue

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
                    AttributeError,
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

    def _draw_collision_layer(
        self,
        painter: QPainter,
        layer: TileLayer,
    ) -> None:
        if self.resource is None:
            return

        fill = QColor(
            255,
            70,
            70,
            90,
        )

        border = QPen(
            QColor(
                255,
                100,
                100,
                210,
            ),
            1,
        )

        border.setCosmetic(
            True
        )

        painter.setPen(
            border
        )

        painter.setBrush(
            fill
        )

        for key in layer.cells:
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
                AttributeError,
            ):
                continue

            rect = QRectF(
                column
                * self.resource.tile_width,
                row
                * self.resource.tile_height,
                self.resource.tile_width,
                self.resource.tile_height,
            )

            painter.drawRect(
                rect
            )


class TileMapEditor(QWidget):
    """Editor visual de TileMaps."""

    back_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.resource_path: Path | None = None
        self.resource: TileMapResource | None = None

        self.serializer = TileMapSerializer()
        self.tileset_serializer = TileSetSerializer()

        self.selected_tile_id: int | None = None

        self.back_button = QPushButton(
            "← Voltar para Cena"
        )

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

        self.cursor_info = QLabel(
            "Célula: -"
        )

        self.save_button = QPushButton(
            "Salvar TileMap"
        )

        self.palette = TilePaletteCanvas()
        self.canvas = TileMapCanvas()

        self.palette.setMinimumHeight(
            180
        )

        self.brush_button = QToolButton()
        self.brush_button.setText(
            "Pincel"
        )
        self.brush_button.setCheckable(
            True
        )
        self.brush_button.setChecked(
            True
        )

        self.eraser_button = QToolButton()
        self.eraser_button.setText(
            "Borracha"
        )
        self.eraser_button.setCheckable(
            True
        )

        self.fill_button = QToolButton()
        self.fill_button.setText(
            "Preenchimento"
        )
        self.fill_button.setCheckable(
            True
        )

        self.eyedropper_button = QToolButton()
        self.eyedropper_button.setText(
            "Conta-gotas"
        )
        self.eyedropper_button.setCheckable(
            True
        )

        self.tool_buttons = [
            self.brush_button,
            self.eraser_button,
            self.fill_button,
            self.eyedropper_button,
        ]

        self.zoom_combo = QComboBox()

        for label, factor in (
            ("25%", 0.25),
            ("50%", 0.5),
            ("100%", 1.0),
            ("200%", 2.0),
            ("400%", 4.0),
            ("800%", 8.0),
        ):
            self.zoom_combo.addItem(
                label,
                factor,
            )

        self.zoom_combo.setCurrentText(
            "100%"
        )

        self.fit_button = QPushButton(
            "Ajustar Saída"
        )

        self.output_info = QLabel(
            "Saída: 480 × 270"
        )

        form = QFormLayout()

        form.addRow(
            "TileSet:",
            self.tileset_combo,
        )

        header = QHBoxLayout()

        header.addWidget(
            self.back_button
        )

        header.addSpacing(
            12
        )

        header.addWidget(
            self.title
        )

        header.addStretch()

        tools = QHBoxLayout()

        tools.addWidget(
            self.brush_button
        )

        tools.addWidget(
            self.eraser_button
        )

        tools.addWidget(
            self.fill_button
        )

        tools.addWidget(
            self.eyedropper_button
        )

        tools.addSpacing(
            20
        )

        tools.addWidget(
            QLabel("Zoom:")
        )

        tools.addWidget(
            self.zoom_combo
        )

        tools.addWidget(
            self.fit_button
        )

        tools.addSpacing(
            16
        )

        tools.addWidget(
            self.output_info
        )

        tools.addStretch()

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
            self.cursor_info
        )

        left_layout.addWidget(
            QLabel(
                "Botão do meio: mover visão"
            )
        )

        right_panel = QWidget()

        right_layout = QVBoxLayout(
            right_panel
        )

        right_layout.addLayout(
            header
        )

        right_layout.addWidget(
            self.resource_label
        )

        right_layout.addLayout(
            form
        )

        right_layout.addLayout(
            tools
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

        self.back_button.clicked.connect(
            self._request_back
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

        self.canvas.tile_picked.connect(
            self._on_tile_picked
        )

        self.canvas.cursor_cell_changed.connect(
            self._on_cursor_cell_changed
        )

        self.canvas.map_changed.connect(
            self._on_map_changed
        )

        self.brush_button.clicked.connect(
            lambda: self._select_tool(
                TileMapCanvas.TOOL_BRUSH
            )
        )

        self.eraser_button.clicked.connect(
            lambda: self._select_tool(
                TileMapCanvas.TOOL_ERASER
            )
        )

        self.fill_button.clicked.connect(
            lambda: self._select_tool(
                TileMapCanvas.TOOL_FILL
            )
        )

        self.eyedropper_button.clicked.connect(
            lambda: self._select_tool(
                TileMapCanvas.TOOL_EYEDROPPER
            )
        )

        self.zoom_combo.currentIndexChanged.connect(
            self._update_zoom
        )

        self.fit_button.clicked.connect(
            self.canvas.fit_map
        )

        self.save_button.clicked.connect(
            self.save_resource
        )

        self._update_zoom()

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

        try:
            project = load_project(
                self.project_root
            )

            self.canvas.set_output_size(
                project.width,
                project.height,
            )

            platform_label = (
                "Lupi"
                if project.platform == "lupi"
                else "PC"
            )

            self.output_info.setText(
                f"Saída {platform_label}: "
                f"{project.width} × {project.height}"
            )

        except (
            OSError,
            ValueError,
            TypeError,
        ):
            self.canvas.set_output_size(
                480,
                270,
            )

            self.output_info.setText(
                "Saída: 480 × 270"
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

        self._select_tool(
            TileMapCanvas.TOOL_BRUSH
        )

        self._update_zoom()

    def _request_back(self) -> None:
        self.save_resource()

        self.back_requested.emit()

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

    def _select_tool(
        self,
        tool: str,
    ) -> None:
        mapping = {
            TileMapCanvas.TOOL_BRUSH:
                self.brush_button,
            TileMapCanvas.TOOL_ERASER:
                self.eraser_button,
            TileMapCanvas.TOOL_FILL:
                self.fill_button,
            TileMapCanvas.TOOL_EYEDROPPER:
                self.eyedropper_button,
        }

        selected_button = mapping.get(
            tool
        )

        if selected_button is None:
            return

        for button in self.tool_buttons:
            button.blockSignals(
                True
            )

            button.setChecked(
                button is selected_button
            )

            button.blockSignals(
                False
            )

        self.canvas.set_tool(
            tool
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
        self.selected_tile_id = tile_id

        self.canvas.set_selected_tile(
            tile_id
        )

        self.palette.select_tile(
            tile_id
        )

        self._update_tile_info(
            tile_id
        )

    def _on_tile_picked(
        self,
        tile_id: int,
    ) -> None:
        self.selected_tile_id = tile_id

        self.canvas.set_selected_tile(
            tile_id
        )

        self.palette.select_tile(
            tile_id
        )

        self._update_tile_info(
            tile_id
        )

        self._select_tool(
            TileMapCanvas.TOOL_BRUSH
        )

    def _update_tile_info(
        self,
        tile_id: int,
    ) -> None:
        columns = max(
            1,
            self.palette.columns,
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

    def _on_cursor_cell_changed(
        self,
        column: int,
        row: int,
    ) -> None:
        self.cursor_info.setText(
            f"Célula: col {column}, lin {row}"
        )

    def _update_zoom(self) -> None:
        factor = float(
            self.zoom_combo.currentData()
        )

        self.canvas.set_zoom(
            factor
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