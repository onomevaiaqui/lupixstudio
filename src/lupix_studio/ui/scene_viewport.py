from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRegistry
from lupix_studio.scene.model import SceneEntity, SceneResource


class SceneCanvas(QGraphicsView):
    """Viewport visual e interativo de uma Scene Lupix."""

    entity_selected = Signal(str)
    entity_moved = Signal(str, float, float)

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(
            self
        )

        self.setScene(
            self.graphics_scene
        )

        self.project_root: Path | None = None
        self.resource: SceneResource | None = None

        self.scene_width = 480
        self.scene_height = 270

        self.grid_size = 16
        self.grid_visible = True

        self.entity_items: dict[
            str,
            QGraphicsItem,
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

        self.graphics_scene.selectionChanged.connect(
            self._on_graphics_selection_changed
        )

    def set_resource(
        self,
        project_root: Path,
        resource: SceneResource,
    ) -> None:
        self.project_root = project_root.resolve()
        self.resource = resource

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

    def rebuild_entities(self) -> None:
        selected_id = self.selected_entity_id()

        self.graphics_scene.clear()
        self.entity_items.clear()

        if self.resource is None:
            return

        for entity in self.resource.entities:
            self._add_entity_item(
                entity
            )

        if selected_id is not None:
            self.select_entity(
                selected_id
            )

    def _add_entity_item(
        self,
        entity: SceneEntity,
    ) -> None:
        item = self._create_entity_item(
            entity
        )

        item.setPos(
            entity.transform.x,
            entity.transform.y,
        )

        item.setRotation(
            entity.transform.rotation
        )

        item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
            True,
        )

        item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
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

    def _create_entity_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsItem:
        if (
            entity.sprite is not None
            and entity.sprite.asset_id
            and self.project_root is not None
        ):
            registry = AssetRegistry(
                self.project_root
            )

            record = registry.find_by_id(
                entity.sprite.asset_id
            )

            if record is not None:
                path = (
                    self.project_root
                    / record.path
                )

                pixmap = QPixmap(
                    str(path)
                )

                if not pixmap.isNull():
                    item = QGraphicsPixmapItem(
                        pixmap
                    )

                    item.setOffset(
                        -pixmap.width() / 2,
                        -pixmap.height() / 2,
                    )

                    item.setOpacity(
                        max(
                            0.0,
                            min(
                                1.0,
                                entity.sprite.opacity,
                            ),
                        )
                    )

                    item.setZValue(
                        entity.sprite.layer
                    )

                    transform = QTransform()

                    transform.scale(
                        -1.0
                        if entity.sprite.flip_x
                        else 1.0,
                        -1.0
                        if entity.sprite.flip_y
                        else 1.0,
                    )

                    transform.scale(
                        entity.transform.scale_x,
                        entity.transform.scale_y,
                    )

                    item.setTransform(
                        transform
                    )

                    return item

        radius = 6

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

        item.setTransform(
            QTransform().scale(
                entity.transform.scale_x,
                entity.transform.scale_y,
            )
        )

        return item

    def update_entity(
        self,
        entity_id: str,
    ) -> None:
        if self.resource is None:
            return

        entity = self.resource.entity(
            entity_id
        )

        if entity is None:
            return

        was_selected = (
            self.selected_entity_id()
            == entity_id
        )

        old_item = self.entity_items.get(
            entity_id
        )

        if old_item is not None:
            self.graphics_scene.removeItem(
                old_item
            )

        self.entity_items.pop(
            entity_id,
            None,
        )

        self._add_entity_item(
            entity
        )

        if was_selected:
            self.select_entity(
                entity_id
            )

    def selected_entity_id(
        self,
    ) -> str | None:
        selected = self.graphics_scene.selectedItems()

        if not selected:
            return None

        value = selected[0].data(
            0
        )

        return str(value) if value else None

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

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:
        super().mouseReleaseEvent(
            event
        )

        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            return

        selected = self.graphics_scene.selectedItems()

        if not selected:
            return

        item = selected[0]

        entity_id = item.data(
            0
        )

        if not entity_id:
            return

        position = item.pos()

        self.entity_moved.emit(
            str(entity_id),
            position.x(),
            position.y(),
        )

    def _on_graphics_selection_changed(
        self,
    ) -> None:
        entity_id = self.selected_entity_id()

        if entity_id is not None:
            self.entity_selected.emit(
                entity_id
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


class SceneViewport(QWidget):
    """Editor visual de uma Scene."""

    entity_selected = Signal(str)
    entity_moved = Signal(str, float, float)

    def __init__(self) -> None:
        super().__init__()

        self.resource: SceneResource | None = None
        self.project_root: Path | None = None

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
        project_root: Path,
        resource: SceneResource,
    ) -> None:
        self.project_root = project_root.resolve()
        self.resource = resource

        self.title.setText(
            resource.name
        )

        self.resolution_label.setText(
            f"{resource.width} × {resource.height}"
        )

        self.canvas.set_resource(
            self.project_root,
            resource,
        )

        self._update_grid()
        self._update_zoom()

    def refresh_entities(self) -> None:
        self.canvas.rebuild_entities()

    def select_entity(
        self,
        entity_id: str,
    ) -> None:
        self.canvas.select_entity(
            entity_id
        )

    def update_entity(
        self,
        entity_id: str,
    ) -> None:
        self.canvas.update_entity(
            entity_id
        )

    def _update_grid(self) -> None:
        self.canvas.set_grid_size(
            int(
                self.grid_combo.currentData()
            )
        )

    def _update_zoom(self) -> None:
        self.canvas.set_zoom(
            float(
                self.zoom_combo.currentData()
            )
        )