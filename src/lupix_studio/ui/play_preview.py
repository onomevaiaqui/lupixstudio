from __future__ import annotations

from pathlib import Path
from time import monotonic

from PySide6.QtCore import (
    QRectF,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QKeyEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QGraphicsItemGroup,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRegistry
from lupix_studio.runtime import SceneRuntime
from lupix_studio.runtime.flowchart_runtime import FlowchartRuntime
from lupix_studio.scene.model import (
    SceneEntity,
    SceneResource,
)
from lupix_studio.scene.serializer import SceneSerializer
from lupix_studio.tilemap.serializer import (
    TileMapSerializer,
)
from lupix_studio.ui_theme import UITheme


class PlayCanvas(QGraphicsView):
    """Canvas de execução da cena."""

    continue_requested = Signal()
    end_requested = Signal()
    ui_action_requested = Signal(str, str)
    flow_key_pressed = Signal(str)

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
        self.ui_theme = UITheme()
        self._theme_font_family = ""
        self._pressed_ui_item = None
        self._pressed_ui_entity_id: str | None = None
        self._hovered_ui_item = None
        self.setMouseTracking(True)

        self.follow_active_camera = True

        self._camera_center_x: float | None = None
        self._camera_center_y: float | None = None
        self._camera_last_time = monotonic()

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

        self.health_label = QLabel(self.viewport())
        self.health_label.setObjectName("PlayerHealthHUD")
        self.health_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.health_label.setStyleSheet(
            "QLabel#PlayerHealthHUD { color: #ffffff;"
            " background-color: rgba(8, 14, 26, 210);"
            " border: 1px solid #d5ad38; border-radius: 6px;"
            " padding: 7px 11px; font-size: 14px;"
            " font-weight: 700; }"
        )
        self.health_label.hide()

        self.dialogue_label = QLabel(
            self.viewport()
        )

        self.dialogue_label.setObjectName(
            "PlayDialogue"
        )

        self.dialogue_label.setWordWrap(
            True
        )

        self.dialogue_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.dialogue_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self.dialogue_label.setStyleSheet(
            "QLabel#PlayDialogue {"
            " color: #ffffff;"
            " background-color: rgba(8, 14, 26, 230);"
            " border: 2px solid #d5ad38;"
            " border-radius: 8px;"
            " padding: 12px 16px;"
            " font-size: 15px;"
            " font-weight: 600;"
            " }"
        )

        self.dialogue_label.hide()

        self.dialogue_timer = QTimer(
            self
        )

        self.dialogue_timer.setSingleShot(
            True
        )

        self.dialogue_timer.timeout.connect(
            self.hide_message
        )

        self.death_overlay = QLabel(self.viewport())
        self.death_overlay.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.death_overlay.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.death_overlay.hide()
        self.death_transition_timer = QTimer(self)
        self.death_transition_timer.setInterval(16)
        self.death_transition_timer.timeout.connect(
            self._update_death_transition
        )
        self._death_started_at = 0.0
        self._death_respawn_delay = 1.0
        self._death_fade_duration = 0.35
        self._death_requires_confirmation = False
        self._death_exiting = False
        self.continue_button = QPushButton("Sim", self.viewport())
        self.end_button = QPushButton("Não", self.viewport())
        for button in (self.continue_button, self.end_button):
            button.setFixedSize(110, 38)
            button.setStyleSheet(
                "QPushButton { color: white; background: #252a34;"
                " border: 1px solid #8f98a8; border-radius: 6px;"
                " font-size: 15px; font-weight: 600; }"
                "QPushButton:hover, QPushButton:focus {"
                " background: #d5ad38; color: #111216; }"
            )
            button.hide()
        self.continue_button.clicked.connect(self.continue_requested.emit)
        self.end_button.clicked.connect(self.end_requested.emit)

    def start_death_transition(
        self, text: str, respawn_delay: float, fade_duration: float,
        require_confirmation: bool = False,
    ) -> None:
        self.death_transition_timer.stop()
        self._death_started_at = monotonic()
        self._death_respawn_delay = max(0.0, float(respawn_delay))
        self._death_fade_duration = max(0.05, float(fade_duration))
        self._death_requires_confirmation = bool(require_confirmation)
        self._death_exiting = False
        self.continue_button.hide()
        self.end_button.hide()
        prompt = (
            f"{text}\n\n{self.ui_theme.continue_prompt}"
            if require_confirmation else text
        )
        self.death_overlay.setText(prompt)
        self.death_overlay.setGeometry(self.viewport().rect())
        self.death_overlay.show()
        self.death_overlay.raise_()
        self.death_transition_timer.start()
        self._update_death_transition()

    def stop_death_transition(self) -> None:
        self.death_transition_timer.stop()
        self.death_overlay.hide()
        self.continue_button.hide()
        self.end_button.hide()
        self._death_exiting = False

    def complete_death_transition(self) -> None:
        self.continue_button.hide()
        self.end_button.hide()
        self._death_exiting = True
        self._death_started_at = monotonic()
        self.death_transition_timer.start()

    def _position_death_buttons(self) -> None:
        center_x = self.viewport().width() // 2
        y = self.viewport().height() // 2 + 55
        self.continue_button.move(center_x - 120, y)
        self.end_button.move(center_x + 10, y)

    def _update_death_transition(self) -> None:
        elapsed = monotonic() - self._death_started_at
        fade = self._death_fade_duration
        if self._death_exiting:
            alpha = int(235 * max(0.0, 1.0 - elapsed / fade))
            if elapsed >= fade:
                self.stop_death_transition()
                return
            self.death_overlay.setStyleSheet(
                "QLabel { background-color: rgba(0, 0, 0, "
                f"{alpha}); color: rgba(255, 255, 255, {alpha});"
                " font-size: 28px; font-weight: 700; }"
            )
            return
        flash_duration = 0.12
        fade_out_start = max(
            flash_duration + fade, self._death_respawn_delay
        )
        if elapsed < flash_duration:
            alpha = int(115 * (1.0 - elapsed / flash_duration))
            background = f"rgba(170, 20, 30, {alpha})"
            color = "rgba(255, 255, 255, 0)"
        elif elapsed < flash_duration + fade:
            progress = (elapsed - flash_duration) / fade
            alpha = int(235 * min(1.0, progress))
            background = f"rgba(0, 0, 0, {alpha})"
            color = f"rgba(255, 255, 255, {alpha})"
        elif self._death_requires_confirmation:
            background = "rgba(0, 0, 0, 235)"
            color = "rgba(255, 255, 255, 255)"
            if elapsed >= self._death_respawn_delay:
                self._position_death_buttons()
                self.continue_button.show()
                self.end_button.show()
                self.continue_button.raise_()
                self.end_button.raise_()
                self.continue_button.setFocus()
        elif elapsed < fade_out_start:
            background = "rgba(0, 0, 0, 235)"
            color = "rgba(255, 255, 255, 255)"
        elif elapsed < fade_out_start + fade:
            progress = (elapsed - fade_out_start) / fade
            alpha = int(235 * max(0.0, 1.0 - progress))
            background = f"rgba(0, 0, 0, {alpha})"
            color = f"rgba(255, 255, 255, {alpha})"
        else:
            self.stop_death_transition()
            return
        self.death_overlay.setStyleSheet(
            "QLabel {"
            f" background-color: {background}; color: {color};"
            + self._death_image_css()
            + f" font-size: {self.ui_theme.death_font_size}px; font-weight: 700;"
            " letter-spacing: 1px; }"
        )

    def apply_ui_theme(self, theme: UITheme) -> None:
        self.ui_theme = theme
        self._theme_font_family = ""
        font_path = theme.asset(theme.font)
        if font_path:
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                self._theme_font_family = families[0]
        family = (
            f"font-family: '{self._theme_font_family}';"
            if self._theme_font_family else ""
        )
        hud_image = theme.asset(theme.hud_background_image)
        hud_asset = f"border-image: url('{hud_image}') 8 8 8 8 stretch stretch;" if hud_image else ""
        self.health_label.setStyleSheet(
            "QLabel#PlayerHealthHUD {" + family
            + f"color: {theme.hud_text_color}; background-color: {theme.hud_background_color};"
            + f"font-size: {theme.hud_font_size}px; font-weight: 700;"
            + f"border: 1px solid {theme.accent_color}; border-radius: 6px; padding: 7px 11px;"
            + hud_asset + "}"
        )
        normal_image = theme.asset(theme.button_background_image)
        selected_image = theme.asset(theme.button_selected_image)
        normal_asset = f"border-image: url('{normal_image}') 8 8 8 8 stretch stretch;" if normal_image else ""
        selected_asset = f"border-image: url('{selected_image}') 8 8 8 8 stretch stretch;" if selected_image else ""
        button_style = (
            "QPushButton {" + family
            + f"color: {theme.button_text_color}; background: {theme.button_background_color};"
            + f"font-size: {theme.button_font_size}px; font-weight: 600; border: 1px solid #8f98a8; border-radius: 6px;"
            + normal_asset + "}"
            + "QPushButton:hover, QPushButton:focus {"
            + f"background: {theme.button_selected_color};" + selected_asset + "}"
        )
        self.continue_button.setText(theme.yes_text)
        self.end_button.setText(theme.no_text)
        self.continue_button.setStyleSheet(button_style)
        self.end_button.setStyleSheet(button_style)

    def _death_image_css(self) -> str:
        image = self.ui_theme.asset(self.ui_theme.death_background_image)
        return f"background-image: url('{image}'); background-position: center;" if image else ""

    def update_health_hud(
        self, health: int, maximum: int, visible: bool
    ) -> None:
        if not visible or maximum <= 0:
            self.health_label.hide()
            return
        health = max(0, min(int(health), int(maximum)))
        self.health_label.setText(
            f"{self.ui_theme.hud_label}  {health} / {maximum}"
        )
        self.health_label.adjustSize()
        self.health_label.move(18, 18)
        self.health_label.show()
        self.health_label.raise_()

    def show_message(
        self,
        text: str,
        duration_ms: int = 4000,
    ) -> None:
        message = text.strip()

        if not message:
            return

        self.dialogue_label.setText(
            message
        )

        self._position_dialogue()

        self.dialogue_label.show()
        self.dialogue_label.raise_()

        self.dialogue_timer.start(
            max(
                500,
                int(duration_ms),
            )
        )

    def hide_message(
        self,
    ) -> None:
        self.dialogue_timer.stop()
        self.dialogue_label.hide()

    def _position_dialogue(
        self,
    ) -> None:
        viewport = self.viewport()
        margin = 18

        width = max(
            240,
            min(
                720,
                viewport.width()
                - margin * 2,
            ),
        )

        self.dialogue_label.setFixedWidth(
            width
        )

        self.dialogue_label.adjustSize()

        height = max(
            64,
            self.dialogue_label.height(),
        )

        self.dialogue_label.setFixedHeight(
            height
        )

        x = max(
            margin,
            (
                viewport.width()
                - width
            ) // 2,
        )

        y = max(
            margin,
            viewport.height()
            - height
            - 24,
        )

        self.dialogue_label.move(
            x,
            y,
        )

    def resizeEvent(
        self,
        event,
    ) -> None:
        super().resizeEvent(
            event
        )

        if self.dialogue_label.isVisible():
            self._position_dialogue()
        if self.death_overlay.isVisible():
            self.death_overlay.setGeometry(self.viewport().rect())
            self._position_death_buttons()
        if self._is_interface_scene():
            self._fit_interface_scene()

    def set_runtime(
        self,
        project_root: Path,
        runtime: SceneRuntime,
    ) -> None:
        self.hide_message()
        self.health_label.hide()
        self.stop_death_transition()

        self.project_root = (
            project_root.resolve()
        )

        self.apply_ui_theme(UITheme.load(self.project_root))
        self.runtime = runtime

        self.rebuild()

    def rebuild(self) -> None:
        self.graphics_scene.clear()
        self.entity_items.clear()

        self._camera_center_x = None
        self._camera_center_y = None
        self._camera_last_time = monotonic()

        if self.runtime is None:
            return

        scene = self.runtime.scene

        #
        # O QGraphicsScene do Play precisa representar o MUNDO,
        # não somente a resolução de saída.
        #
        # Exemplo:
        #   saída Lupi = 480 x 270
        #   fase       = 2400 x 540
        #
        # A câmera continua enxergando somente 480 x 270,
        # mas pode se deslocar por todo o world_rect.
        #
        if str(scene.type).strip().lower() == "interface":
            world_left = 0.0
            world_top = 0.0
            world_right = float(scene.width)
            world_bottom = float(scene.height)
        else:
            world_left = float(self.runtime.world_left)
            world_top = float(self.runtime.world_top)
            world_right = float(self.runtime.world_right)
            world_bottom = float(self.runtime.world_bottom)

        world_width = max(
            1.0,
            world_right - world_left,
        )

        world_height = max(
            1.0,
            world_bottom - world_top,
        )

        world_rect = QRectF(
            world_left,
            world_top,
            world_width,
            world_height,
        )

        #
        # Uma pequena margem evita que o QGraphicsView restrinja
        # centerOn() exatamente nas bordas do mundo.
        #
        margin = max(
            256.0,
            float(scene.width),
            float(scene.height),
        )

        self.graphics_scene.setSceneRect(
            world_rect.adjusted(
                -margin,
                -margin,
                margin,
                margin,
            )
        )

        background = QGraphicsRectItem(
            world_rect
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

        self.fit_camera()

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

            if (
                isinstance(
                    item,
                    QGraphicsPixmapItem,
                )
                and entity.sprite is not None
            ):
                self._refresh_sprite_visual(
                    entity,
                    item,
                )

        if self.follow_active_camera:
            self.fit_camera()

    def _is_interface_scene(self) -> bool:
        if self.runtime is None:
            return False
        scene = self.runtime.scene
        declared_type = str(scene.type).strip().lower()
        if declared_type in {"interface", "ui", "menu"}:
            return True

        # Cenas criadas pelo fluxo comum também podem ser telas de UI.
        # Se possuem Elemento UI e não possuem componentes de mundo,
        # devem usar a resolução fixa da cena no Preview.
        has_ui_elements = any(
            entity.ui_element is not None for entity in scene.entities
        )
        has_world_elements = any(
            entity.player_controller is not None
            or entity.camera is not None
            or entity.tilemap is not None
            for entity in scene.entities
        )
        return has_ui_elements and not has_world_elements

    def _fit_interface_scene(self) -> None:
        if self.runtime is None:
            return
        scene = self.runtime.scene
        rect = QRectF(0.0, 0.0, float(scene.width), float(scene.height))
        self.graphics_scene.setSceneRect(rect)
        self.resetTransform()
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(rect.center())

    def fit_scene(self) -> None:
        if self.runtime is None:
            return

        self.follow_active_camera = False
        if self._is_interface_scene():
            self._fit_interface_scene()
            return

        world_left = self.runtime.world_left
        world_top = self.runtime.world_top
        world_right = self.runtime.world_right
        world_bottom = self.runtime.world_bottom

        self.fitInView(
            QRectF(
                world_left,
                world_top,
                max(1.0, world_right - world_left),
                max(1.0, world_bottom - world_top),
            ),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def fit_camera(self) -> None:
        if self.runtime is None:
            return

        if self._is_interface_scene():
            self.follow_active_camera = False
            self._fit_interface_scene()
            return

        scene = self.runtime.scene
        camera_entity = scene.active_camera()

        if camera_entity is None or camera_entity.camera is None:
            self.fit_scene()
            return

        camera = camera_entity.camera
        zoom = max(0.01, float(camera.zoom))
        visible_width = max(1.0, float(camera.width) / zoom)
        visible_height = max(1.0, float(camera.height) / zoom)

        player = self.runtime.player
        if player is not None:
            target_x = player.transform.x
            target_y = player.transform.y
        else:
            target_x = camera_entity.transform.x
            target_y = camera_entity.transform.y

        world_left = self.runtime.world_left
        world_top = self.runtime.world_top
        world_right = self.runtime.world_right
        world_bottom = self.runtime.world_bottom

        world_width = max(1.0, world_right - world_left)
        world_height = max(1.0, world_bottom - world_top)

        if visible_width < world_width:
            half_width = visible_width / 2.0
            center_x = max(
                world_left + half_width,
                min(world_right - half_width, target_x),
            )
        else:
            center_x = (world_left + world_right) / 2.0
            visible_width = world_width

        if visible_height < world_height:
            half_height = visible_height / 2.0
            center_y = max(
                world_top + half_height,
                min(world_bottom - half_height, target_y),
            )
        else:
            center_y = (world_top + world_bottom) / 2.0
            visible_height = world_height

        camera_rect = QRectF(
            center_x - visible_width / 2.0,
            center_y - visible_height / 2.0,
            visible_width,
            visible_height,
        )

        self.fitInView(
            camera_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.centerOn(center_x, center_y)

    def use_active_camera(self) -> None:
        self.follow_active_camera = True
        self.fit_camera()

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
        item.setData(0, entity.id)
        if entity.ui_element is not None:
            item.setZValue(float(entity.ui_element.get("layer", 0)))

        self.graphics_scene.addItem(
            item
        )

        self.entity_items[
            entity.id
        ] = item

    @staticmethod
    def _button_rect(item):
        pending = list(item.childItems())
        while pending:
            child = pending.pop()
            if isinstance(child, QGraphicsRectItem):
                return child
            pending.extend(child.childItems())
        return None

    def _set_button_state(self, item, state: str) -> None:
        if self.runtime is None or item is None:
            return
        entity = self.runtime.scene.entity(str(item.data(0) or ""))
        data = entity.ui_element if entity is not None else None
        rect = self._button_rect(item)
        if data is None or rect is None:
            return
        label = next(
            (child for child in item.childItems() if isinstance(child, QGraphicsTextItem)),
            None,
        )
        if label is not None:
            label.setDefaultTextColor(QColor(str(data.get(
                f"button_text_{state}_color", data.get("color", "#ffffff")
            ))))
        border = QColor(str(data.get("button_border_color", "#d5ad38")))
        border.setAlphaF(max(0.0, min(1.0, float(data.get("button_border_opacity", 100)) / 100.0)))
        rect.setPen(QPen(border, 2.0))
        opacity = max(0.0, min(1.0, float(data.get("button_opacity", 100)) / 100.0))
        rect.setOpacity(1.0)
        if bool(data.get("button_transparent", False)) or opacity <= 0.0:
            rect.setBrush(Qt.BrushStyle.NoBrush)
            return
        image_path = str(data.get(f"button_{state}_image", "") or "")
        if image_path and self.project_root is not None:
            pixmap = QPixmap(str((self.project_root / image_path).resolve()))
            if not pixmap.isNull():
                rect.setBrush(QBrush(pixmap.scaled(
                    rect.rect().size().toSize(), Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )))
                rect.setOpacity(opacity)
                return
        background = QColor(str(data.get(f"button_{state}_color", "#252a34")))
        background.setAlphaF(opacity)
        rect.setBrush(background)

    def mouseMoveEvent(self, event) -> None:
        scene_pos = self.mapToScene(event.position().toPoint())
        item = self.graphics_scene.itemAt(scene_pos, self.transform())
        while item is not None and item.data(0) is None:
            item = item.parentItem()
        hovered = None
        if item is not None and self.runtime is not None:
            entity = self.runtime.scene.entity(str(item.data(0) or ""))
            data = entity.ui_element if entity is not None else None
            if data is not None and str(data.get("type", "")) == "button":
                hovered = item
        if hovered is not self._hovered_ui_item:
            if self._hovered_ui_item is not None and self._hovered_ui_item is not self._pressed_ui_item:
                self._set_button_state(self._hovered_ui_item, "normal")
            self._hovered_ui_item = hovered
            if hovered is not None and hovered is not self._pressed_ui_item:
                self._set_button_state(hovered, "hover")
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.runtime is not None:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            scene_pos = self.mapToScene(event.position().toPoint())
            item = self.graphics_scene.itemAt(scene_pos, self.transform())
            while item is not None and item.data(0) is None:
                item = item.parentItem()
            if item is not None:
                entity_id = str(item.data(0) or "")
                entity = self.runtime.scene.entity(entity_id)
                data = entity.ui_element if entity is not None else None
                if data is not None and str(data.get("type", "")) == "button":
                    self._pressed_ui_item = item
                    self._pressed_ui_entity_id = entity_id
                    item.setScale(0.96)
                    self._set_button_state(item, "pressed")
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._pressed_ui_item is not None:
            item = self._pressed_ui_item
            entity_id = self._pressed_ui_entity_id or ""
            self._pressed_ui_item = None
            self._pressed_ui_entity_id = None
            item.setScale(1.0)
            self._set_button_state(
                item, "hover" if item is self._hovered_ui_item else "normal"
            )
            scene_pos = self.mapToScene(event.position().toPoint())
            released = self.graphics_scene.itemAt(scene_pos, self.transform())
            while released is not None and released.data(0) is None:
                released = released.parentItem()
            if released is item and self.runtime is not None:
                entity = self.runtime.scene.entity(entity_id)
                data = entity.ui_element if entity is not None else None
                if data is not None:
                    self.ui_action_requested.emit(
                        str(data.get("action", "none")),
                        str(data.get("target_scene", "")),
                    )
            event.accept()
            return
        super().mouseReleaseEvent(event)

    @staticmethod
    def _flow_key_name(key: int) -> str:
        keys = {
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_Return: "enter",
            Qt.Key.Key_Enter: "enter",
            Qt.Key.Key_Left: "left",
            Qt.Key.Key_Right: "right",
            Qt.Key.Key_Up: "up",
            Qt.Key.Key_Down: "down",
            Qt.Key.Key_A: "a",
            Qt.Key.Key_D: "d",
            Qt.Key.Key_W: "w",
            Qt.Key.Key_S: "s",
            Qt.Key.Key_E: "e",
            Qt.Key.Key_F: "f",
        }
        return keys.get(Qt.Key(key), "")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not event.isAutoRepeat():
            key_name = self._flow_key_name(event.key())
            if key_name:
                self.flow_key_pressed.emit(key_name)
        if self.runtime is None:
            super().keyPressEvent(event)
            return
        key = event.key()
        if key in (Qt.Key.Key_A, Qt.Key.Key_Left):
            self.runtime.input.left = True
            event.accept()
            return
        if key in (Qt.Key.Key_D, Qt.Key.Key_Right):
            self.runtime.input.right = True
            event.accept()
            return
        if key in (Qt.Key.Key_Space, Qt.Key.Key_Up, Qt.Key.Key_W):
            self.runtime.input.jump = True
            event.accept()
            return
        if key == Qt.Key.Key_Escape:
            self.end_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if self.runtime is None:
            super().keyReleaseEvent(event)
            return
        if event.isAutoRepeat():
            event.accept()
            return
        key = event.key()
        if key in (Qt.Key.Key_A, Qt.Key.Key_Left):
            self.runtime.input.left = False
            event.accept()
            return
        if key in (Qt.Key.Key_D, Qt.Key.Key_Right):
            self.runtime.input.right = False
            event.accept()
            return
        if key in (Qt.Key.Key_Space, Qt.Key.Key_Up, Qt.Key.Key_W):
            self.runtime.input.jump = False
            event.accept()
            return
        super().keyReleaseEvent(event)

    def focusOutEvent(self, event) -> None:
        if self.runtime is not None:
            self.runtime.input.left = False
            self.runtime.input.right = False
            self.runtime.input.jump = False
        super().focusOutEvent(event)

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

    def _create_visual(
        self,
        entity: SceneEntity,
    ):
        ui_item = self._create_ui_element_item(entity)
        if ui_item is not None:
            return ui_item

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
        pixmap = self._sprite_pixmap_for_entity(
            entity
        )

        if pixmap is None:
            return None

        item = QGraphicsPixmapItem(
            pixmap
        )

        self._apply_sprite_item_settings(
            entity,
            item,
            pixmap,
        )

        return item

    def _refresh_sprite_visual(
        self,
        entity: SceneEntity,
        item: QGraphicsPixmapItem,
    ) -> None:
        pixmap = self._sprite_pixmap_for_entity(
            entity
        )

        if pixmap is None:
            return

        item.setPixmap(
            pixmap
        )

        self._apply_sprite_item_settings(
            entity,
            item,
            pixmap,
        )

    def _sprite_pixmap_for_entity(
        self,
        entity: SceneEntity,
    ) -> QPixmap | None:
        if (
            entity.sprite is None
            or self.project_root is None
        ):
            return None

        clip = None

        if (
            self.runtime is not None
            and entity.animation is not None
            and entity.animation.enabled
        ):
            clip_name = self.runtime.animation_name_for(
                entity.id
            )

            if not clip_name:
                clip_name = entity.animation.default_animation

            clip = entity.animation.clip(
                clip_name
            )

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

        if clip is None:
            return source

        if not clip.frames:
            if clip.regions:
                first_region_id = next(
                    iter(
                        clip.regions
                    )
                )

                return self._region_canvas_pixmap(
                    source,
                    clip,
                    first_region_id,
                )

            return source

        frame_id = self.runtime.animation_frame_for(
            entity.id
        )

        if clip.regions:
            resolved_frame_id = frame_id
            region = clip.region(
                resolved_frame_id
            )

            if region is None:
                for candidate in clip.frames:
                    candidate_region = clip.region(
                        candidate
                    )

                    if candidate_region is not None:
                        resolved_frame_id = candidate
                        region = candidate_region
                        break

            if region is None:
                return QPixmap()

            return self._region_canvas_pixmap(
                source,
                clip,
                resolved_frame_id,
            )

        animation = entity.animation

        if animation is None:
            return source

        frame_width = max(
            1,
            int(animation.frame_width),
        )

        frame_height = max(
            1,
            int(animation.frame_height),
        )

        columns = source.width() // frame_width
        rows = source.height() // frame_height

        if columns <= 0 or rows <= 0:
            return source

        if frame_id < 0 or frame_id >= columns * rows:
            return source

        column = frame_id % columns
        row = frame_id // columns

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
        """
        Renderiza uma região em um canvas lógico fixo.

        Todas as poses:
        - mantêm a escala original;
        - usam o mesmo canvas;
        - ficam alinhadas pela base central.
        """

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

        bottom_y = (
            canvas_height
        )

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

    @staticmethod
    def _apply_sprite_item_settings(
        entity: SceneEntity,
        item: QGraphicsPixmapItem,
        pixmap: QPixmap,
    ) -> None:
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

        transform = item.transform()

        scale_x = (
            entity.transform.scale_x
            * (
                -1.0
                if entity.sprite.flip_x
                else 1.0
            )
        )

        scale_y = (
            entity.transform.scale_y
            * (
                -1.0
                if entity.sprite.flip_y
                else 1.0
            )
        )

        transform.setMatrix(
            scale_x,
            0.0,
            0.0,
            0.0,
            scale_y,
            0.0,
            0.0,
            0.0,
            1.0,
        )

        item.setTransform(
            transform
        )

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
    area_event = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.runtime: SceneRuntime | None = None
        self.flow_runtime: FlowchartRuntime | None = None

        self.active_area_sequences: set[str] = set()
        self.scene_serializer = SceneSerializer()

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
        self.canvas.continue_requested.connect(
            self._continue_after_death
        )
        self.canvas.end_requested.connect(self.stop)
        self.canvas.ui_action_requested.connect(self._run_ui_action)
        self.canvas.flow_key_pressed.connect(self._on_flow_key_pressed)

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
            self.canvas.use_active_camera
        )

    def start(
        self,
        project_root: Path,
        scene: SceneResource,
    ) -> None:
        self.stop_runtime()

        self.active_area_sequences.clear()

        self.project_root = (
            project_root.resolve()
        )

        self.runtime = SceneRuntime(
            scene,
            project_root=self.project_root,
        )

        self.runtime.start()
        self.flow_runtime = FlowchartRuntime(
            scene,
            self._show_flow_message,
            self._change_flow_scene,
            self._play_flow_animation,
        )
        self.flow_runtime.start()

        self.canvas.set_runtime(
            self.project_root,
            self.runtime,
        )

        self.status_label.setText(
            "Executando"
        )

        self.timer.start()

        self.canvas.setFocus()

    def _on_flow_key_pressed(self, key_name: str) -> None:
        if self.flow_runtime is not None:
            self.flow_runtime.trigger_key(key_name)

    def _show_flow_message(
        self,
        entity_name: str,
        message: str,
        duration_ms: int,
    ) -> None:
        self.area_event.emit(f"Flowchart ({entity_name}): {message}")
        self.canvas.show_message(message, duration_ms)

    def _play_flow_animation(
        self,
        entity_id: str,
        entity_name: str,
        animation_name: str,
    ) -> bool:
        if self.runtime is None:
            return False
        played = self.runtime.play_flow_animation(entity_id, animation_name)
        if played:
            self.area_event.emit(
                f"Flowchart ({entity_name}): animação {animation_name}"
            )
        else:
            self.area_event.emit(
                f"Flowchart ({entity_name}): animação indisponível"
            )
        return played

    def _change_flow_scene(
        self,
        entity_name: str,
        target_scene: str,
    ) -> bool:
        self.area_event.emit(
            f"Flowchart ({entity_name}): trocar para {target_scene}"
        )
        return self._change_scene(target_scene)

    def _run_ui_action(self, action: str, target_scene: str) -> None:
        if action == "continue_game":
            self._continue_after_death()
        elif action == "restart_scene" and self.runtime is not None and self.project_root is not None:
            self.start(self.project_root, self.runtime.scene)
        elif action == "change_scene" and target_scene.strip():
            self._change_scene(target_scene.strip())
        elif action == "quit":
            self.stop()

    def _continue_after_death(self) -> None:
        if self.runtime is None:
            return
        if self.runtime.respawn_player_now():
            self.canvas.complete_death_transition()
            self.canvas.setFocus()
            self.area_event.emit("Respawn confirmado.")

    def stop_runtime(self) -> None:
        self.timer.stop()

        if self.runtime is not None:
            self.runtime.stop()
        if self.flow_runtime is not None:
            self.flow_runtime.stop()

        self.runtime = None
        self.flow_runtime = None

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
        if self.flow_runtime is not None:
            self.flow_runtime.update(1.0 / 60.0)

        player = self.runtime.player
        controller = (
            player.player_controller if player is not None else None
        )
        self.canvas.update_health_hud(
            self.runtime.player_health(),
            self.runtime.player_max_health(),
            bool(controller and controller.show_health_hud),
        )

        for area_event in (
            self.runtime.consume_area_events()
        ):
            area_entity = (
                self.runtime.scene.entity(
                    area_event.area_id
                )
            )

            area_name = (
                area_entity.name
                if area_entity is not None
                else area_event.area_id
            )

            if area_event.event == "entered":
                message = (
                    f"Area2D entered: {area_name}"
                )
            elif area_event.event == "exited":
                message = (
                    f"Area2D exited: {area_name}"
                )
            else:
                message = (
                    f"Area2D {area_event.event}: "
                    f"{area_name}"
                )

            self.area_event.emit(
                message
            )

            if (
                area_event.event != "entered"
                or area_entity is None
                or area_entity.area2d is None
            ):
                continue

            actions = list(
                area_entity.area2d.on_enter_actions
            )

            if actions:
                area_id = area_entity.id

                if (
                    area_id
                    in self.active_area_sequences
                ):
                    continue

                self.active_area_sequences.add(
                    area_id
                )

                self._run_area_actions(
                    area_id,
                    actions,
                    0,
                )
                continue

            # Compatibilidade com cenas antigas.
            legacy_action = (
                area_entity.area2d.on_enter_action
            )

            if legacy_action == "show_message":
                message_text = (
                    area_entity.area2d.message_text.strip()
                )

                if message_text:
                    self.area_event.emit(
                        f"Mensagem: {message_text}"
                    )
                    self.canvas.show_message(
                        message_text
                    )

            elif legacy_action == "change_scene":
                target_scene = (
                    area_entity.area2d.target_scene.strip()
                )

                if (
                    target_scene
                    and self._change_scene(
                        target_scene
                    )
                ):
                    return

            elif (
                legacy_action
                == "message_change_scene"
            ):
                message_text = (
                    area_entity.area2d.message_text.strip()
                )
                target_scene = (
                    area_entity.area2d.target_scene.strip()
                )

                if message_text:
                    self.area_event.emit(
                        f"Mensagem: {message_text}"
                    )
                    self.canvas.show_message(
                        message_text,
                        duration_ms=3000,
                    )

                if target_scene:
                    QTimer.singleShot(
                        3000,
                        lambda scene=target_scene: (
                            self._change_scene(
                                scene
                            )
                        ),
                    )
                    return

        self.canvas.refresh()

    def _finish_area_sequence(
        self,
        area_id: str,
    ) -> None:
        self.active_area_sequences.discard(
            area_id
        )

    def _run_area_actions(
        self,
        area_id: str,
        actions: list[object],
        index: int = 0,
    ) -> None:
        if index >= len(actions):
            self._finish_area_sequence(
                area_id
            )
            return

        action = actions[index]

        action_type = str(
            getattr(
                action,
                "action",
                "none",
            )
            or "none"
        )

        if action_type == "show_message":
            message_text = str(
                getattr(
                    action,
                    "message_text",
                    "",
                )
                or ""
            ).strip()

            if message_text:
                self.area_event.emit(
                    f"Mensagem: {message_text}"
                )

                self.canvas.show_message(
                    message_text
                )

            self._run_area_actions(
                area_id,
                actions,
                index + 1,
            )
            return

        if action_type == "wait":
            wait_seconds = max(
                0.0,
                float(
                    getattr(
                        action,
                        "wait_seconds",
                        0.0,
                    )
                    or 0.0
                ),
            )

            QTimer.singleShot(
                int(
                    wait_seconds
                    * 1000
                ),
                lambda: self._run_area_actions(
                    area_id,
                    actions,
                    index + 1,
                ),
            )
            return

        if action_type == "teleport_player":
            if self.runtime is None:
                self._finish_area_sequence(
                    area_id
                )
                return

            player = self.runtime.scene.player_entity()

            if player is not None:
                player.transform.x = float(
                    getattr(action, "player_x", 0.0)
                    or 0.0
                )
                player.transform.y = float(
                    getattr(action, "player_y", 0.0)
                    or 0.0
                )

                self.area_event.emit(
                    "Jogador teleportado para "
                    f"({player.transform.x:.1f}, "
                    f"{player.transform.y:.1f})"
                )
                self.canvas.refresh()

            self._run_area_actions(
                area_id,
                actions,
                index + 1,
            )
            return

        if action_type == "damage_player":
            if self.runtime is None:
                self._finish_area_sequence(
                    area_id
                )
                return

            amount = max(
                1,
                int(
                    getattr(
                        action,
                        "damage_amount",
                        1,
                    )
                    or 1
                ),
            )

            health, maximum = (
                self.runtime.damage_player(
                    amount
                )
            )

            damage_applied = self.runtime.last_player_damage_applied()
            if damage_applied:
                self.area_event.emit(
                    f"Dano: {amount} | Vida: {health}/{maximum}"
                )
            else:
                self.area_event.emit("Dano ignorado: Player invulnerável.")

            if damage_applied and health == 0 and self.runtime.player is not None:
                controller = self.runtime.player.player_controller
                if controller is not None:
                    message = (
                        controller.death_message
                        if controller.show_death_message
                        else ""
                    )
                    self.canvas.start_death_transition(
                        message,
                        controller.respawn_delay,
                        controller.death_fade_duration,
                        controller.confirm_respawn,
                    )
                    self.area_event.emit("Player morreu; respawn iniciado.")

            self._run_area_actions(
                area_id,
                actions,
                index + 1,
            )
            return

        if action_type == "set_collider":
            if self.runtime is None:
                self._finish_area_sequence(
                    area_id
                )
                return

            target_entity_id = str(
                getattr(
                    action,
                    "target_entity_id",
                    "",
                )
                or ""
            )

            target_entity = (
                self.runtime.scene.entity(
                    target_entity_id
                )
            )

            if (
                target_entity is not None
                and target_entity.collider is not None
            ):
                enabled = bool(
                    getattr(
                        action,
                        "collider_enabled",
                        True,
                    )
                )

                target_entity.collider.enabled = enabled
                self.runtime.refresh_collisions()

                state_text = (
                    "ativado"
                    if enabled
                    else "desativado"
                )

                self.area_event.emit(
                    f"Collider {state_text}: "
                    f"{target_entity.name}"
                )

                self.canvas.refresh()

            self._run_area_actions(
                area_id,
                actions,
                index + 1,
            )
            return

        if action_type == "change_scene":
            target_scene = str(
                getattr(
                    action,
                    "target_scene",
                    "",
                )
                or ""
            ).strip()

            remaining_actions = actions[
                index + 1:
            ]

            self._finish_area_sequence(
                area_id
            )

            if not target_scene:
                return

            changed = self._change_scene(
                target_scene
            )

            if (
                changed
                and remaining_actions
            ):
                QTimer.singleShot(
                    0,
                    lambda: self._run_area_actions(
                        area_id,
                        remaining_actions,
                        0,
                    ),
                )

            return

        self._run_area_actions(
            area_id,
            actions,
            index + 1,
        )

    def _change_scene(
        self,
        target_scene: str,
    ) -> bool:
        if self.project_root is None:
            self.area_event.emit(
                "Troca de cena falhou: projeto não carregado."
            )
            return False

        relative = Path(target_scene)

        if relative.suffix.lower() != ".scene":
            relative = relative.with_suffix(".scene")

        candidates: list[Path] = []

        if relative.is_absolute():
            candidates.append(relative)
        else:
            candidates.append(
                self.project_root / relative
            )

            if (
                not relative.parts
                or relative.parts[0].lower() != "scenes"
            ):
                candidates.append(
                    self.project_root
                    / "scenes"
                    / relative
                )

        scene_path = next(
            (
                path
                for path in candidates
                if path.exists()
            ),
            None,
        )

        if scene_path is None:
            self.area_event.emit(
                "Troca de cena falhou: "
                f"{target_scene} não encontrada."
            )
            return False

        source_player = None

        if self.runtime is not None:
            source_player = (
                self.runtime.player
            )

        try:
            scene = self.scene_serializer.load(
                scene_path
            )
        except (
            OSError,
            ValueError,
            TypeError,
        ) as error:
            self.area_event.emit(
                "Troca de cena falhou: "
                f"{error}"
            )
            return False

        target_player = (
            scene.player_entity()
        )

        if (
            target_player is None
            and source_player is not None
        ):
            player_data = self._player_data_for_scene_change(source_player)
            target_player = SceneEntity.from_dict(player_data)

            scene.add_entity(
                target_player
            )

            self.area_event.emit(
                "Player transportado para "
                f"{scene.name}"
            )

        if target_player is not None:
            spawn = (
                self._default_spawn_for_scene(
                    scene
                )
            )

            if spawn is not None:
                target_player.transform.x = (
                    spawn.transform.x
                )

                target_player.transform.y = (
                    spawn.transform.y
                )

                self.area_event.emit(
                    "Spawn encontrado: "
                    f"{spawn.name}"
                )

            elif source_player is not None:
                target_player.transform.x = (
                    source_player.transform.x
                )

                target_player.transform.y = (
                    source_player.transform.y
                )

        self.area_event.emit(
            f"Trocando cena: {scene.name}"
        )

        self.start(
            self.project_root,
            scene,
        )

        return True

    @staticmethod
    def _player_data_for_scene_change(
        source_player: SceneEntity,
    ) -> dict[str, object]:
        data = source_player.to_dict()
        flowchart = data.get("blueprint")
        if not isinstance(flowchart, dict):
            return data

        nodes = flowchart.get("nodes", [])
        connections = flowchart.get("connections", [])
        if not isinstance(nodes, list) or not isinstance(connections, list):
            return data

        scene_start_ids = {
            str(node.get("id"))
            for node in nodes
            if isinstance(node, dict)
            and str(node.get("type")) == "scene_start"
        }
        if not scene_start_ids:
            return data

        copied_flowchart = dict(flowchart)
        copied_flowchart["nodes"] = [
            dict(node)
            for node in nodes
            if isinstance(node, dict)
            and str(node.get("id")) not in scene_start_ids
        ]
        copied_flowchart["connections"] = [
            dict(connection)
            for connection in connections
            if isinstance(connection, dict)
            and str(connection.get("from_node")) not in scene_start_ids
            and str(connection.get("to_node")) not in scene_start_ids
        ]
        data["blueprint"] = copied_flowchart
        return data

    @staticmethod
    def _default_spawn_for_scene(
        scene: SceneResource,
    ) -> SceneEntity | None:
        preferred_names = {
            "spawnpoint",
            "spawn_point",
            "player_spawn",
            "spawn",
        }

        for entity in scene.entities:
            if (
                entity.name.strip().lower()
                in preferred_names
            ):
                return entity

        return None

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