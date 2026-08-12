from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import (
    QRectF,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QKeyEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRegistry
from lupix_studio.runtime import SceneRuntime
from lupix_studio.scene.model import (
    SceneEntity,
    SceneResource,
)
from lupix_studio.tilemap.serializer import (
    TileMapSerializer,
)


class PlayCanvas(QGraphicsView):
    """Canvas de execução da cena."""

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(
            self
        )

        self.setScene(
            self.graphics_scene
        )

        self.project_root: Path | None = None
        self.runtime: SceneRuntime | None = None

        self.entity_items: dict[
            str,
            QGraphicsPixmapItem | QGraphicsRectItem,
        ] = {}

        self.setBackgroundBrush(
            QColor("#111216")
        )

        self.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

    def set_runtime(
        self,
        project_root: Path,
        runtime: SceneRuntime,
    ) -> None:
        self.project_root = (
            project_root.resolve()
        )

        self.runtime = runtime

        self.rebuild()

    def rebuild(self) -> None:
        self.graphics_scene.clear()
        self.entity_items.clear()

        if self.runtime is None:
            return

        scene = self.runtime.scene

        self.graphics_scene.setSceneRect(
            QRectF(
                0,
                0,
                scene.width,
                scene.height,
            )
        )

        background = QGraphicsRectItem(
            0,
            0,
            scene.width,
            scene.height,
        )

        background.setBrush(
            QColor("#202225")
        )

        background.setPen(
            QPen(
                QColor("#777a80"),
                1,
            )
        )

        background.setZValue(
            -100000
        )

        self.graphics_scene.addItem(
            background
        )

        for entity in scene.entities:
            self._add_entity(
                entity
            )

        self.fit_scene()

    def refresh(self) -> None:
        if self.runtime is None:
            return

        for entity in self.runtime.scene.entities:
            item = self.entity_items.get(
                entity.id
            )

            if item is None:
                continue

            item.setPos(
                entity.transform.x,
                entity.transform.y,
            )

            item.setRotation(
                entity.transform.rotation
            )

    def fit_scene(self) -> None:
        if self.runtime is None:
            return

        scene = self.runtime.scene

        self.fitInView(
            QRectF(
                0,
                0,
                scene.width,
                scene.height,
            ),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def _add_entity(
        self,
        entity: SceneEntity,
    ) -> None:
        item = self._create_visual(
            entity
        )

        if item is None:
            return

        item.setPos(
            entity.transform.x,
            entity.transform.y,
        )

        item.setRotation(
            entity.transform.rotation
        )

        self.graphics_scene.addItem(
            item
        )

        self.entity_items[
            entity.id
        ] = item

    def _create_visual(
        self,
        entity: SceneEntity,
    ) -> QGraphicsPixmapItem | QGraphicsRectItem | None:
        tilemap_item = self._create_tilemap_item(
            entity
        )

        if tilemap_item is not None:
            return tilemap_item

        sprite_item = self._create_sprite_item(
            entity
        )

        if sprite_item is not None:
            return sprite_item

        if (
            entity.player_controller is not None
            and entity.player_controller.enabled
        ):
            marker = QGraphicsRectItem(
                -8,
                -14,
                16,
                28,
            )

            marker.setBrush(
                QColor("#59b7ff")
            )

            marker.setPen(
                QPen(
                    Qt.PenStyle.NoPen
                )
            )

            return marker

        return None

    def _create_sprite_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsPixmapItem | None:
        if (
            entity.sprite is None
            or not entity.sprite.asset_id
            or self.project_root is None
        ):
            return None

        registry = AssetRegistry(
            self.project_root
        )

        record = registry.find_by_id(
            entity.sprite.asset_id
        )

        if record is None:
            return None

        image_path = (
            self.project_root
            / record.path
        )

        pixmap = QPixmap(
            str(image_path)
        )

        if pixmap.isNull():
            return None

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

        return item

    def _create_tilemap_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsPixmapItem | None:
        if (
            entity.tilemap is None
            or not entity.tilemap.resource_path
            or self.project_root is None
        ):
            return None

        resource_path = (
            self.project_root
            / entity.tilemap.resource_path
        )

        if not resource_path.exists():
            return None

        try:
            tilemap = TileMapSerializer().load(
                resource_path
            )

        except (
            OSError,
            ValueError,
            TypeError,
        ):
            return None

        if not tilemap.tileset_asset_id:
            return None

        registry = AssetRegistry(
            self.project_root
        )

        record = registry.find_by_id(
            tilemap.tileset_asset_id
        )

        if record is None:
            return None

        texture_path = (
            self.project_root
            / record.path
        )

        source = QPixmap(
            str(texture_path)
        )

        if source.isNull():
            return None

        output_width = (
            tilemap.width
            * tilemap.tile_width
        )

        output_height = (
            tilemap.height
            * tilemap.tile_height
        )

        if (
            output_width <= 0
            or output_height <= 0
        ):
            return None

        output = QPixmap(
            output_width,
            output_height,
        )

        output.fill(
            Qt.GlobalColor.transparent
        )

        painter = QPainter(
            output
        )

        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        columns = max(
            1,
            source.width()
            // tilemap.tile_width,
        )

        for layer in tilemap.layers:
            if not layer.visible:
                continue

            if (
                layer.name.strip().lower()
                == "collision"
            ):
                continue

            painter.save()

            painter.setOpacity(
                max(
                    0.0,
                    min(
                        1.0,
                        layer.opacity,
                    ),
                )
            )

            for key, tile_id in layer.cells.items():
                try:
                    column_text, row_text = key.split(
                        ",",
                        maxsplit=1,
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

                source_column = (
                    tile_id
                    % columns
                )

                source_row = (
                    tile_id
                    // columns
                )

                source_rect = QRectF(
                    source_column
                    * tilemap.tile_width,
                    source_row
                    * tilemap.tile_height,
                    tilemap.tile_width,
                    tilemap.tile_height,
                )

                destination_rect = QRectF(
                    column
                    * tilemap.tile_width,
                    row
                    * tilemap.tile_height,
                    tilemap.tile_width,
                    tilemap.tile_height,
                )

                painter.drawPixmap(
                    destination_rect,
                    source,
                    source_rect,
                )

            painter.restore()

        painter.end()

        item = QGraphicsPixmapItem(
            output
        )

        item.setOffset(
            0,
            0,
        )

        item.setZValue(
            -10000
        )

        return item


class PlayPreview(QWidget):
    """Preview executável da cena."""

    stop_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.runtime: SceneRuntime | None = None

        self.timer = QTimer(
            self
        )

        self.timer.setInterval(
            16
        )

        self.timer.timeout.connect(
            self._update_runtime
        )

        self.title = QLabel(
            "▶ Preview"
        )

        self.status_label = QLabel(
            "Parado"
        )

        self.controls_label = QLabel(
            "A/← Esquerda   "
            "D/→ Direita   "
            "Espaço Pular"
        )

        self.stop_button = QPushButton(
            "■ Stop"
        )

        self.fit_button = QPushButton(
            "Ajustar"
        )

        self.canvas = PlayCanvas()

        header = QHBoxLayout()

        header.addWidget(
            self.title
        )

        header.addSpacing(
            12
        )

        header.addWidget(
            self.status_label
        )

        header.addStretch()

        header.addWidget(
            self.fit_button
        )

        header.addWidget(
            self.stop_button
        )

        layout = QVBoxLayout(
            self
        )

        layout.addLayout(
            header
        )

        layout.addWidget(
            self.controls_label
        )

        layout.addWidget(
            self.canvas
        )

        self.stop_button.clicked.connect(
            self.stop
        )

        self.fit_button.clicked.connect(
            self.canvas.fit_scene
        )

    def start(
        self,
        project_root: Path,
        scene: SceneResource,
    ) -> None:
        self.stop_runtime()

        self.project_root = (
            project_root.resolve()
        )

        self.runtime = SceneRuntime(
            scene,
            project_root=self.project_root,
        )

        self.runtime.start()

        self.canvas.set_runtime(
            self.project_root,
            self.runtime,
        )

        self.status_label.setText(
            "Executando"
        )

        self.timer.start()

        self.canvas.setFocus()

    def stop_runtime(self) -> None:
        self.timer.stop()

        if self.runtime is not None:
            self.runtime.stop()

        self.runtime = None

        self.status_label.setText(
            "Parado"
        )

    def stop(self) -> None:
        self.stop_runtime()

        self.stop_requested.emit()

    def _update_runtime(self) -> None:
        if self.runtime is None:
            return

        self.runtime.update(
            1.0 / 60.0
        )

        self.canvas.refresh()

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ) -> None:
        if self.runtime is None:
            super().keyPressEvent(
                event
            )
            return

        key = event.key()

        if key in (
            Qt.Key.Key_A,
            Qt.Key.Key_Left,
        ):
            self.runtime.input.left = True

            event.accept()
            return

        if key in (
            Qt.Key.Key_D,
            Qt.Key.Key_Right,
        ):
            self.runtime.input.right = True

            event.accept()
            return

        if key == Qt.Key.Key_Space:
            self.runtime.input.jump = True

            event.accept()
            return

        if key == Qt.Key.Key_Escape:
            self.stop()

            event.accept()
            return

        super().keyPressEvent(
            event
        )

    def keyReleaseEvent(
        self,
        event: QKeyEvent,
    ) -> None:
        if self.runtime is None:
            super().keyReleaseEvent(
                event
            )
            return

        if event.isAutoRepeat():
            return

        key = event.key()

        if key in (
            Qt.Key.Key_A,
            Qt.Key.Key_Left,
        ):
            self.runtime.input.left = False

            event.accept()
            return

        if key in (
            Qt.Key.Key_D,
            Qt.Key.Key_Right,
        ):
            self.runtime.input.right = False

            event.accept()
            return

        if key == Qt.Key.Key_Space:
            self.runtime.input.jump = False

            event.accept()
            return

        super().keyReleaseEvent(
            event
        )