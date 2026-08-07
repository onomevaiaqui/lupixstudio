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
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRecord
from lupix_studio.tileset.model import TilePattern, TileSetResource
from lupix_studio.tileset.serializer import TileSetSerializer
from lupix_studio.tileset.validator import validate_tileset


class TileSetCanvas(QGraphicsView):
    selection_changed = Signal(int, int, int, int)

    def __init__(self) -> None:
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item: QGraphicsPixmapItem | None = None

        self.tile_width = 16
        self.tile_height = 16

        self.start_column: int | None = None
        self.start_row: int | None = None
        self.end_column: int | None = None
        self.end_row: int | None = None

        self.dragging = False

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

    def clear_selection(
        self,
    ) -> None:
        self.start_column = None
        self.start_row = None
        self.end_column = None
        self.end_row = None

        self.viewport().update()

    def _cell_at(
        self,
        scene_pos: QPointF,
    ) -> tuple[int, int] | None:
        if self.pixmap_item is None:
            return None

        pixmap = self.pixmap_item.pixmap()

        x = scene_pos.x()
        y = scene_pos.y()

        if (
            x < 0
            or y < 0
            or x >= pixmap.width()
            or y >= pixmap.height()
        ):
            return None

        return (
            int(x // self.tile_width),
            int(y // self.tile_height),
        )

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            cell = self._cell_at(
                self.mapToScene(
                    event.position().toPoint()
                )
            )

            if cell is not None:
                self.start_column = cell[0]
                self.start_row = cell[1]
                self.end_column = cell[0]
                self.end_row = cell[1]
                self.dragging = True

                self._emit_selection()
                self.viewport().update()

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if self.dragging:
            cell = self._cell_at(
                self.mapToScene(
                    event.position().toPoint()
                )
            )

            if cell is not None:
                self.end_column = cell[0]
                self.end_row = cell[1]

                self._emit_selection()
                self.viewport().update()

        super().mouseMoveEvent(
            event
        )

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.dragging = False

        super().mouseReleaseEvent(
            event
        )

    def selection_rect_cells(
        self,
    ) -> tuple[int, int, int, int] | None:
        if (
            self.start_column is None
            or self.start_row is None
            or self.end_column is None
            or self.end_row is None
        ):
            return None

        left = min(
            self.start_column,
            self.end_column,
        )

        right = max(
            self.start_column,
            self.end_column,
        )

        top = min(
            self.start_row,
            self.end_row,
        )

        bottom = max(
            self.start_row,
            self.end_row,
        )

        return (
            left,
            top,
            right - left + 1,
            bottom - top + 1,
        )

    def select_pattern(
        self,
        pattern: TilePattern,
    ) -> None:
        self.start_column = pattern.column
        self.start_row = pattern.row

        self.end_column = (
            pattern.column
            + pattern.width
            - 1
        )

        self.end_row = (
            pattern.row
            + pattern.height
            - 1
        )

        self._emit_selection()
        self.viewport().update()

    def _emit_selection(
        self,
    ) -> None:
        selection = self.selection_rect_cells()

        if selection is None:
            return

        self.selection_changed.emit(
            *selection
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
                80,
            )
        )

        grid_pen.setCosmetic(True)
        painter.setPen(grid_pen)

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

        selection = self.selection_rect_cells()

        if selection is None:
            return

        column, row, width, height = selection

        pen = QPen(
            QColor(
                255,
                210,
                60,
            ),
            2,
        )

        pen.setCosmetic(True)
        painter.setPen(pen)

        painter.drawRect(
            QRectF(
                column * self.tile_width,
                row * self.tile_height,
                width * self.tile_width,
                height * self.tile_height,
            )
        )


class TileSetEditor(QWidget):
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

        self.path_label = QLabel("-")
        self.path_label.setWordWrap(True)

        self.validation_label = QLabel(
            "Validação: -"
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

        self.selection_value = QLabel("-")

        self.pattern_name = QLineEdit()
        self.pattern_name.setPlaceholderText(
            "Nome do padrão"
        )

        self.add_pattern_button = QPushButton(
            "Adicionar padrão"
        )

        self.remove_pattern_button = QPushButton(
            "Remover padrão"
        )

        self.pattern_list = QListWidget()

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

        controls.addSpacing(20)

        controls.addWidget(
            self.save_button
        )

        controls.addStretch()

        selection_info = QHBoxLayout()

        selection_info.addWidget(
            QLabel("Seleção:")
        )

        selection_info.addWidget(
            self.selection_value
        )

        selection_info.addStretch()

        pattern_controls = QHBoxLayout()

        pattern_controls.addWidget(
            self.pattern_name
        )

        pattern_controls.addWidget(
            self.add_pattern_button
        )

        pattern_controls.addWidget(
            self.remove_pattern_button
        )

        right_panel = QWidget()

        right_layout = QVBoxLayout(
            right_panel
        )

        right_layout.addWidget(
            QLabel("Tile Palette")
        )

        right_layout.addLayout(
            pattern_controls
        )

        right_layout.addWidget(
            self.pattern_list
        )

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.addWidget(
            self.canvas
        )

        splitter.addWidget(
            right_panel
        )

        splitter.setStretchFactor(
            0,
            4,
        )

        splitter.setStretchFactor(
            1,
            1,
        )

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.path_label
        )

        layout.addWidget(
            self.validation_label
        )

        layout.addLayout(
            controls
        )

        layout.addLayout(
            selection_info
        )

        layout.addWidget(
            splitter
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

        self.canvas.selection_changed.connect(
            self._on_selection_changed
        )

        self.add_pattern_button.clicked.connect(
            self._add_pattern
        )

        self.remove_pattern_button.clicked.connect(
            self._remove_pattern
        )

        self.pattern_list.itemClicked.connect(
            self._on_pattern_clicked
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
        self._refresh_patterns()
        self._refresh_validation()

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

        self._refresh_validation()

    def _update_grid(
        self,
    ) -> None:
        self.canvas.set_grid_size(
            self.tile_width_spin.value(),
            self.tile_height_spin.value(),
        )

        self.selection_value.setText("-")

        if self.resource is not None:
            self.resource.tile_width = (
                self.tile_width_spin.value()
            )

            self.resource.tile_height = (
                self.tile_height_spin.value()
            )

            self._refresh_validation()

    def _update_zoom(
        self,
    ) -> None:
        factor = float(
            self.zoom_combo.currentData()
        )

        self.canvas.set_zoom(
            factor
        )

    def _on_selection_changed(
        self,
        column: int,
        row: int,
        width: int,
        height: int,
    ) -> None:
        self.selection_value.setText(
            f"col {column}, lin {row}, "
            f"{width} × {height}"
        )

    def _add_pattern(
        self,
    ) -> None:
        if self.resource is None:
            return

        selection = (
            self.canvas.selection_rect_cells()
        )

        if selection is None:
            return

        column, row, width, height = selection

        name = self.pattern_name.text().strip()

        if not name:
            name = (
                f"Pattern {len(self.resource.patterns) + 1}"
            )

        self.resource.patterns.append(
            TilePattern(
                name=name,
                column=column,
                row=row,
                width=width,
                height=height,
            )
        )

        self.pattern_name.clear()

        self._refresh_patterns()
        self.save_resource()

    def _remove_pattern(
        self,
    ) -> None:
        if self.resource is None:
            return

        row = self.pattern_list.currentRow()

        if (
            row < 0
            or row >= len(
                self.resource.patterns
            )
        ):
            return

        del self.resource.patterns[
            row
        ]

        self._refresh_patterns()
        self.save_resource()

    def _refresh_patterns(
        self,
    ) -> None:
        self.pattern_list.clear()

        if self.resource is None:
            return

        for pattern in self.resource.patterns:
            self.pattern_list.addItem(
                QListWidgetItem(
                    f"{pattern.name} "
                    f"({pattern.width}x{pattern.height})"
                )
            )

    def _on_pattern_clicked(
        self,
        item: QListWidgetItem,
    ) -> None:
        if self.resource is None:
            return

        row = self.pattern_list.row(
            item
        )

        if (
            row < 0
            or row >= len(
                self.resource.patterns
            )
        ):
            return

        self.canvas.select_pattern(
            self.resource.patterns[
                row
            ]
        )

    def _refresh_validation(
        self,
    ) -> None:
        if (
            self.resource is None
            or self.project_root is None
        ):
            self.validation_label.setText(
                "Validação: -"
            )
            return

        issues = validate_tileset(
            self.resource,
            self.project_root,
        )

        errors = [
            issue
            for issue in issues
            if issue.level == "error"
        ]

        warnings = [
            issue
            for issue in issues
            if issue.level == "warning"
        ]

        if errors:
            self.validation_label.setText(
                f"Validação: {len(errors)} erro(s), "
                f"{len(warnings)} aviso(s)"
            )
            return

        if warnings:
            self.validation_label.setText(
                f"Validação: {len(warnings)} aviso(s)"
            )
            return

        self.validation_label.setText(
            "Validação: OK"
        )