from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.animation import AnimationClip, AnimationFrameRegion
from lupix_studio.assets.importer import import_png
from lupix_studio.assets.registry import AssetRegistry
from lupix_studio.scene.model import SceneEntity


class SpriteSheetCanvas(QWidget):
    """Canvas do spritesheet com seleção livre de regiões."""

    region_created = Signal(QRect)
    region_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.pixmap = QPixmap()
        self.zoom = 2
        self.regions: dict[int, AnimationFrameRegion] = {}
        self.active_region_id: int | None = None
        self.drag_start: QPoint | None = None
        self.drag_current: QPoint | None = None
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(1, 1)

    def clear(self) -> None:
        self.pixmap = QPixmap()
        self.regions = {}
        self.active_region_id = None
        self.drag_start = None
        self.drag_current = None
        self._update_size()
        self.update()

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self.pixmap = pixmap
        self._update_size()
        self.update()

    def set_regions(self, regions: dict[int, AnimationFrameRegion]) -> None:
        self.regions = dict(regions)
        if self.active_region_id not in self.regions:
            self.active_region_id = None
        self.update()

    def set_active_region(self, frame_id: int | None) -> None:
        if frame_id is not None and frame_id not in self.regions:
            frame_id = None
        self.active_region_id = frame_id
        self.update()

    def set_zoom(self, zoom: int) -> None:
        self.zoom = max(1, min(8, int(zoom)))
        self._update_size()
        self.update()

    def _update_size(self) -> None:
        if self.pixmap.isNull():
            self.setFixedSize(1, 1)
            return
        self.setFixedSize(self.pixmap.width() * self.zoom, self.pixmap.height() * self.zoom)

    def _image_point(self, point: QPoint) -> QPoint:
        if self.pixmap.isNull():
            return QPoint()
        x = max(0, min(self.pixmap.width() - 1, point.x() // self.zoom))
        y = max(0, min(self.pixmap.height() - 1, point.y() // self.zoom))
        return QPoint(x, y)

    def _region_at(self, point: QPoint) -> int | None:
        image_point = self._image_point(point)
        for frame_id in reversed(list(self.regions)):
            region = self.regions[frame_id]
            rect = QRect(region.x, region.y, region.width, region.height)
            if rect.contains(image_point):
                return frame_id
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self.pixmap.isNull():
            super().mousePressEvent(event)
            return
        existing = self._region_at(event.position().toPoint())
        shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        if existing is not None and not shift:
            self.active_region_id = existing
            self.region_selected.emit(existing)
            self.update()
            event.accept()
            return
        point = self._image_point(event.position().toPoint())
        self.active_region_id = None
        self.drag_start = point
        self.drag_current = point
        self.update()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drag_start is None:
            super().mouseMoveEvent(event)
            return
        self.drag_current = self._image_point(event.position().toPoint())
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        if self.drag_start is None or self.drag_current is None:
            return
        self.drag_current = self._image_point(event.position().toPoint())
        rect = self._normalized_drag_rect()
        self.drag_start = None
        self.drag_current = None
        if rect is None or rect.width() < 2 or rect.height() < 2:
            self.update()
            return
        self.region_created.emit(rect)
        self.update()
        event.accept()

    def _normalized_drag_rect(self) -> QRect | None:
        if self.drag_start is None or self.drag_current is None:
            return None
        left = min(self.drag_start.x(), self.drag_current.x())
        right = max(self.drag_start.x(), self.drag_current.x())
        top = min(self.drag_start.y(), self.drag_current.y())
        bottom = max(self.drag_start.y(), self.drag_current.y())
        return QRect(left, top, right - left + 1, bottom - top + 1)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.fillRect(self.rect(), QColor("#111318"))
        if self.pixmap.isNull():
            return
        destination = QRect(0, 0, self.pixmap.width() * self.zoom, self.pixmap.height() * self.zoom)
        painter.drawPixmap(destination, self.pixmap)
        self._draw_regions(painter)
        self._draw_drag_region(painter)

    def _draw_regions(self, painter: QPainter) -> None:
        font = QFont(painter.font())
        font.setPixelSize(10)
        painter.setFont(font)
        for frame_id, region in self.regions.items():
            rect = QRect(
                region.x * self.zoom,
                region.y * self.zoom,
                region.width * self.zoom,
                region.height * self.zoom,
            )
            active = frame_id == self.active_region_id
            border = QColor("#f8d75c" if active else "#4f8cff")
            fill = QColor(248, 215, 92, 45) if active else QColor(37, 99, 235, 35)
            pen = QPen(border, 2)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(fill)
            painter.drawRect(rect.adjusted(1, 1, -1, -1))
            label = QRect(rect.x() + 3, rect.y() + 3, max(24, min(48, rect.width() - 6)), 17)
            painter.fillRect(label, QColor(0, 0, 0, 175))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(label, Qt.AlignmentFlag.AlignCenter, str(frame_id))

    def _draw_drag_region(self, painter: QPainter) -> None:
        rect = self._normalized_drag_rect()
        if rect is None:
            return
        display = QRect(
            rect.x() * self.zoom,
            rect.y() * self.zoom,
            rect.width() * self.zoom,
            rect.height() * self.zoom,
        )
        pen = QPen(QColor("#65d8ff"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(QColor(101, 216, 255, 30))
        painter.drawRect(display)


class AnimationSpriteSheetEditor(QWidget):
    """Editor visual de regiões, preview, timeline e fonte por animação."""

    frames_changed = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.project_root: Path | None = None
        self.entity: SceneEntity | None = None
        self.current_clip: AnimationClip | None = None
        self.preview_frames: list[int] = []
        self.preview_fps = 6.0
        self.preview_loop = True
        self.preview_index = 0
        self.preview_paused = False
        self.active_region_id: int | None = None
        self._updating_source = False
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self._advance_preview)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.setObjectName("AnimationSpriteSheetEditor")
        self.setStyleSheet(
            """
            QWidget#AnimationSpriteSheetEditor { background: transparent; }
            QFrame#AnimationPanel { background-color: #191b20; border: 1px solid #343840; border-radius: 6px; }
            QLabel#SectionTitle { font-weight: 600; font-size: 13px; }
            QLabel#MutedLabel { color: #8d929b; }
            QLabel#RegionInfo { color: #c6cbd4; }
            QScrollArea#SpriteScroll { background-color: #111318; border: 1px solid #343840; border-radius: 4px; }
            QListWidget#AnimationTimeline { background-color: #111318; border: 1px solid #343840; border-radius: 4px; padding: 5px; }
            QListWidget#AnimationTimeline::item { min-width: 72px; min-height: 70px; border: 1px solid #343840; border-radius: 4px; margin-right: 4px; padding: 3px; }
            QListWidget#AnimationTimeline::item:selected { background-color: #2563eb; border: 1px solid #4f8cff; }
            QPushButton#SmallToolButton { min-width: 30px; max-width: 30px; min-height: 28px; max-height: 28px; padding: 0px; }
            QPushButton#DeleteRegionButton { min-height: 28px; color: #ff6b6b; }
            """
        )
        self._build_preview_panel()
        self._build_sprite_panel()
        self._build_timeline_panel()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.preview_panel)
        splitter.addWidget(self.sprite_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([300, 900])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.timeline_panel)

    def _build_preview_panel(self) -> None:
        self.preview_title = QLabel("Preview")
        self.preview_title.setObjectName("SectionTitle")
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(220, 220)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setStyleSheet("QLabel { border: 1px solid #343840; border-radius: 4px; background-color: #111318; }")
        self.preview_info = QLabel("Escala fixa • alinhamento: base central")
        self.preview_info.setObjectName("MutedLabel")
        self.play_pause_button = QPushButton("⏸")
        self.restart_button = QPushButton("↺")
        for button in (self.play_pause_button, self.restart_button):
            button.setObjectName("SmallToolButton")
        controls = QHBoxLayout()
        controls.addWidget(self.play_pause_button)
        controls.addWidget(self.restart_button)
        controls.addStretch()
        self.preview_panel = QFrame()
        self.preview_panel.setObjectName("AnimationPanel")
        layout = QVBoxLayout(self.preview_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self.preview_title)
        layout.addWidget(self.preview_label, 1)
        layout.addWidget(self.preview_info)
        layout.addLayout(controls)

    def _build_sprite_panel(self) -> None:
        self.sprite_title = QLabel("Spritesheet — Regiões")
        self.sprite_title.setObjectName("SectionTitle")
        self.status = QLabel("Nenhum Sprite disponível.")
        self.status.setObjectName("MutedLabel")

        self.source_combo = QComboBox()
        self.source_combo.setMinimumWidth(220)
        self.import_button = QPushButton("Importar PNG")
        self.main_sprite_button = QPushButton("Usar Sprite principal")
        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Fonte:"))
        source_row.addWidget(self.source_combo, 1)
        source_row.addWidget(self.import_button)
        source_row.addWidget(self.main_sprite_button)

        self.help_label = QLabel(
            "Arraste uma área aproximada em volta da pose. O Lupix ajusta a região aos pixels visíveis. "
            "Cada animação pode usar o Sprite principal ou um spritesheet PNG próprio."
        )
        self.help_label.setObjectName("MutedLabel")
        self.help_label.setWordWrap(True)
        self.region_info = QLabel("Região selecionada: nenhuma")
        self.region_info.setObjectName("RegionInfo")
        self.zoom_out_button = QPushButton("−")
        self.zoom_in_button = QPushButton("+")
        self.zoom_label = QLabel("Zoom 2x")
        for button in (self.zoom_out_button, self.zoom_in_button):
            button.setObjectName("SmallToolButton")
        self.add_to_timeline_button = QPushButton("Adicionar à Timeline")
        self.trim_region_button = QPushButton("Ajustar à Pose")
        self.delete_region_button = QPushButton("Excluir Região")
        self.delete_region_button.setObjectName("DeleteRegionButton")
        for button in (self.add_to_timeline_button, self.trim_region_button, self.delete_region_button):
            button.setEnabled(False)

        header = QHBoxLayout()
        header.addWidget(self.sprite_title)
        header.addStretch()
        header.addWidget(self.zoom_out_button)
        header.addWidget(self.zoom_label)
        header.addWidget(self.zoom_in_button)

        self.canvas = SpriteSheetCanvas()
        container = QWidget()
        canvas_layout = QVBoxLayout(container)
        canvas_layout.setContentsMargins(12, 12, 12, 12)
        canvas_layout.addWidget(self.canvas, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        canvas_layout.addStretch()
        self.sprite_scroll = QScrollArea()
        self.sprite_scroll.setObjectName("SpriteScroll")
        self.sprite_scroll.setWidgetResizable(True)
        self.sprite_scroll.setWidget(container)
        self.sprite_scroll.setMinimumSize(400, 220)

        region_buttons = QHBoxLayout()
        region_buttons.addWidget(self.region_info)
        region_buttons.addStretch()
        region_buttons.addWidget(self.add_to_timeline_button)
        region_buttons.addWidget(self.trim_region_button)
        region_buttons.addWidget(self.delete_region_button)

        self.sprite_panel = QFrame()
        self.sprite_panel.setObjectName("AnimationPanel")
        layout = QVBoxLayout(self.sprite_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(7)
        layout.addLayout(header)
        layout.addLayout(source_row)
        layout.addWidget(self.status)
        layout.addWidget(self.sprite_scroll, 1)
        layout.addLayout(region_buttons)
        layout.addWidget(self.help_label)

    def _build_timeline_panel(self) -> None:
        self.timeline_title = QLabel("Timeline")
        self.timeline_title.setObjectName("SectionTitle")
        self.timeline = QListWidget()
        self.timeline.setObjectName("AnimationTimeline")
        self.timeline.setFlow(QListWidget.Flow.LeftToRight)
        self.timeline.setWrapping(False)
        self.timeline.setIconSize(QSize(48, 48))
        self.timeline.setMinimumHeight(100)
        self.timeline.setMaximumHeight(116)
        self.timeline.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.timeline.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.move_left_button = QPushButton("←")
        self.move_right_button = QPushButton("→")
        for button in (self.move_left_button, self.move_right_button):
            button.setObjectName("SmallToolButton")
        self.duplicate_button = QPushButton("Duplicar")
        self.remove_timeline_button = QPushButton("Remover")
        controls = QHBoxLayout()
        for button in (self.move_left_button, self.move_right_button, self.duplicate_button, self.remove_timeline_button):
            controls.addWidget(button)
        header = QHBoxLayout()
        header.addWidget(self.timeline_title)
        header.addStretch()
        header.addLayout(controls)
        self.timeline_panel = QFrame()
        self.timeline_panel.setObjectName("AnimationPanel")
        layout = QVBoxLayout(self.timeline_panel)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        layout.addLayout(header)
        layout.addWidget(self.timeline)

    def _connect_signals(self) -> None:
        self.canvas.region_created.connect(self._on_region_created)
        self.canvas.region_selected.connect(self._on_region_selected)
        self.zoom_out_button.clicked.connect(self._zoom_out)
        self.zoom_in_button.clicked.connect(self._zoom_in)
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        self.import_button.clicked.connect(self._import_spritesheet)
        self.main_sprite_button.clicked.connect(self._use_main_sprite)
        self.add_to_timeline_button.clicked.connect(self._add_active_region_to_timeline)
        self.trim_region_button.clicked.connect(self._trim_active_region)
        self.delete_region_button.clicked.connect(self._delete_active_region)
        self.play_pause_button.clicked.connect(self._toggle_preview)
        self.restart_button.clicked.connect(self._restart_preview)
        self.move_left_button.clicked.connect(self._move_frame_left)
        self.move_right_button.clicked.connect(self._move_frame_right)
        self.duplicate_button.clicked.connect(self._duplicate_frame)
        self.remove_timeline_button.clicked.connect(self._remove_frame_from_timeline)
        self.timeline.currentRowChanged.connect(self._on_timeline_selection_changed)

    def set_context(self, project_root: Path | None, entity: SceneEntity | None) -> None:
        self.project_root = project_root.resolve() if project_root is not None else None
        self.entity = entity
        self.current_clip = None
        self.active_region_id = None
        self._refresh_source_combo()
        self._load_sprite()

    def set_clip(self, clip: AnimationClip | None) -> None:
        self.current_clip = clip
        self.active_region_id = None
        if clip is None:
            self.preview_frames = []
            self.canvas.set_regions({})
            self.timeline.clear()
            self._refresh_source_combo()
            self._update_region_controls()
            self._restart_preview()
            return
        self.preview_frames = list(clip.frames)
        self.preview_fps = clip.fps
        self.preview_loop = clip.loop
        self._refresh_source_combo()
        self._load_sprite()
        self.canvas.set_regions(clip.regions)
        self._refresh_timeline()
        self._update_region_controls()
        self._restart_preview()

    def set_frame_size(self, width: int, height: int) -> None:
        del width, height

    def set_frames(self, frames: list[int]) -> None:
        if self.current_clip is not None:
            self.current_clip.frames = list(frames)
        self.preview_frames = list(frames)
        self._refresh_timeline()
        self._restart_preview()

    def set_preview_settings(self, frames: list[int], fps: float, loop: bool) -> None:
        self.preview_frames = list(frames)
        self.preview_fps = max(0.01, float(fps))
        self.preview_loop = bool(loop)
        self.preview_index = 0
        self._refresh_timeline()
        self._restart_preview()

    def _effective_asset_id(self, explicit: str | None = None) -> str:
        if explicit is None and self.current_clip is not None:
            explicit = self.current_clip.asset_id
        if explicit:
            return str(explicit)
        if self.entity is not None and self.entity.sprite is not None:
            return str(self.entity.sprite.asset_id or "")
        return ""

    def _refresh_source_combo(self) -> None:
        self._updating_source = True
        try:
            self.source_combo.clear()
            self.source_combo.addItem("Sprite principal", "")
            if self.project_root is not None:
                registry = AssetRegistry(self.project_root)
                records = [record for record in registry.load() if record.type == "sprites"]
                for record in records:
                    self.source_combo.addItem(record.name, record.id)
            asset_id = self.current_clip.asset_id if self.current_clip is not None else ""
            index = self.source_combo.findData(asset_id)
            self.source_combo.setCurrentIndex(max(index, 0))
        finally:
            self._updating_source = False

    def _on_source_changed(self) -> None:
        if self._updating_source or self.current_clip is None:
            return
        selected = str(self.source_combo.currentData() or "")
        old_explicit = self.current_clip.asset_id
        old_effective = self._effective_asset_id(old_explicit)
        new_effective = self._effective_asset_id(selected)
        if selected == old_explicit:
            return
        if old_effective != new_effective and self.current_clip.regions:
            answer = QMessageBox.question(
                self,
                "Trocar Spritesheet",
                "As regiões atuais pertencem ao spritesheet anterior.\n\n"
                "Trocar a fonte e limpar os frames/regiões desta animação?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self._refresh_source_combo()
                return
            self.current_clip.frames.clear()
            self.current_clip.regions.clear()
            self.preview_frames = []
        self.current_clip.asset_id = selected
        self.active_region_id = None
        self._load_sprite()
        self.canvas.set_regions(self.current_clip.regions)
        self._refresh_timeline()
        self._update_region_controls()
        self._restart_preview()
        self.frames_changed.emit(list(self.current_clip.frames))

    def _use_main_sprite(self) -> None:
        index = self.source_combo.findData("")
        if index >= 0:
            self.source_combo.setCurrentIndex(index)

    def _import_spritesheet(self) -> None:
        if self.project_root is None or self.current_clip is None:
            return
        filename, _ = QFileDialog.getOpenFileName(self, "Importar Spritesheet", str(Path.home()), "PNG (*.png)")
        if not filename:
            return
        try:
            imported = import_png(Path(filename), self.project_root, "sprites")
        except (OSError, ValueError, TypeError) as error:
            QMessageBox.critical(self, "Erro ao importar", str(error))
            return
        registry = AssetRegistry(self.project_root)
        destination = Path(imported.destination).resolve()
        record_id = ""
        for record in registry.load():
            try:
                if (self.project_root / record.path).resolve() == destination:
                    record_id = record.id
                    break
            except (OSError, ValueError):
                continue
        if not record_id:
            QMessageBox.warning(self, "Importar Spritesheet", "O PNG foi importado, mas o asset não foi localizado no registro.")
            self._refresh_source_combo()
            return
        self._refresh_source_combo()
        index = self.source_combo.findData(record_id)
        if index >= 0:
            self.source_combo.setCurrentIndex(index)

    def _load_sprite(self) -> None:
        self.canvas.clear()
        self.preview_timer.stop()
        self.preview_label.clear()
        self.timeline.clear()
        if self.project_root is None or self.entity is None:
            self.status.setText("Nenhum Sprite disponível.")
            return
        asset_id = self._effective_asset_id()
        if not asset_id:
            self.status.setText("Nenhum Sprite disponível.")
            return
        registry = AssetRegistry(self.project_root)
        record = registry.find_by_id(asset_id)
        if record is None:
            self.status.setText("Spritesheet não encontrado no projeto.")
            return
        path = self.project_root / record.path
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.status.setText("Não foi possível carregar o Spritesheet.")
            return
        self.canvas.set_pixmap(pixmap)
        source_kind = "Sprite principal" if not (self.current_clip and self.current_clip.asset_id) else record.name
        self.status.setText(f"{source_kind} • {pixmap.width()} × {pixmap.height()} px")
        if self.current_clip is not None:
            self.canvas.set_regions(self.current_clip.regions)
        self._refresh_timeline()
        self._restart_preview()

    def _trim_rect_to_visible_pixels(self, rect: QRect) -> QRect:
        if self.canvas.pixmap.isNull():
            return rect
        image = self.canvas.pixmap.toImage()
        left = max(0, rect.left())
        top = max(0, rect.top())
        right = min(image.width() - 1, rect.right())
        bottom = min(image.height() - 1, rect.bottom())
        min_x = min_y = max_x = max_y = None
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                if image.pixelColor(x, y).alpha() <= 0:
                    continue
                min_x = x if min_x is None else min(min_x, x)
                min_y = y if min_y is None else min(min_y, y)
                max_x = x if max_x is None else max(max_x, x)
                max_y = y if max_y is None else max(max_y, y)
        if None in (min_x, min_y, max_x, max_y):
            return rect
        return QRect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def _on_region_created(self, rect: QRect) -> None:
        if self.current_clip is None:
            return
        trimmed = self._trim_rect_to_visible_pixels(rect)
        region = AnimationFrameRegion(x=trimmed.x(), y=trimmed.y(), width=trimmed.width(), height=trimmed.height())
        frame_id = self.current_clip.add_region_frame(region)
        self.active_region_id = frame_id
        self.preview_frames = list(self.current_clip.frames)
        self.canvas.set_regions(self.current_clip.regions)
        self.canvas.set_active_region(frame_id)
        self._update_region_controls()
        self._refresh_timeline()
        self._restart_preview()
        self.frames_changed.emit(list(self.current_clip.frames))

    def _on_region_selected(self, frame_id: int) -> None:
        self.active_region_id = int(frame_id)
        self.canvas.set_active_region(self.active_region_id)
        self._update_region_controls()

    def _trim_active_region(self) -> None:
        if self.current_clip is None or self.active_region_id is None:
            return
        region = self.current_clip.region(self.active_region_id)
        if region is None:
            return
        trimmed = self._trim_rect_to_visible_pixels(QRect(region.x, region.y, region.width, region.height))
        region.x, region.y = trimmed.x(), trimmed.y()
        region.width, region.height = trimmed.width(), trimmed.height()
        self.canvas.set_regions(self.current_clip.regions)
        self._refresh_timeline()
        self._restart_preview()
        self.frames_changed.emit(list(self.current_clip.frames))

    def _update_region_controls(self) -> None:
        enabled = self.current_clip is not None and self.active_region_id is not None and self.active_region_id in self.current_clip.regions
        self.add_to_timeline_button.setEnabled(enabled)
        self.trim_region_button.setEnabled(enabled)
        self.delete_region_button.setEnabled(enabled)
        if not enabled:
            self.region_info.setText("Região selecionada: nenhuma")
            return
        region = self.current_clip.regions[self.active_region_id]
        self.region_info.setText(f"Frame {self.active_region_id} — X {region.x}, Y {region.y}, {region.width} × {region.height}")

    def _add_active_region_to_timeline(self) -> None:
        if self.current_clip is None or self.active_region_id is None:
            return
        if self.active_region_id not in self.current_clip.regions:
            return
        self.current_clip.frames.append(self.active_region_id)
        self._commit_timeline(len(self.current_clip.frames) - 1)

    def _delete_active_region(self) -> None:
        if self.current_clip is None or self.active_region_id is None:
            return
        frame_id = self.active_region_id
        self.current_clip.frames = [value for value in self.current_clip.frames if value != frame_id]
        self.current_clip.remove_region(frame_id)
        self.active_region_id = None
        self.canvas.set_regions(self.current_clip.regions)
        self.canvas.set_active_region(None)
        self._commit_timeline(-1)
        self._update_region_controls()

    def _logical_canvas_size(self) -> QSize:
        if self.current_clip is None or not self.current_clip.regions:
            return QSize(1, 1)
        max_width = max(region.width for region in self.current_clip.regions.values())
        max_height = max(region.height for region in self.current_clip.regions.values())
        max_offset_x = max(abs(region.offset_x) for region in self.current_clip.regions.values())
        max_offset_y = max(abs(region.offset_y) for region in self.current_clip.regions.values())
        return QSize(max_width + max_offset_x * 2, max_height + max_offset_y * 2)

    def _frame_pixmap(self, frame_id: int) -> QPixmap:
        if self.current_clip is None or self.canvas.pixmap.isNull():
            return QPixmap()
        region = self.current_clip.region(frame_id)
        if region is None:
            return QPixmap()
        source = self.canvas.pixmap.copy(region.x, region.y, region.width, region.height)
        if source.isNull():
            return QPixmap()
        logical = self._logical_canvas_size()
        output = QPixmap(logical)
        output.fill(Qt.GlobalColor.transparent)
        target_x = logical.width() // 2 - source.width() // 2 + region.offset_x
        target_y = logical.height() - source.height() + region.offset_y
        painter = QPainter(output)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.drawPixmap(target_x, target_y, source)
        painter.end()
        return output

    def _refresh_timeline(self) -> None:
        current_row = self.timeline.currentRow()
        self.timeline.blockSignals(True)
        self.timeline.clear()
        for frame_id in self.preview_frames:
            item = QListWidgetItem(str(frame_id))
            pixmap = self._frame_pixmap(frame_id)
            if not pixmap.isNull():
                item.setIcon(QIcon(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, int(frame_id))
            self.timeline.addItem(item)
        if self.timeline.count() > 0 and current_row >= 0:
            self.timeline.setCurrentRow(min(current_row, self.timeline.count() - 1))
        self.timeline.blockSignals(False)

    def _on_timeline_selection_changed(self, row: int) -> None:
        if row < 0 or row >= len(self.preview_frames) or self.current_clip is None:
            return
        frame_id = self.preview_frames[row]
        if frame_id in self.current_clip.regions:
            self.active_region_id = frame_id
            self.canvas.set_active_region(frame_id)
            self._update_region_controls()

    def _move_frame_left(self) -> None:
        if self.current_clip is None:
            return
        row = self.timeline.currentRow()
        if row <= 0 or row >= len(self.current_clip.frames):
            return
        self.current_clip.frames[row - 1], self.current_clip.frames[row] = self.current_clip.frames[row], self.current_clip.frames[row - 1]
        self._commit_timeline(row - 1)

    def _move_frame_right(self) -> None:
        if self.current_clip is None:
            return
        row = self.timeline.currentRow()
        if row < 0 or row >= len(self.current_clip.frames) - 1:
            return
        self.current_clip.frames[row], self.current_clip.frames[row + 1] = self.current_clip.frames[row + 1], self.current_clip.frames[row]
        self._commit_timeline(row + 1)

    def _duplicate_frame(self) -> None:
        if self.current_clip is None:
            return
        row = self.timeline.currentRow()
        if row < 0 or row >= len(self.current_clip.frames):
            return
        self.current_clip.frames.insert(row + 1, self.current_clip.frames[row])
        self._commit_timeline(row + 1)

    def _remove_frame_from_timeline(self) -> None:
        if self.current_clip is None:
            return
        row = self.timeline.currentRow()
        if row < 0 or row >= len(self.current_clip.frames):
            return
        del self.current_clip.frames[row]
        self._commit_timeline(min(row, len(self.current_clip.frames) - 1))

    def _commit_timeline(self, selected_row: int) -> None:
        if self.current_clip is None:
            return
        self.preview_frames = list(self.current_clip.frames)
        self._refresh_timeline()
        if selected_row >= 0:
            self.timeline.setCurrentRow(selected_row)
        self.preview_index = 0
        self._restart_preview()
        self.frames_changed.emit(list(self.current_clip.frames))

    def _zoom_in(self) -> None:
        self.canvas.set_zoom(self.canvas.zoom + 1)
        self.zoom_label.setText(f"Zoom {self.canvas.zoom}x")

    def _zoom_out(self) -> None:
        self.canvas.set_zoom(self.canvas.zoom - 1)
        self.zoom_label.setText(f"Zoom {self.canvas.zoom}x")

    def _toggle_preview(self) -> None:
        if not self.preview_frames:
            return
        self.preview_paused = not self.preview_paused
        if self.preview_paused:
            self.preview_timer.stop()
            self.play_pause_button.setText("▶")
        else:
            self.play_pause_button.setText("⏸")
            self._start_preview_timer()

    def _restart_preview(self) -> None:
        self.preview_timer.stop()
        self.preview_paused = False
        self.play_pause_button.setText("⏸")
        if not self.preview_frames or self.canvas.pixmap.isNull():
            self.preview_label.clear()
            return
        self.preview_index = 0
        self._show_preview_frame()
        self._start_preview_timer()

    def _start_preview_timer(self) -> None:
        if self.preview_paused or len(self.preview_frames) <= 1:
            return
        self.preview_timer.start(max(1, int(1000.0 / self.preview_fps)))

    def _advance_preview(self) -> None:
        if not self.preview_frames:
            self.preview_timer.stop()
            return
        self.preview_index += 1
        if self.preview_index >= len(self.preview_frames):
            if self.preview_loop:
                self.preview_index = 0
            else:
                self.preview_index = len(self.preview_frames) - 1
                self.preview_timer.stop()
                self.preview_paused = True
                self.play_pause_button.setText("▶")
        self._show_preview_frame()

    def _show_preview_frame(self) -> None:
        if not self.preview_frames:
            self.preview_label.clear()
            return
        pixmap = self._frame_pixmap(self.preview_frames[self.preview_index])
        if pixmap.isNull():
            self.preview_label.clear()
            return
        size = self.preview_label.size()
        scaled = pixmap.scaled(
            max(1, size.width() - 14),
            max(1, size.height() - 14),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        self.preview_label.setPixmap(scaled)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.preview_frames:
            self._show_preview_frame()
