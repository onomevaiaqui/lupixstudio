from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.assets.registry import AssetRegistry
from lupix_studio.scene.model import SceneEntity


class SpriteSheetCanvas(QWidget):
    """Grade visual do spritesheet com seleção de frames."""

    frames_changed = Signal(list)

    def __init__(self) -> None:
        super().__init__()

        self.pixmap = QPixmap()

        self.frame_width = 16
        self.frame_height = 16

        self.selected_frames: list[int] = []

        self.columns = 0
        self.rows = 0

        self.zoom = 2

        self.last_clicked_frame: int | None = None

        self.setMouseTracking(
            True
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        self.setMinimumSize(
            1,
            1,
        )

    def clear(self) -> None:
        self.pixmap = QPixmap()

        self.selected_frames.clear()

        self.columns = 0
        self.rows = 0

        self.last_clicked_frame = None

        self._update_size()

        self.update()

    def set_pixmap(
        self,
        pixmap: QPixmap,
    ) -> None:
        self.pixmap = pixmap

        self._recalculate_grid()
        self._update_size()

        self.update()

    def set_frame_size(
        self,
        width: int,
        height: int,
    ) -> None:
        self.frame_width = max(
            1,
            int(width),
        )

        self.frame_height = max(
            1,
            int(height),
        )

        self._recalculate_grid()
        self._update_size()

        self.selected_frames = [
            frame
            for frame in self.selected_frames
            if 0 <= frame < self.frame_count()
        ]

        self.update()

    def set_selected_frames(
        self,
        frames: list[int],
    ) -> None:
        maximum = self.frame_count()

        self.selected_frames = [
            frame
            for frame in frames
            if 0 <= frame < maximum
        ]

        if self.selected_frames:
            self.last_clicked_frame = (
                self.selected_frames[-1]
            )

        else:
            self.last_clicked_frame = None

        self.update()

    def set_zoom(
        self,
        zoom: int,
    ) -> None:
        self.zoom = max(
            1,
            min(
                8,
                int(zoom),
            ),
        )

        self._update_size()

        self.update()

    def frame_count(
        self,
    ) -> int:
        return (
            self.columns
            * self.rows
        )

    def frame_rect(
        self,
        frame: int,
    ) -> QRect | None:
        if (
            frame < 0
            or frame >= self.frame_count()
            or self.columns <= 0
        ):
            return None

        column = (
            frame
            % self.columns
        )

        row = (
            frame
            // self.columns
        )

        return QRect(
            column * self.frame_width,
            row * self.frame_height,
            self.frame_width,
            self.frame_height,
        )

    def frame_pixmap(
        self,
        frame: int,
    ) -> QPixmap:
        rect = self.frame_rect(
            frame
        )

        if (
            rect is None
            or self.pixmap.isNull()
        ):
            return QPixmap()

        return self.pixmap.copy(
            rect
        )

    def _recalculate_grid(
        self,
    ) -> None:
        if self.pixmap.isNull():
            self.columns = 0
            self.rows = 0
            return

        self.columns = (
            self.pixmap.width()
            // self.frame_width
        )

        self.rows = (
            self.pixmap.height()
            // self.frame_height
        )

    def _update_size(
        self,
    ) -> None:
        if self.pixmap.isNull():
            self.setFixedSize(
                1,
                1,
            )
            return

        self.setFixedSize(
            self.pixmap.width()
            * self.zoom,
            self.pixmap.height()
            * self.zoom,
        )

    def _frame_at_position(
        self,
        position: QPoint,
    ) -> int | None:
        if (
            self.pixmap.isNull()
            or self.columns <= 0
            or self.rows <= 0
        ):
            return None

        cell_width = (
            self.frame_width
            * self.zoom
        )

        cell_height = (
            self.frame_height
            * self.zoom
        )

        column = (
            position.x()
            // cell_width
        )

        row = (
            position.y()
            // cell_height
        )

        if (
            column < 0
            or row < 0
            or column >= self.columns
            or row >= self.rows
        ):
            return None

        return (
            row
            * self.columns
            + column
        )

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            super().mousePressEvent(
                event
            )
            return

        frame = self._frame_at_position(
            event.position().toPoint()
        )

        if frame is None:
            return

        shift_pressed = bool(
            event.modifiers()
            & Qt.KeyboardModifier.ShiftModifier
        )

        if (
            shift_pressed
            and self.last_clicked_frame is not None
        ):
            self._select_range(
                self.last_clicked_frame,
                frame,
            )

        else:
            self._toggle_frame(
                frame
            )

        self.last_clicked_frame = frame

        self.update()

        self.frames_changed.emit(
            list(
                self.selected_frames
            )
        )

        event.accept()

    def _toggle_frame(
        self,
        frame: int,
    ) -> None:
        if frame in self.selected_frames:
            self.selected_frames.remove(
                frame
            )

        else:
            self.selected_frames.append(
                frame
            )

    def _select_range(
        self,
        start: int,
        end: int,
    ) -> None:
        first = min(
            start,
            end,
        )

        last = max(
            start,
            end,
        )

        for frame in range(
            first,
            last + 1,
        ):
            if frame not in self.selected_frames:
                self.selected_frames.append(
                    frame
                )

        self.selected_frames.sort()

    def paintEvent(
        self,
        event,
    ) -> None:
        del event

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform,
            False,
        )

        painter.fillRect(
            self.rect(),
            QColor("#15171b"),
        )

        if self.pixmap.isNull():
            return

        target = QRect(
            0,
            0,
            self.pixmap.width()
            * self.zoom,
            self.pixmap.height()
            * self.zoom,
        )

        painter.drawPixmap(
            target,
            self.pixmap,
        )

        self._draw_selected_frames(
            painter
        )

        self._draw_grid(
            painter
        )

        self._draw_frame_numbers(
            painter
        )

    def _draw_selected_frames(
        self,
        painter: QPainter,
    ) -> None:
        if (
            self.columns <= 0
            or self.rows <= 0
        ):
            return

        cell_width = (
            self.frame_width
            * self.zoom
        )

        cell_height = (
            self.frame_height
            * self.zoom
        )

        painter.setPen(
            QPen(
                QColor("#4f8cff"),
                2,
            )
        )

        painter.setBrush(
            QColor(
                37,
                99,
                235,
                95,
            )
        )

        for frame in self.selected_frames:
            column = (
                frame
                % self.columns
            )

            row = (
                frame
                // self.columns
            )

            rect = QRect(
                column * cell_width,
                row * cell_height,
                cell_width,
                cell_height,
            )

            painter.drawRect(
                rect.adjusted(
                    1,
                    1,
                    -1,
                    -1,
                )
            )

    def _draw_grid(
        self,
        painter: QPainter,
    ) -> None:
        if (
            self.columns <= 0
            or self.rows <= 0
        ):
            return

        pen = QPen(
            QColor(
                255,
                255,
                255,
                85,
            ),
            1,
        )

        pen.setCosmetic(
            True
        )

        painter.setPen(
            pen
        )

        cell_width = (
            self.frame_width
            * self.zoom
        )

        cell_height = (
            self.frame_height
            * self.zoom
        )

        total_width = (
            self.columns
            * cell_width
        )

        total_height = (
            self.rows
            * cell_height
        )

        for column in range(
            self.columns + 1
        ):
            x = (
                column
                * cell_width
            )

            painter.drawLine(
                x,
                0,
                x,
                total_height,
            )

        for row in range(
            self.rows + 1
        ):
            y = (
                row
                * cell_height
            )

            painter.drawLine(
                0,
                y,
                total_width,
                y,
            )

    def _draw_frame_numbers(
        self,
        painter: QPainter,
    ) -> None:
        if (
            self.columns <= 0
            or self.rows <= 0
        ):
            return

        font = QFont(
            painter.font()
        )

        font.setPixelSize(
            9
        )

        painter.setFont(
            font
        )

        cell_width = (
            self.frame_width
            * self.zoom
        )

        cell_height = (
            self.frame_height
            * self.zoom
        )

        for frame in range(
            self.frame_count()
        ):
            column = (
                frame
                % self.columns
            )

            row = (
                frame
                // self.columns
            )

            rect = QRect(
                column * cell_width + 2,
                row * cell_height + 2,
                max(
                    1,
                    cell_width - 4,
                ),
                12,
            )

            painter.fillRect(
                rect,
                QColor(
                    0,
                    0,
                    0,
                    140,
                ),
            )

            painter.setPen(
                QColor("#ffffff")
            )

            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignLeft
                | Qt.AlignmentFlag.AlignVCenter,
                str(frame),
            )


class AnimationSpriteSheetEditor(QWidget):
    """Editor visual de spritesheet, preview e timeline."""

    frames_changed = Signal(list)

    def __init__(self) -> None:
        super().__init__()

        self.project_root: Path | None = None
        self.entity: SceneEntity | None = None

        self.preview_frames: list[int] = []
        self.preview_fps = 6.0
        self.preview_loop = True
        self.preview_index = 0
        self.preview_paused = False

        self.preview_timer = QTimer(
            self
        )

        self.preview_timer.timeout.connect(
            self._advance_preview
        )

        self._build_ui()

        self._connect_signals()

    def _build_ui(
        self,
    ) -> None:
        self.setObjectName(
            "AnimationSpriteSheetEditor"
        )

        self.setStyleSheet(
            """
            QWidget#AnimationSpriteSheetEditor {
                background: transparent;
            }

            QFrame#AnimationPanel {
                background-color: #191b20;
                border: 1px solid #343840;
                border-radius: 6px;
            }

            QLabel#SectionTitle {
                font-weight: 600;
                font-size: 13px;
            }

            QLabel#MutedLabel {
                color: #8d929b;
            }

            QScrollArea#SpriteScroll {
                background-color: #111318;
                border: 1px solid #343840;
                border-radius: 4px;
            }

            QScrollArea#SpriteScroll > QWidget > QWidget {
                background-color: #111318;
            }

            QListWidget#AnimationTimeline {
                background-color: #111318;
                border: 1px solid #343840;
                border-radius: 4px;
                padding: 4px;
            }

            QListWidget#AnimationTimeline::item {
                min-width: 48px;
                min-height: 48px;
                border: 1px solid #343840;
                border-radius: 4px;
                margin-right: 3px;
                padding: 3px;
            }

            QListWidget#AnimationTimeline::item:hover {
                border: 1px solid #5a606b;
            }

            QListWidget#AnimationTimeline::item:selected {
                background-color: #2563eb;
                border: 1px solid #4f8cff;
            }

            QPushButton#SmallToolButton {
                min-width: 30px;
                max-width: 30px;
                min-height: 28px;
                max-height: 28px;
                padding: 0px;
            }
            """
        )

        self._build_preview_panel()

        self._build_sprite_panel()

        self._build_timeline_panel()

        self.editor_splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        self.editor_splitter.setChildrenCollapsible(
            False
        )

        self.editor_splitter.addWidget(
            self.preview_panel
        )

        self.editor_splitter.addWidget(
            self.sprite_panel
        )

        self.editor_splitter.setStretchFactor(
            0,
            1,
        )

        self.editor_splitter.setStretchFactor(
            1,
            3,
        )

        self.editor_splitter.setSizes(
            [
                300,
                850,
            ]
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            self.editor_splitter,
            1,
        )

        layout.addWidget(
            self.timeline_panel
        )

    def _build_preview_panel(
        self,
    ) -> None:
        self.preview_title = QLabel(
            "Preview"
        )

        self.preview_title.setObjectName(
            "SectionTitle"
        )

        self.preview_label = QLabel()

        self.preview_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.preview_label.setMinimumSize(
            220,
            220,
        )

        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.preview_label.setStyleSheet(
            """
            QLabel {
                border: 1px solid #343840;
                border-radius: 4px;
                background-color: #111318;
            }
            """
        )

        self.play_pause_button = QPushButton(
            "⏸"
        )

        self.restart_button = QPushButton(
            "↺"
        )

        for button in (
            self.play_pause_button,
            self.restart_button,
        ):
            button.setObjectName(
                "SmallToolButton"
            )

        self.play_pause_button.setToolTip(
            "Play / Pause"
        )

        self.restart_button.setToolTip(
            "Reiniciar preview"
        )

        controls = QHBoxLayout()

        controls.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        controls.setSpacing(
            5
        )

        controls.addWidget(
            self.play_pause_button
        )

        controls.addWidget(
            self.restart_button
        )

        controls.addStretch()

        self.preview_panel = QFrame()

        self.preview_panel.setObjectName(
            "AnimationPanel"
        )

        layout = QVBoxLayout(
            self.preview_panel
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            self.preview_title
        )

        layout.addWidget(
            self.preview_label,
            1,
        )

        layout.addLayout(
            controls
        )

    def _build_sprite_panel(
        self,
    ) -> None:
        self.title = QLabel(
            "Spritesheet"
        )

        self.title.setObjectName(
            "SectionTitle"
        )

        self.status = QLabel(
            "Nenhum Sprite disponível."
        )

        self.status.setObjectName(
            "MutedLabel"
        )

        self.selected_label = QLabel(
            "Selecionados: nenhum"
        )

        self.help_label = QLabel(
            "Clique para adicionar/remover um frame. "
            "Shift + clique seleciona um intervalo."
        )

        self.help_label.setObjectName(
            "MutedLabel"
        )

        self.help_label.setWordWrap(
            True
        )

        self.canvas = SpriteSheetCanvas()

        self.zoom_out_button = QPushButton(
            "−"
        )

        self.zoom_in_button = QPushButton(
            "+"
        )

        self.zoom_label = QLabel(
            "Zoom 2x"
        )

        for button in (
            self.zoom_out_button,
            self.zoom_in_button,
        ):
            button.setObjectName(
                "SmallToolButton"
            )

        self.zoom_out_button.setToolTip(
            "Diminuir zoom"
        )

        self.zoom_in_button.setToolTip(
            "Aumentar zoom"
        )

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        header.setSpacing(
            5
        )

        header.addWidget(
            self.title
        )

        header.addStretch()

        header.addWidget(
            self.zoom_out_button
        )

        header.addWidget(
            self.zoom_label
        )

        header.addWidget(
            self.zoom_in_button
        )

        self.canvas_container = QWidget()

        canvas_layout = QVBoxLayout(
            self.canvas_container
        )

        canvas_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        canvas_layout.setSpacing(
            0
        )

        canvas_layout.addWidget(
            self.canvas,
            0,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop,
        )

        canvas_layout.addStretch()

        self.sprite_scroll = QScrollArea()

        self.sprite_scroll.setObjectName(
            "SpriteScroll"
        )

        self.sprite_scroll.setWidgetResizable(
            True
        )

        self.sprite_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.sprite_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.sprite_scroll.setWidget(
            self.canvas_container
        )

        self.sprite_scroll.setMinimumSize(
            400,
            220,
        )

        self.sprite_panel = QFrame()

        self.sprite_panel.setObjectName(
            "AnimationPanel"
        )

        layout = QVBoxLayout(
            self.sprite_panel
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        layout.setSpacing(
            7
        )

        layout.addLayout(
            header
        )

        layout.addWidget(
            self.status
        )

        layout.addWidget(
            self.sprite_scroll,
            1,
        )

        layout.addWidget(
            self.selected_label
        )

        layout.addWidget(
            self.help_label
        )

    def _build_timeline_panel(
        self,
    ) -> None:
        self.timeline_title = QLabel(
            "Timeline"
        )

        self.timeline_title.setObjectName(
            "SectionTitle"
        )

        self.timeline = QListWidget()

        self.timeline.setObjectName(
            "AnimationTimeline"
        )

        self.timeline.setFlow(
            QListWidget.Flow.LeftToRight
        )

        self.timeline.setWrapping(
            False
        )

        self.timeline.setMinimumHeight(
            76
        )

        self.timeline.setMaximumHeight(
            96
        )

        self.timeline.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.timeline.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.move_left_button = QPushButton(
            "←"
        )

        self.move_right_button = QPushButton(
            "→"
        )

        self.duplicate_button = QPushButton(
            "Duplicar"
        )

        self.remove_timeline_button = QPushButton(
            "Remover"
        )

        for button in (
            self.move_left_button,
            self.move_right_button,
        ):
            button.setObjectName(
                "SmallToolButton"
            )

        self.move_left_button.setToolTip(
            "Mover frame para esquerda"
        )

        self.move_right_button.setToolTip(
            "Mover frame para direita"
        )

        self.duplicate_button.setToolTip(
            "Duplicar frame selecionado"
        )

        self.remove_timeline_button.setToolTip(
            "Remover frame da sequência"
        )

        self.duplicate_button.setMinimumHeight(
            28
        )

        self.remove_timeline_button.setMinimumHeight(
            28
        )

        controls = QHBoxLayout()

        controls.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        controls.setSpacing(
            5
        )

        controls.addWidget(
            self.move_left_button
        )

        controls.addWidget(
            self.move_right_button
        )

        controls.addSpacing(
            5
        )

        controls.addWidget(
            self.duplicate_button
        )

        controls.addWidget(
            self.remove_timeline_button
        )

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        header.addWidget(
            self.timeline_title
        )

        header.addStretch()

        header.addLayout(
            controls
        )

        self.timeline_panel = QFrame()

        self.timeline_panel.setObjectName(
            "AnimationPanel"
        )

        layout = QVBoxLayout(
            self.timeline_panel
        )

        layout.setContentsMargins(
            10,
            8,
            10,
            8,
        )

        layout.setSpacing(
            6
        )

        layout.addLayout(
            header
        )

        layout.addWidget(
            self.timeline
        )

    def _connect_signals(
        self,
    ) -> None:
        self.canvas.frames_changed.connect(
            self._on_frames_changed
        )

        self.zoom_out_button.clicked.connect(
            self._zoom_out
        )

        self.zoom_in_button.clicked.connect(
            self._zoom_in
        )

        self.play_pause_button.clicked.connect(
            self._toggle_preview
        )

        self.restart_button.clicked.connect(
            self._restart_preview
        )

        self.move_left_button.clicked.connect(
            self._move_frame_left
        )

        self.move_right_button.clicked.connect(
            self._move_frame_right
        )

        self.duplicate_button.clicked.connect(
            self._duplicate_frame
        )

        self.remove_timeline_button.clicked.connect(
            self._remove_frame_from_timeline
        )

    def set_context(
        self,
        project_root: Path | None,
        entity: SceneEntity | None,
    ) -> None:
        self.project_root = (
            project_root.resolve()
            if project_root is not None
            else None
        )

        self.entity = entity

        self._load_sprite()

    def set_frame_size(
        self,
        width: int,
        height: int,
    ) -> None:
        self.canvas.set_frame_size(
            width,
            height,
        )

        self._update_status()

        self._restart_preview()

    def set_frames(
        self,
        frames: list[int],
    ) -> None:
        self.canvas.set_selected_frames(
            frames
        )

        self.preview_frames = list(
            frames
        )

        self.preview_index = 0

        self._update_selected_label()

        self._refresh_timeline()

        self._restart_preview()

    def set_preview_settings(
        self,
        frames: list[int],
        fps: float,
        loop: bool,
    ) -> None:
        self.preview_frames = [
            frame
            for frame in frames
            if 0 <= frame < self.canvas.frame_count()
        ]

        self.preview_fps = max(
            0.01,
            float(fps),
        )

        self.preview_loop = bool(
            loop
        )

        self.preview_index = 0

        self._refresh_timeline()

        self._restart_preview()

    def _load_sprite(
        self,
    ) -> None:
        self.canvas.clear()

        self.preview_timer.stop()

        self.preview_label.clear()

        self.timeline.clear()

        if (
            self.project_root is None
            or self.entity is None
            or self.entity.sprite is None
            or not self.entity.sprite.asset_id
        ):
            self.status.setText(
                "Nenhum Sprite disponível."
            )

            self._update_selected_label()

            return

        registry = AssetRegistry(
            self.project_root
        )

        record = registry.find_by_id(
            self.entity.sprite.asset_id
        )

        if record is None:
            self.status.setText(
                "Sprite não encontrado no projeto."
            )

            self._update_selected_label()

            return

        path = (
            self.project_root
            / record.path
        )

        pixmap = QPixmap(
            str(path)
        )

        if pixmap.isNull():
            self.status.setText(
                "Não foi possível carregar o Sprite."
            )

            self._update_selected_label()

            return

        self.canvas.set_pixmap(
            pixmap
        )

        self._update_status()

        self._update_selected_label()

        self._refresh_timeline()

        self._restart_preview()

    def _update_status(
        self,
    ) -> None:
        if self.canvas.pixmap.isNull():
            return

        self.status.setText(
            f"{self.canvas.columns} coluna(s) × "
            f"{self.canvas.rows} linha(s) — "
            f"{self.canvas.frame_count()} frame(s)"
        )

    def _update_selected_label(
        self,
    ) -> None:
        frames = self.canvas.selected_frames

        if not frames:
            self.selected_label.setText(
                "Selecionados: nenhum"
            )

            return

        self.selected_label.setText(
            "Selecionados: "
            + ", ".join(
                str(frame)
                for frame in frames
            )
        )

    def _on_frames_changed(
        self,
        frames: list[int],
    ) -> None:
        self.preview_frames = list(
            frames
        )

        self.preview_index = 0

        self._update_selected_label()

        self._refresh_timeline()

        self._restart_preview()

        self.frames_changed.emit(
            list(
                self.preview_frames
            )
        )

    def _refresh_timeline(
        self,
    ) -> None:
        current_row = (
            self.timeline.currentRow()
        )

        self.timeline.clear()

        for frame in self.preview_frames:
            item = QListWidgetItem(
                str(frame)
            )

            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.timeline.addItem(
                item
            )

        if (
            self.timeline.count() > 0
            and current_row >= 0
        ):
            self.timeline.setCurrentRow(
                min(
                    current_row,
                    self.timeline.count() - 1,
                )
            )

    def _move_frame_left(
        self,
    ) -> None:
        row = (
            self.timeline.currentRow()
        )

        if (
            row <= 0
            or row >= len(
                self.preview_frames
            )
        ):
            return

        self.preview_frames[
            row - 1
        ], self.preview_frames[row] = (
            self.preview_frames[row],
            self.preview_frames[row - 1],
        )

        self._commit_timeline(
            row - 1
        )

    def _move_frame_right(
        self,
    ) -> None:
        row = (
            self.timeline.currentRow()
        )

        if (
            row < 0
            or row >= len(
                self.preview_frames
            ) - 1
        ):
            return

        self.preview_frames[
            row
        ], self.preview_frames[
            row + 1
        ] = (
            self.preview_frames[
                row + 1
            ],
            self.preview_frames[
                row
            ],
        )

        self._commit_timeline(
            row + 1
        )

    def _duplicate_frame(
        self,
    ) -> None:
        row = (
            self.timeline.currentRow()
        )

        if (
            row < 0
            or row >= len(
                self.preview_frames
            )
        ):
            return

        self.preview_frames.insert(
            row + 1,
            self.preview_frames[
                row
            ],
        )

        self._commit_timeline(
            row + 1
        )

    def _remove_frame_from_timeline(
        self,
    ) -> None:
        row = (
            self.timeline.currentRow()
        )

        if (
            row < 0
            or row >= len(
                self.preview_frames
            )
        ):
            return

        del self.preview_frames[
            row
        ]

        self._commit_timeline(
            min(
                row,
                len(
                    self.preview_frames
                ) - 1,
            )
        )

    def _commit_timeline(
        self,
        selected_row: int,
    ) -> None:
        self.canvas.set_selected_frames(
            list(
                dict.fromkeys(
                    self.preview_frames
                )
            )
        )

        self._update_selected_label()

        self._refresh_timeline()

        if selected_row >= 0:
            self.timeline.setCurrentRow(
                selected_row
            )

        self.preview_index = 0

        self._restart_preview()

        self.frames_changed.emit(
            list(
                self.preview_frames
            )
        )

    def _zoom_in(
        self,
    ) -> None:
        self.canvas.set_zoom(
            self.canvas.zoom
            + 1
        )

        self._update_zoom_label()

    def _zoom_out(
        self,
    ) -> None:
        self.canvas.set_zoom(
            self.canvas.zoom
            - 1
        )

        self._update_zoom_label()

    def _update_zoom_label(
        self,
    ) -> None:
        self.zoom_label.setText(
            f"Zoom {self.canvas.zoom}x"
        )

    def _toggle_preview(
        self,
    ) -> None:
        if not self.preview_frames:
            return

        self.preview_paused = (
            not self.preview_paused
        )

        if self.preview_paused:
            self.preview_timer.stop()

            self.play_pause_button.setText(
                "▶"
            )

        else:
            self.play_pause_button.setText(
                "⏸"
            )

            self._start_preview_timer()

    def _restart_preview(
        self,
    ) -> None:
        self.preview_timer.stop()

        self.preview_paused = False

        self.play_pause_button.setText(
            "⏸"
        )

        if (
            not self.preview_frames
            or self.canvas.pixmap.isNull()
        ):
            self.preview_label.clear()

            return

        self.preview_index = 0

        self._show_preview_frame()

        self._start_preview_timer()

    def _start_preview_timer(
        self,
    ) -> None:
        if (
            self.preview_paused
            or len(
                self.preview_frames
            ) <= 1
        ):
            return

        interval = max(
            1,
            int(
                1000.0
                / self.preview_fps
            ),
        )

        self.preview_timer.start(
            interval
        )

    def _advance_preview(
        self,
    ) -> None:
        if not self.preview_frames:
            self.preview_timer.stop()

            return

        self.preview_index += 1

        if (
            self.preview_index
            >= len(
                self.preview_frames
            )
        ):
            if self.preview_loop:
                self.preview_index = 0

            else:
                self.preview_index = (
                    len(
                        self.preview_frames
                    )
                    - 1
                )

                self.preview_timer.stop()

                self.preview_paused = True

                self.play_pause_button.setText(
                    "▶"
                )

        self._show_preview_frame()

    def _show_preview_frame(
        self,
    ) -> None:
        if not self.preview_frames:
            self.preview_label.clear()

            return

        frame = (
            self.preview_frames[
                self.preview_index
            ]
        )

        pixmap = (
            self.canvas.frame_pixmap(
                frame
            )
        )

        if pixmap.isNull():
            self.preview_label.clear()

            return

        available = (
            self.preview_label.size()
        )

        scaled = pixmap.scaled(
            max(
                1,
                available.width()
                - 12,
            ),
            max(
                1,
                available.height()
                - 12,
            ),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )

        self.preview_label.setPixmap(
            scaled
        )

    def resizeEvent(
        self,
        event,
    ) -> None:
        super().resizeEvent(
            event
        )

        if self.preview_frames:
            self._show_preview_frame()