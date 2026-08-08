from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import SceneEntity, SceneResource


class SceneCanvas(QGraphicsView):
    """Viewport visual de uma Scene Lupix."""

    entity_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(self)
        self.setScene(
            self.graphics_scene
        )

        self.resource: SceneResource | None = None

        self.scene_width = 480
        self.scene_height = 270

        self.grid_size = 16
        self.grid_visible = True

        self.entity_items: dict[
            str,
            QGraphicsEllipseItem,
        ] = {}

        self.setBackgroundBrush(
            QColor("#111216")
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )

        self.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            False,
        )

        self.graphics_scene.selectionChanged.connect(
            self._on_graphics_selection_changed
        )

        self.set_scene_size(
            self.scene_width,
            self.scene_height,
        )

    def set_resource(
        self,
        resource: SceneResource | None,
    ) -> None:
        self.resource = resource

        if resource is None:
            self.graphics_scene.clear()
            self.entity_items.clear()
            return

        self.set_scene_size(
            resource.width,
            resource.height,
        )

        self.rebuild_entities()

    def set_scene_size(
        self,
        width: int,
        height: int,
    ) -> None:
        self.scene_width = max(
            1,
            int(width),
        )

        self.scene_height = max(
            1,
            int(height),
        )

        margin = 128

        self.graphics_scene.setSceneRect(
            QRectF(
                -margin,
                -margin,
                self.scene_width
                + margin * 2,
                self.scene_height
                + margin * 2,
            )
        )

        self.viewport().update()

    def set_grid_visible(
        self,
        visible: bool,
    ) -> None:
        self.grid_visible = visible
        self.viewport().update()

    def set_grid_size(
        self,
        size: int,
    ) -> None:
        self.grid_size = max(
            1,
            int(size),
        )

        self.viewport().update()

    def set_zoom(
        self,
        factor: float,
    ) -> None:
        self.resetTransform()

        self.scale(
            factor,
            factor,
        )

    def rebuild_entities(
        self,
    ) -> None:
        self._remove_entity_items()

        if self.resource is None:
            return

        for entity in self.resource.entities:
            self._add_entity_item(
                entity
            )

    def _remove_entity_items(
        self,
    ) -> None:
        for item in self.entity_items.values():
            self.graphics_scene.removeItem(
                item
            )

        self.entity_items.clear()

    def _add_entity_item(
        self,
        entity: SceneEntity,
    ) -> None:
        radius = 5

        item = QGraphicsEllipseItem(
            -radius,
            -radius,
            radius * 2,
            radius * 2,
        )

        item.setBrush(
            QColor("#d5b85a")
        )

        item.setPen(
            QPen(
                QColor("#f4df8c"),
                1,
            )
        )

        item.setPos(
            entity.transform.x,
            entity.transform.y,
        )

        item.setFlag(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable,
            True,
        )

        item.setData(
            0,
            entity.id,
        )

        self.graphics_scene.addItem(
            item
        )

        self.entity_items[
            entity.id
        ] = item

    def select_entity(
        self,
        entity_id: str,
    ) -> None:
        item = self.entity_items.get(
            entity_id
        )

        if item is None:
            return

        self.graphics_scene.clearSelection()

        item.setSelected(
            True
        )

        self.centerOn(
            item
        )

    def _on_graphics_selection_changed(
        self,
    ) -> None:
        selected = (
            self.graphics_scene.selectedItems()
        )

        if not selected:
            return

        entity_id = selected[0].data(
            0
        )

        if entity_id:
            self.entity_selected.emit(
                str(entity_id)
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

        game_rect = QRectF(
            0,
            0,
            self.scene_width,
            self.scene_height,
        )

        painter.fillRect(
            game_rect,
            QColor("#202225"),
        )

        border_pen = QPen(
            QColor("#7a7d84"),
            1,
        )

        border_pen.setCosmetic(
            True
        )

        painter.setPen(
            border_pen
        )

        painter.drawRect(
            game_rect
        )

        if self.grid_visible:
            self._draw_grid(
                painter
            )

        self._draw_origin(
            painter
        )

    def _draw_grid(
        self,
        painter: QPainter,
    ) -> None:
        grid_pen = QPen(
            QColor(
                255,
                255,
                255,
                28,
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

        while x <= self.scene_width:
            painter.drawLine(
                QPointF(
                    x,
                    0,
                ),
                QPointF(
                    x,
                    self.scene_height,
                ),
            )

            x += self.grid_size

        y = 0

        while y <= self.scene_height:
            painter.drawLine(
                QPointF(
                    0,
                    y,
                ),
                QPointF(
                    self.scene_width,
                    y,
                ),
            )

            y += self.grid_size

    def _draw_origin(
        self,
        painter: QPainter,
    ) -> None:
        axis_pen = QPen(
            QColor("#d65f5f"),
            1,
        )

        axis_pen.setCosmetic(
            True
        )

        painter.setPen(
            axis_pen
        )

        painter.drawLine(
            QPointF(
                0,
                0,
            ),
            QPointF(
                24,
                0,
            ),
        )

        axis_pen.setColor(
            QColor("#62b879")
        )

        painter.setPen(
            axis_pen
        )

        painter.drawLine(
            QPointF(
                0,
                0,
            ),
            QPointF(
                0,
                24,
            ),
        )


class SceneViewport(QWidget):
    """Editor visual básico de uma Scene."""

    entity_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.resource: SceneResource | None = None

        self.title = QLabel(
            "Nenhuma cena aberta"
        )

        self.resolution_label = QLabel(
            "-"
        )

        self.grid_checkbox = QCheckBox(
            "Grade"
        )

        self.grid_checkbox.setChecked(
            True
        )

        self.grid_combo = QComboBox()

        for size in (
            8,
            16,
            32,
            64,
        ):
            self.grid_combo.addItem(
                f"{size}px",
                size,
            )

        self.grid_combo.setCurrentText(
            "16px"
        )

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
            "200%"
        )

        self.canvas = SceneCanvas()

        controls = QHBoxLayout()

        controls.addWidget(
            QLabel("Grade:")
        )

        controls.addWidget(
            self.grid_checkbox
        )

        controls.addWidget(
            self.grid_combo
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

        controls.addStretch()

        layout = QVBoxLayout(
            self
        )

        layout.addWidget(
            self.title
        )

        layout.addWidget(
            self.resolution_label
        )

        layout.addLayout(
            controls
        )

        layout.addWidget(
            self.canvas
        )

        self.grid_checkbox.toggled.connect(
            self.canvas.set_grid_visible
        )

        self.grid_combo.currentIndexChanged.connect(
            self._update_grid
        )

        self.zoom_combo.currentIndexChanged.connect(
            self._update_zoom
        )

        self.canvas.entity_selected.connect(
            self.entity_selected.emit
        )

        self._update_grid()
        self._update_zoom()

    def open_scene(
        self,
        resource: SceneResource,
    ) -> None:
        self.resource = resource

        self.title.setText(
            resource.name
        )

        self.resolution_label.setText(
            f"{resource.width} × {resource.height}"
        )

        self.canvas.set_resource(
            resource
        )

        self._update_grid()
        self._update_zoom()

    def refresh_entities(
        self,
    ) -> None:
        self.canvas.rebuild_entities()

    def select_entity(
        self,
        entity_id: str,
    ) -> None:
        self.canvas.select_entity(
            entity_id
        )

    def _update_grid(
        self,
    ) -> None:
        size = int(
            self.grid_combo.currentData()
        )

        self.canvas.set_grid_size(
            size
        )

    def _update_zoom(
        self,
    ) -> None:
        factor = float(
            self.zoom_combo.currentData()
        )

        self.canvas.set_zoom(
            factor
        )