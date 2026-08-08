from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import SceneEntity, SceneResource


class SceneEntityItem(QGraphicsEllipseItem):
    """Representação visual temporária de uma entidade."""

    def __init__(
        self,
        entity: SceneEntity,
    ) -> None:
        radius = 5

        super().__init__(
            -radius,
            -radius,
            radius * 2,
            radius * 2,
        )

        self.entity = entity

        self.setBrush(
            QColor("#d5b85a")
        )

        self.setPen(
            QPen(
                QColor("#f4df8c"),
                1,
            )
        )

        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
            True,
        )

        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
            True,
        )

        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges,
            True,
        )

        self.setData(
            0,
            entity.id,
        )

        self.sync_from_entity()

    def sync_from_entity(
        self,
    ) -> None:
        self.setPos(
            self.entity.transform.x,
            self.entity.transform.y,
        )

        self.setRotation(
            self.entity.transform.rotation
        )

        self.setScale(
            self.entity.transform.scale_x
        )

    def itemChange(
        self,
        change,
        value,
    ):
        result = super().itemChange(
            change,
            value,
        )

        if (
            change
            == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged
        ):
            position = self.pos()

            self.entity.transform.x = (
                position.x()
            )

            self.entity.transform.y = (
                position.y()
            )

        return result


class SceneCanvas(QGraphicsView):
    """Viewport visual de uma Scene Lupix."""

    entity_selected = Signal(str)
    entity_moved = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(
            self
        )

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
            SceneEntityItem,
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
                self.scene_width + margin * 2,
                self.scene_height + margin * 2,
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
        selected_ids = {
            str(item.data(0))
            for item in self.graphics_scene.selectedItems()
            if item.data(0)
        }

        self._remove_entity_items()

        if self.resource is None:
            return

        for entity in self.resource.entities:
            item = SceneEntityItem(
                entity
            )

            self.graphics_scene.addItem(
                item
            )

            self.entity_items[
                entity.id
            ] = item

            if entity.id in selected_ids:
                item.setSelected(
                    True
                )

    def refresh_entity(
        self,
        entity_id: str,
    ) -> None:
        item = self.entity_items.get(
            entity_id
        )

        if item is None:
            return

        item.sync_from_entity()

        self.viewport().update()

    def _remove_entity_items(
        self,
    ) -> None:
        for item in self.entity_items.values():
            self.graphics_scene.removeItem(
                item
            )

        self.entity_items.clear()

    def select_entity(
        self,
        entity_id: str,
    ) -> None:
        item = self.entity_items.get(
            entity_id
        )

        if item is None:
            return

        self.graphics_scene.blockSignals(
            True
        )

        try:
            self.graphics_scene.clearSelection()
            item.setSelected(
                True
            )

        finally:
            self.graphics_scene.blockSignals(
                False
            )

        self.centerOn(
            item
        )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:
        selected_before = (
            self.graphics_scene.selectedItems()
        )

        super().mouseReleaseEvent(
            event
        )

        selected = (
            self.graphics_scene.selectedItems()
        )

        if not selected:
            return

        item = selected[0]

        if not isinstance(
            item,
            SceneEntityItem,
        ):
            return

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.entity_moved.emit(
                item.entity.id
            )

        if selected_before != selected:
            self.entity_selected.emit(
                item.entity.id
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
                QPointF(x, 0),
                QPointF(
                    x,
                    self.scene_height,
                ),
            )

            x += self.grid_size

        y = 0

        while y <= self.scene_height:
            painter.drawLine(
                QPointF(0, y),
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
            QPointF(0, 0),
            QPointF(24, 0),
        )

        axis_pen.setColor(
            QColor("#62b879")
        )

        painter.setPen(
            axis_pen
        )

        painter.drawLine(
            QPointF(0, 0),
            QPointF(0, 24),
        )


class SceneViewport(QWidget):
    """Editor visual básico de uma Scene."""

    entity_selected = Signal(str)
    entity_moved = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.resource: SceneResource | None = None

        self.title = QLabel(
            "Nenhuma cena aberta"
        )

        self.resolution_label = QLabel("-")

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

        self.canvas.entity_moved.connect(
            self.entity_moved.emit
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

    def refresh_entity(
        self,
        entity_id: str,
    ) -> None:
        self.canvas.refresh_entity(
            entity_id
        )

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