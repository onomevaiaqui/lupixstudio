from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QPainter,
    QPen,
    QPixmap,
    QTransform,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRegistry
from lupix_studio.project.loader import load_project
from lupix_studio.scene.model import (
    SceneEntity,
    SceneResource,
)
from lupix_studio.tilemap.model import TileLayer
from lupix_studio.tilemap.serializer import TileMapSerializer


class SceneCanvas(QGraphicsView):
    """Viewport visual e interativo de uma Scene Lupix."""

    entity_selected = Signal(str)

    entity_moved = Signal(
        str,
        float,
        float,
    )

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

        self.editor_rect = QRectF(
            -2048,
            -2048,
            12288,
            8192,
        )

        self.grid_size = 16
        self.grid_visible = True

        self.colliders_visible = True

        self.entity_items: dict[
            str,
            QGraphicsItem,
        ] = {}

        # A seleção do viewport é controlada pela Hierarquia.
        # Cliques na cena não trocam a entidade ativa.
        self._active_entity_id: str | None = None
        self._dragging_entity = False
        self._drag_offset = QPointF()

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
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        self.graphics_scene.selectionChanged.connect(
            self._on_graphics_selection_changed
        )

    def set_resource(
        self,
        project_root: Path,
        resource: SceneResource,
    ) -> None:
        self.project_root = (
            project_root.resolve()
        )

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

        editor_width = max(
            8192,
            self.scene_width * 8,
        )

        editor_height = max(
            4096,
            self.scene_height * 8,
        )

        self.editor_rect = QRectF(
            -2048,
            -2048,
            editor_width + 4096,
            editor_height + 4096,
        )

        self.graphics_scene.setSceneRect(
            self.editor_rect
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

    def set_colliders_visible(
        self,
        visible: bool,
    ) -> None:
        self.colliders_visible = visible

        self.rebuild_entities()

    def set_zoom(
        self,
        factor: float,
    ) -> None:
        self.resetTransform()

        self.scale(
            factor,
            factor,
        )

    def center_scene(self) -> None:
        """Centraliza a área útil da cena no viewport."""
        self.centerOn(
            self.scene_width / 2.0,
            self.scene_height / 2.0,
        )

    def rebuild_entities(self) -> None:
        selected_id = (
            self.selected_entity_id()
        )

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

        # A posição da entidade continua sendo a origem
        # de todos os seus componentes.
        #
        # Para TileMap, (0, 0) corresponde ao canto
        # superior esquerdo do mapa/cena.
        item.setPos(
            entity.transform.x,
            entity.transform.y,
        )

        item.setRotation(
            entity.transform.rotation
        )

        if entity.ui_element is not None:
            item.setZValue(float(entity.ui_element.get("layer", 0)))

        # A seleção visual padrão do QGraphicsItem fica desativada.
        # A Hierarquia continua sendo a fonte de verdade da seleção,
        # mas nenhum retângulo de seleção é desenhado ao redor do Player.
        item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
            False,
        )

        # O movimento é controlado manualmente pelo SceneCanvas.
        # Isso impede que um clique sobre Sprite/Camera/Collider/TileMap
        # troque a seleção definida pela Hierarquia.
        item.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
            False,
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

    def _create_ui_element_item(self, entity: SceneEntity):
        data = entity.ui_element
        if data is None:
            return None
        element_type = str(data.get("type", "text"))
        text = str(data.get("text", ""))
        color = QColor(str(data.get("color", "#ffffff")))
        font = QFont()
        font.setPointSize(max(8, int(data.get("font_size", 24))))
        font_path = str(data.get("font", "") or "")
        if font_path and self.project_root is not None:
            path = (self.project_root / font_path).resolve()
            if path.is_file():
                font_id = QFontDatabase.addApplicationFont(str(path))
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    font.setFamily(families[0])
        width = max(1.0, float(data.get("width", 180.0)))
        height = max(1.0, float(data.get("height", 48.0)))
        if element_type == "image":
            asset = str(data.get("asset", "") or "")
            if not asset or self.project_root is None:
                return None
            pixmap = QPixmap(str((self.project_root / asset).resolve()))
            if pixmap.isNull():
                return None
            pixmap = pixmap.scaled(
                int(width), int(height),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            item = QGraphicsPixmapItem(pixmap)
            item.setOffset(-width / 2.0, -height / 2.0)
            return item
        if element_type == "button":
            group = QGraphicsItemGroup()
            rect = QGraphicsRectItem(-width / 2.0, -height / 2.0, width, height)
            background_opacity = max(0.0, min(1.0, float(data.get("button_opacity", 100)) / 100.0))
            border_opacity = max(0.0, min(1.0, float(data.get("button_border_opacity", 100)) / 100.0))
            border_color = QColor(str(data.get("button_border_color", "#d5ad38")))
            border_color.setAlphaF(border_opacity)
            rect.setPen(QPen(border_color, 2.0))
            normal_image = str(data.get("button_normal_image", "") or "")
            normal_pixmap = QPixmap()
            if normal_image and self.project_root is not None:
                normal_pixmap = QPixmap(str((self.project_root / normal_image).resolve()))
            if bool(data.get("button_transparent", False)) or background_opacity <= 0.0:
                rect.setBrush(Qt.BrushStyle.NoBrush)
            elif not normal_pixmap.isNull():
                rect.setBrush(QBrush(normal_pixmap.scaled(
                    int(width), int(height), Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )))
                rect.setOpacity(background_opacity)
            else:
                background = QColor(str(data.get("button_normal_color", "#252a34")))
                background.setAlphaF(background_opacity)
                rect.setBrush(background)
            label = QGraphicsTextItem(text)
            label.setDefaultTextColor(QColor(str(data.get("button_text_normal_color", data.get("color", "#ffffff")))))
            label.setFont(font)
            bounds = label.boundingRect()
            label.setPos(-bounds.width() / 2.0, -bounds.height() / 2.0)
            group.addToGroup(rect)
            group.addToGroup(label)
            return group
        # O texto fica dentro de um contêiner cuja origem representa
        # o centro do elemento. A posição da entidade move o contêiner,
        # sem sobrescrever o deslocamento interno usado para centralizar.
        group = QGraphicsItemGroup()
        label = QGraphicsTextItem(text)
        label.setDefaultTextColor(color)
        label.setFont(font)
        bounds = label.boundingRect()
        label.setPos(-bounds.width() / 2.0, -bounds.height() / 2.0)
        group.addToGroup(label)
        return group

    def _create_entity_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsItem:
        group = QGraphicsItemGroup()

        has_visual = False

        ui_item = self._create_ui_element_item(entity)
        if ui_item is not None:
            group.addToGroup(ui_item)
            has_visual = True

        tilemap_item = self._create_tilemap_item(
            entity
        )

        if tilemap_item is not None:
            group.addToGroup(
                tilemap_item
            )

            has_visual = True

        sprite_item = self._create_sprite_item(
            entity
        )

        if sprite_item is not None:
            group.addToGroup(
                sprite_item
            )

            has_visual = True

        camera_item = self._create_camera_item(
            entity
        )

        if camera_item is not None:
            group.addToGroup(
                camera_item
            )

            has_visual = True

        if self.colliders_visible:
            collider_item = (
                self._create_collider_item(
                    entity
                )
            )

            if collider_item is not None:
                group.addToGroup(
                    collider_item
                )

                has_visual = True

            area2d_item = (
                self._create_area2d_item(
                    entity
                )
            )

            if area2d_item is not None:
                group.addToGroup(
                    area2d_item
                )

                has_visual = True

            collision_group = (
                self._create_tilemap_collision_group(
                    entity
                )
            )

            if collision_group is not None:
                group.addToGroup(
                    collision_group
                )

                has_visual = True

        if not has_visual:
            empty_item = self._create_empty_item(
                entity
            )

            group.addToGroup(
                empty_item
            )

        return group

    def _load_tilemap(
        self,
        entity: SceneEntity,
    ):
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
            return TileMapSerializer().load(
                resource_path
            )

        except (
            OSError,
            ValueError,
            TypeError,
        ):
            return None

    def _create_tilemap_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsPixmapItem | None:
        tilemap = self._load_tilemap(
            entity
        )

        if (
            tilemap is None
            or not tilemap.tileset_asset_id
            or self.project_root is None
        ):
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

                if (
                    column < 0
                    or row < 0
                    or column >= tilemap.width
                    or row >= tilemap.height
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

                target_rect = QRectF(
                    column
                    * tilemap.tile_width,
                    row
                    * tilemap.tile_height,
                    tilemap.tile_width,
                    tilemap.tile_height,
                )

                painter.drawPixmap(
                    target_rect,
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

        transform = QTransform()

        transform.scale(
            entity.transform.scale_x,
            entity.transform.scale_y,
        )

        item.setTransform(
            transform
        )

        return item

    def _collision_layer(
        self,
        entity: SceneEntity,
    ) -> tuple[object, TileLayer] | None:
        tilemap = self._load_tilemap(
            entity
        )

        if tilemap is None:
            return None

        for layer in tilemap.layers:
            if (
                layer.name.strip().lower()
                == "collision"
            ):
                return (
                    tilemap,
                    layer,
                )

        return None

    def _create_tilemap_collision_group(
        self,
        entity: SceneEntity,
    ) -> QGraphicsItemGroup | None:
        result = self._collision_layer(
            entity
        )

        if result is None:
            return None

        tilemap, layer = result

        if not layer.cells:
            return None

        group = QGraphicsItemGroup()

        fill_color = QColor(
            255,
            70,
            70,
            75,
        )

        border_color = QColor(
            255,
            90,
            90,
            220,
        )

        pen = QPen(
            border_color,
            1,
        )

        pen.setCosmetic(
            True
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

            rect = QGraphicsRectItem(
                column
                * tilemap.tile_width,
                row
                * tilemap.tile_height,
                tilemap.tile_width,
                tilemap.tile_height,
            )

            rect.setPen(
                pen
            )

            rect.setBrush(
                fill_color
            )

            rect.setZValue(
                85000
            )

            group.addToGroup(
                rect
            )

        transform = QTransform()

        transform.scale(
            entity.transform.scale_x,
            entity.transform.scale_y,
        )

        group.setTransform(
            transform
        )

        group.setZValue(
            85000
        )

        return group

    def _create_sprite_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsPixmapItem | None:
        if (
            entity.sprite is None
            or self.project_root is None
        ):
            return None

        clip = None

        if (
            entity.animation is not None
            and entity.animation.enabled
        ):
            clip = entity.animation.default_clip()

        asset_id = str(
            getattr(
                clip,
                "asset_id",
                "",
            )
            or entity.sprite.asset_id
            or ""
        )

        if not asset_id:
            return None

        registry = AssetRegistry(
            self.project_root
        )

        record = registry.find_by_id(
            asset_id
        )

        if record is None:
            return None

        source = QPixmap(
            str(
                self.project_root
                / record.path
            )
        )

        if source.isNull():
            return None

        pixmap = self._scene_sprite_pixmap(
            entity,
            source,
        )

        if pixmap.isNull():
            pixmap = source

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
            -1.0 if entity.sprite.flip_x else 1.0,
            -1.0 if entity.sprite.flip_y else 1.0,
        )

        transform.scale(
            entity.transform.scale_x,
            entity.transform.scale_y,
        )

        item.setTransform(
            transform
        )

        return item

    def _scene_sprite_pixmap(
        self,
        entity: SceneEntity,
        source: QPixmap,
    ) -> QPixmap:
        """Retorna a pose estática exibida no editor de cena."""

        animation = entity.animation

        if (
            animation is None
            or not animation.enabled
        ):
            return source

        clip = animation.default_clip()

        if (
            clip is None
            or not clip.frames
        ):
            return source

        frame_id = clip.frames[0]

        if clip.regions:
            region = clip.region(
                frame_id
            )

            if region is None:
                for candidate in clip.frames:
                    region = clip.region(
                        candidate
                    )

                    if region is not None:
                        frame_id = candidate
                        break

            if region is None:
                return source

            return self._region_canvas_pixmap(
                source,
                clip,
                frame_id,
            )

        frame_width = max(
            1,
            int(
                animation.frame_width
            ),
        )

        frame_height = max(
            1,
            int(
                animation.frame_height
            ),
        )

        columns = (
            source.width()
            // frame_width
        )

        rows = (
            source.height()
            // frame_height
        )

        if (
            columns <= 0
            or rows <= 0
        ):
            return source

        if (
            frame_id < 0
            or frame_id >= columns * rows
        ):
            return source

        column = (
            frame_id
            % columns
        )

        row = (
            frame_id
            // columns
        )

        return source.copy(
            column * frame_width,
            row * frame_height,
            frame_width,
            frame_height,
        )

    @staticmethod
    def _region_canvas_pixmap(
        source: QPixmap,
        clip,
        frame_id: int,
    ) -> QPixmap:
        """Renderiza uma região em canvas lógico fixo."""

        region = clip.region(
            frame_id
        )

        if region is None:
            return QPixmap()

        frame_pixmap = source.copy(
            region.x,
            region.y,
            region.width,
            region.height,
        )

        if frame_pixmap.isNull():
            return QPixmap()

        max_width = 1
        max_height = 1
        max_offset_x = 0
        max_offset_y = 0

        for candidate in clip.regions.values():
            max_width = max(
                max_width,
                candidate.width,
            )

            max_height = max(
                max_height,
                candidate.height,
            )

            max_offset_x = max(
                max_offset_x,
                abs(
                    candidate.offset_x
                ),
            )

            max_offset_y = max(
                max_offset_y,
                abs(
                    candidate.offset_y
                ),
            )

        canvas_width = (
            max_width
            + max_offset_x * 2
        )

        canvas_height = (
            max_height
            + max_offset_y * 2
        )

        output = QPixmap(
            canvas_width,
            canvas_height,
        )

        output.fill(
            Qt.GlobalColor.transparent
        )

        center_x = (
            canvas_width
            // 2
        )

        bottom_y = canvas_height

        target_x = (
            center_x
            - frame_pixmap.width()
            // 2
            + region.offset_x
        )

        target_y = (
            bottom_y
            - frame_pixmap.height()
            + region.offset_y
        )

        painter = QPainter(
            output
        )

        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        painter.drawPixmap(
            target_x,
            target_y,
            frame_pixmap,
        )

        painter.end()

        return output

    def _create_camera_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsRectItem | None:
        camera = entity.camera

        if camera is None:
            return None

        width = (
            camera.width
            / camera.zoom
        )

        height = (
            camera.height
            / camera.zoom
        )

        item = QGraphicsRectItem(
            -width / 2
            + camera.offset_x,
            -height / 2
            + camera.offset_y,
            width,
            height,
        )

        if camera.active:
            color = QColor(
                "#55d6be"
            )

        else:
            color = QColor(
                "#4da3ff"
            )

        pen = QPen(
            color,
            2,
        )

        pen.setCosmetic(
            True
        )

        item.setPen(
            pen
        )

        item.setBrush(
            Qt.BrushStyle.NoBrush
        )

        item.setZValue(
            100000
        )

        return item

    def _create_collider_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsRectItem | None:
        collider = entity.collider

        if (
            collider is None
            or not collider.enabled
        ):
            return None

        item = QGraphicsRectItem(
            -collider.width / 2
            + collider.offset_x,
            -collider.height / 2
            + collider.offset_y,
            collider.width,
            collider.height,
        )

        if collider.solid:
            color = QColor(
                "#ff5f5f"
            )

        else:
            color = QColor(
                "#ffd34e"
            )

        pen = QPen(
            color,
            1,
        )

        pen.setCosmetic(
            True
        )

        pen.setStyle(
            Qt.PenStyle.DashLine
        )

        item.setPen(
            pen
        )

        fill = QColor(
            color
        )

        fill.setAlpha(
            35
        )

        item.setBrush(
            fill
        )

        item.setZValue(
            90000
        )

        return item

    def _create_area2d_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsRectItem | None:
        area = entity.area2d

        if (
            area is None
            or not area.enabled
            or not area.debug_visible
        ):
            return None

        item = QGraphicsRectItem(
            -area.width / 2.0
            + area.offset_x,
            -area.height / 2.0
            + area.offset_y,
            area.width,
            area.height,
        )

        color = QColor(
            "#45d7ff"
        )

        pen = QPen(
            color,
            1,
        )

        pen.setCosmetic(
            True
        )

        pen.setStyle(
            Qt.PenStyle.DashLine
        )

        item.setPen(
            pen
        )

        fill = QColor(
            color
        )

        fill.setAlpha(
            48
        )

        item.setBrush(
            fill
        )

        item.setZValue(
            90000
        )

        return item

    def _create_empty_item(
        self,
        entity: SceneEntity,
    ) -> QGraphicsItem:
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

        transform = QTransform()

        transform.scale(
            entity.transform.scale_x,
            entity.transform.scale_y,
        )

        item.setTransform(
            transform
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
        # A Hierarquia é a fonte de verdade da seleção.
        if self._active_entity_id is not None:
            return self._active_entity_id

        selected = (
            self.graphics_scene.selectedItems()
        )

        if not selected:
            return None

        value = selected[0].data(
            0
        )

        if not value:
            return None

        return str(
            value
        )

    def select_entity(
        self,
        entity_id: str,
    ) -> None:
        item = self.entity_items.get(
            entity_id
        )

        if item is None:
            return

        self._active_entity_id = str(
            entity_id
        )

        # Não usamos mais a seleção visual nativa do QGraphicsScene.
        # Isso evita o retângulo de seleção ao redor da entidade.
        # O ID ativo é suficiente para permitir o arraste manual.
        self.graphics_scene.clearSelection()

    def mousePressEvent(
        self,
        event,
    ) -> None:
        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            super().mousePressEvent(
                event
            )
            return

        if self.resource is None:
            event.accept()
            return

        scene_position = self.mapToScene(event.position().toPoint())
        clicked = self.graphics_scene.itemAt(scene_position, QTransform())
        while clicked is not None and clicked.data(0) is None:
            clicked = clicked.parentItem()
        if clicked is not None and clicked.data(0) is not None:
            self._active_entity_id = str(clicked.data(0))
            self.entity_selected.emit(self._active_entity_id)

        entity_id = self._active_entity_id
        if entity_id is None:
            event.accept()
            return

        entity = self.resource.entity(
            entity_id
        )

        item = self.entity_items.get(
            entity_id
        )

        if (
            entity is None
            or item is None
        ):
            event.accept()
            return

        # TileMap permanece bloqueado para movimento no viewport.
        if entity.tilemap is not None:
            event.accept()
            return

        scene_position = self.mapToScene(
            event.position().toPoint()
        )

        self._drag_offset = (
            scene_position
            - item.pos()
        )

        self._dragging_entity = True

        event.accept()

    def mouseMoveEvent(
        self,
        event,
    ) -> None:
        if not self._dragging_entity:
            super().mouseMoveEvent(
                event
            )
            return

        entity_id = self._active_entity_id

        if entity_id is None:
            return

        item = self.entity_items.get(
            entity_id
        )

        if item is None:
            return

        scene_position = self.mapToScene(
            event.position().toPoint()
        )

        item.setPos(
            scene_position
            - self._drag_offset
        )

        event.accept()

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:
        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            super().mouseReleaseEvent(
                event
            )
            return

        if not self._dragging_entity:
            event.accept()
            return

        self._dragging_entity = False

        entity_id = self._active_entity_id

        if entity_id is None:
            event.accept()
            return

        item = self.entity_items.get(
            entity_id
        )

        if item is None:
            event.accept()
            return

        position = item.pos()

        self.entity_moved.emit(
            entity_id,
            position.x(),
            position.y(),
        )

        event.accept()

    def _on_graphics_selection_changed(
        self,
    ) -> None:
        entity_id = (
            self.selected_entity_id()
        )

        if entity_id is None:
            return

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

        painter.fillRect(
            self.editor_rect,
            QColor("#202225"),
        )

        if self.grid_visible:
            grid = max(
                1,
                self.grid_size,
            )

            visible = rect.intersected(
                self.editor_rect
            )

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

            first_x = (
                int(
                    visible.left()
                    // grid
                )
                * grid
            )

            last_x = (
                int(
                    visible.right()
                    // grid
                )
                * grid
                + grid
            )

            first_y = (
                int(
                    visible.top()
                    // grid
                )
                * grid
            )

            last_y = (
                int(
                    visible.bottom()
                    // grid
                )
                * grid
                + grid
            )

            x = first_x

            while x <= last_x:
                painter.drawLine(
                    QPointF(
                        x,
                        visible.top(),
                    ),
                    QPointF(
                        x,
                        visible.bottom(),
                    ),
                )

                x += grid

            y = first_y

            while y <= last_y:
                painter.drawLine(
                    QPointF(
                        visible.left(),
                        y,
                    ),
                    QPointF(
                        visible.right(),
                        y,
                    ),
                )

                y += grid

        output_rect = QRectF(
            0,
            0,
            self.scene_width,
            self.scene_height,
        )

        output_pen = QPen(
            QColor(
                93,
                209,
                255,
                230,
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


class SceneViewport(QWidget):
    """Editor visual da Scene."""

    entity_selected = Signal(str)

    entity_moved = Signal(
        str,
        float,
        float,
    )

    def __init__(self) -> None:
        super().__init__()

        self.resource: SceneResource | None = None
        self.project_root: Path | None = None

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

        self.colliders_checkbox = QCheckBox(
            "Mostrar Colliders"
        )

        self.colliders_checkbox.setChecked(
            True
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
            self.colliders_checkbox
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

        self.colliders_checkbox.toggled.connect(
            self.canvas.set_colliders_visible
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
        self.project_root = (
            project_root.resolve()
        )

        self.resource = resource

        self.title.setText(
            resource.name
        )

        # =========================================================
        # RESOLUÇÃO DE SAÍDA
        # =========================================================
        #
        # A Scene continua possuindo um workspace grande e livre.
        # A resolução do projeto define somente o retângulo azul
        # que representa a área exibida ao jogador.
        #
        # Lupi:
        #   480 × 270 fixo
        #
        # PC:
        #   resolução configurada no lupix.project
        #
        output_width = resource.width
        output_height = resource.height
        platform_label = "Scene"

        try:
            project = load_project(
                self.project_root
            )

            output_width = project.width
            output_height = project.height

            platform_label = (
                "Lupi"
                if project.platform == "lupi"
                else "PC"
            )

        except (
            OSError,
            ValueError,
            TypeError,
        ):
            # Compatibilidade com cenas/projetos antigos:
            # se o lupix.project não puder ser carregado,
            # utilizamos a resolução armazenada na própria Scene.
            pass

        self.resolution_label.setText(
            f"Saída {platform_label}: "
            f"{output_width} × {output_height}"
        )

        # Primeiro carrega todos os elementos e entidades da Scene.
        self.canvas.set_resource(
            self.project_root,
            resource,
        )

        # Depois substitui somente a área de saída pela resolução
        # real configurada no projeto. O editor_rect permanece grande.
        self.canvas.set_scene_size(
            output_width,
            output_height,
        )

        self.canvas.set_colliders_visible(
            self.colliders_checkbox.isChecked()
        )

        self._update_grid()
        self._update_zoom()

        # O QGraphicsView possui uma sceneRect muito maior que a área
        # de saída. Ao abrir a Scene, centralizamos explicitamente o
        # retângulo 0..width / 0..height que representa a tela do jogo.
        #
        # singleShot(0, ...) espera o layout terminar de calcular o
        # tamanho real do viewport antes de posicionar a visualização.
        QTimer.singleShot(
            0,
            self.canvas.center_scene,
        )

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