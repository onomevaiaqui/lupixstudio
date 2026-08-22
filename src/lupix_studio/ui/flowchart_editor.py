from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QKeyEvent,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QGraphicsDropShadowEffect,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

NODE_DEFINITIONS = {
    "scene_start": ("Eventos", "Ao iniciar", "#b94a5a", (), ("out",)),
    "player_death": ("Eventos", "Ao morrer", "#b94a5a", (), ("out",)),
    "key_pressed": ("Eventos", "Ao pressionar tecla", "#b94a5a", (), ("out",)),
    "area_entered": ("Eventos", "Ao entrar na área", "#b94a5a", (), ("out",)),
    "clicked": ("Eventos", "Ao clicar", "#b94a5a", (), ("out",)),
    "change_scene": ("Ações", "Trocar cena", "#3478b9", ("in",), ("out",)),
    "fade": ("Ações", "Fade", "#3478b9", ("in",), ("out",)),
    "wait": ("Ações", "Esperar", "#3478b9", ("in",), ("out",)),
    "respawn": ("Ações", "Respawn", "#3478b9", ("in",), ("out",)),
    "play_animation": ("Ações", "Tocar animação", "#3478b9", ("in",), ("out",)),
    "show_message": ("Ações", "Mostrar mensagem", "#3478b9", ("in",), ("out",)),
    "damage": ("Ações", "Causar dano", "#3478b9", ("in",), ("out",)),
    "player_controller": ("Ações", "Player Controller", "#3478b9", ("in",), ("out",)),
    "branch": ("Controle", "Se", "#bd8b32", ("in",), ("true", "false")),
    "sequence": ("Controle", "Sequência", "#bd8b32", ("in",), ("then_1", "then_2")),
}

CATEGORY_GRADIENTS = {
    "Eventos": ("#ef3d92", "#8e3de3"),
    "Ações": ("#643ee8", "#3479d9"),
    "Controle": ("#e89032", "#d54878"),
    "Outros": ("#7656b8", "#4f628e"),
}

NODE_GRADIENTS = {
    "change_scene": ("#d936a5", "#743be4"),
    "show_message": ("#287fc7", "#35a7b7"),
    "wait": ("#6941d9", "#395fcf"),
    "play_animation": ("#e36b35", "#d63c93"),
    "damage": ("#d83b4f", "#a82f77"),
    "respawn": ("#268a83", "#3b63ca"),
    "fade": ("#7650c7", "#46537f"),
}

KEY_OPTIONS = {
    "Espaço": "space",
    "Enter": "enter",
    "Seta esquerda": "left",
    "Seta direita": "right",
    "Seta acima": "up",
    "Seta abaixo": "down",
    "A": "a",
    "D": "d",
    "W": "w",
    "S": "s",
    "E": "e",
    "F": "f",
}

NODE_WIDTH = 210
NODE_MIN_HEIGHT = 154

PORT_LABELS = {
    "in": "Entrada",
    "out": "Saída",
    "true": "Verdadeiro",
    "false": "Falso",
    "then_1": "1",
    "then_2": "2",
}


class FlowPort(QGraphicsEllipseItem):
    def __init__(
        self,
        node_item: FlowNode,
        name: str,
        is_output: bool,
        y: float,
    ) -> None:
        super().__init__(-6, -6, 12, 12, node_item)
        self.node_item = node_item
        self.name = name
        self.is_output = is_output
        self.normal_color = QColor("#7332df" if is_output else "#f032a0")
        self.setBrush(self.normal_color)
        self.setPen(QPen(QColor("#ffffff"), 2))
        self.setAcceptHoverEvents(True)
        self.setToolTip(PORT_LABELS.get(name, name))
        self.setPos(NODE_WIDTH if is_output else 0, y)

    def hoverEnterEvent(self, event) -> None:
        self.setBrush(QColor("#ffffff"))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self.setBrush(self.normal_color)
        super().hoverLeaveEvent(event)


class FlowNode(QGraphicsRectItem):
    def __init__(self, node: dict[str, object], editor: FlowchartEditor) -> None:
        definition = NODE_DEFINITIONS.get(
            str(node.get("type")),
            ("Outros", str(node.get("type")), "#596273", ("in",), ("out",)),
        )
        inputs = definition[3]
        outputs = definition[4]
        rows = max(len(inputs), len(outputs), 1)
        height = max(NODE_MIN_HEIGHT, 122 + rows * 26)
        super().__init__(0, 0, NODE_WIDTH, height)
        self.node = node
        self.editor = editor
        self.category = str(definition[0])
        self.gradient_colors = NODE_GRADIENTS.get(
            str(node.get("type")),
            CATEGORY_GRADIENTS.get(
                self.category,
                CATEGORY_GRADIENTS["Outros"],
            ),
        )
        self.ports: dict[tuple[str, bool], FlowPort] = {}
        self.setBrush(Qt.BrushStyle.NoBrush)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(44, 35, 65, 105))
        self.setGraphicsEffect(shadow)

        self._add_inline_editor()

        for index, name in enumerate(inputs):
            y = 126 + index * 26
            port = FlowPort(self, name, False, y)
            self.ports[(name, False)] = port

        for index, name in enumerate(outputs):
            y = 126 + index * 26
            port = FlowPort(self, name, True, y)
            self.ports[(name, True)] = port

        self.setPos(float(node.get("x", 0)), float(node.get("y", 0)))

    def _add_inline_editor(self) -> None:
        kind = str(self.node.get("type", ""))
        control = None
        if kind == "wait":
            spin = QDoubleSpinBox()
            spin.setRange(0.0, 3600.0)
            spin.setDecimals(2)
            spin.setSuffix(" s")
            spin.setValue(float(self.node.get("seconds", 1.0)))
            spin.valueChanged.connect(
                lambda value: self._set_node_value("seconds", value)
            )
            control = spin
        elif kind == "show_message":
            edit = QLineEdit(str(self.node.get("message_text", "Olá, mundo!")))
            edit.setPlaceholderText("Mensagem...")
            edit.textChanged.connect(
                lambda value: self._set_node_value("message_text", value)
            )
            control = edit
        elif kind == "key_pressed":
            combo = QComboBox()
            current = str(self.node.get("key", "space"))
            for label, value in KEY_OPTIONS.items():
                combo.addItem(label, value)
                if value == current:
                    combo.setCurrentIndex(combo.count() - 1)
            combo.currentIndexChanged.connect(
                lambda _index: self._set_node_value("key", combo.currentData())
            )
            control = combo
        elif kind == "change_scene":
            combo = QComboBox()
            scenes = self.editor._available_scenes()
            current = str(self.node.get("target_scene", ""))
            if current and current not in scenes:
                scenes.insert(0, current)
            combo.addItems(scenes)
            if current in scenes:
                combo.setCurrentText(current)
            combo.currentTextChanged.connect(
                lambda value: self._set_node_value("target_scene", value)
            )
            control = combo
        elif kind == "play_animation":
            combo = QComboBox()
            animation = getattr(self.editor.entity, "animation", None)
            clips = sorted(animation.clips) if animation is not None else []
            current = str(self.node.get("animation_name", ""))
            if current and current not in clips:
                clips.insert(0, current)
            combo.addItems(clips)
            if current in clips:
                combo.setCurrentText(current)
            combo.currentTextChanged.connect(
                lambda value: self._set_node_value("animation_name", value)
            )
            control = combo

        if control is None:
            description = QLineEdit("Sem configuração")
            description.setReadOnly(True)
            control = description
        control.setFixedHeight(30)
        control.setStyleSheet(
            "QLineEdit, QComboBox, QDoubleSpinBox {"
            " color: #f4f1f8; background: #1b1821;"
            " border: 1px solid #5b5368; border-radius: 9px;"
            " padding: 4px 11px; font-size: 13px; }"
            "QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {"
            " border: 1px solid #c94be5; }"
            "QComboBox QAbstractItemView {"
            " color: #f4f1f8; background: #24212d;"
            " selection-background-color: #713bdd; }"
        )
        block_title = str(
            NODE_DEFINITIONS.get(
                kind,
                ("Outros", kind, "", (), ()),
            )[1]
        )
        field_label = QLabel(block_title)
        field_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        field_label.setFixedSize(182, 29)
        field_label.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True,
        )
        field_label.setStyleSheet(
            "QLabel { color: #f2eef6; font-size: 15px;"
            " font-weight: 500; background: transparent; border: none; }"
        )
        title_proxy = QGraphicsProxyWidget(self)
        title_proxy.setWidget(field_label)
        title_proxy.setPos(14, 19)

        control.setFixedSize(182, 30)
        control_proxy = QGraphicsProxyWidget(self)
        control_proxy.setWidget(control)
        control_proxy.setPos(14, 67)

    def _set_node_value(self, key: str, value) -> None:
        self.node[key] = value
        self.editor._emit_changed()

    def paint(self, painter, option, widget=None) -> None:
        del widget
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        body = QPainterPath()
        body.addRoundedRect(self.rect(), 17, 17)
        selected = bool(
            option.state
            & QStyle.StateFlag.State_Selected
        )
        border_color = QColor("#d75be9" if selected else "#443d50")
        painter.setPen(QPen(border_color, 3 if selected else 1.2))
        painter.setBrush(QColor("#24212d"))
        painter.drawPath(body)

        gradient = QLinearGradient(0, 0, NODE_WIDTH, 0)
        gradient.setColorAt(0.0, QColor(self.gradient_colors[0]))
        gradient.setColorAt(1.0, QColor(self.gradient_colors[1]))
        painter.save()
        painter.setClipPath(body)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, NODE_WIDTH, 24)
        painter.restore()

    def mouseDoubleClickEvent(self, event) -> None:
        super().mouseDoubleClickEvent(event)

    def port(self, name: str, is_output: bool) -> FlowPort | None:
        return self.ports.get((name, is_output))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.editor.update_connection_paths()
        return super().itemChange(change, value)


class FlowConnection(QGraphicsPathItem):
    def __init__(
        self,
        data: dict[str, object],
        source: FlowPort,
        target: FlowPort,
    ) -> None:
        super().__init__()
        self.data = data
        self.source = source
        self.target = target
        self.setPen(QPen(QColor("#8b35df"), 3))
        self.setZValue(-1)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.update_path()

    def update_path(self) -> None:
        start = self.source.scenePos()
        end = self.target.scenePos()
        distance = max(70.0, abs(end.x() - start.x()) * 0.5)
        path = QPainterPath(start)
        path.cubicTo(
            QPointF(start.x() + distance, start.y()),
            QPointF(end.x() - distance, end.y()),
            end,
        )
        self.setPath(path)


class NodeSearchDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Adicionar bloco")
        self.resize(420, 480)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Pesquisar evento, ação ou controle...")
        self.results = QListWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Adicionar bloco ao Flowchart"))
        layout.addWidget(self.search)
        layout.addWidget(self.results)
        self.search.textChanged.connect(self._refresh)
        self.results.itemDoubleClicked.connect(lambda _item: self.accept())
        self._refresh()
        self.search.setFocus()

    def _refresh(self) -> None:
        query = self.search.text().strip().casefold()
        self.results.clear()
        definitions = sorted(
            NODE_DEFINITIONS.items(),
            key=lambda item: (item[1][0], item[1][1]),
        )
        for kind, definition in definitions:
            searchable = f"{definition[0]} {definition[1]}".casefold()
            if query and query not in searchable:
                continue
            item = QListWidgetItem(f"{definition[0]}  ›  {definition[1]}")
            item.setData(Qt.ItemDataRole.UserRole, kind)
            self.results.addItem(item)
        if self.results.count():
            self.results.setCurrentRow(0)

    def selected_kind(self) -> str | None:
        item = self.results.currentItem()
        if item is None:
            return None
        return str(item.data(Qt.ItemDataRole.UserRole))


class FlowCanvas(QGraphicsView):
    add_node_requested = Signal(QPointF)
    connection_requested = Signal(object, object)
    delete_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setBackgroundBrush(QColor("#17151d"))
        self.setStyleSheet(
            "QGraphicsView { border: 1px solid #302b38; border-radius: 12px; }"
        )
        self._source_port: FlowPort | None = None
        self._preview_connection: QGraphicsPathItem | None = None

    def wheelEvent(self, event) -> None:
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
        event.accept()

    def contextMenuEvent(self, event) -> None:
        self.add_node_requested.emit(self.mapToScene(event.pos()))
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self.delete_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event) -> None:
        item = self.itemAt(event.pos())
        if (
            event.button() == Qt.MouseButton.LeftButton
            and isinstance(item, FlowPort)
            and item.is_output
        ):
            self._source_port = item
            self._preview_connection = QGraphicsPathItem()
            self._preview_connection.setPen(
                QPen(QColor("#a832df"), 3, Qt.PenStyle.DashLine)
            )
            self._preview_connection.setZValue(-1)
            self.scene().addItem(self._preview_connection)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._source_port is not None and self._preview_connection is not None:
            start = self._source_port.scenePos()
            end = self.mapToScene(event.pos())
            distance = max(70.0, abs(end.x() - start.x()) * 0.5)
            path = QPainterPath(start)
            path.cubicTo(
                QPointF(start.x() + distance, start.y()),
                QPointF(end.x() - distance, end.y()),
                end,
            )
            self._preview_connection.setPath(path)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._source_port is not None:
            item = self.itemAt(event.pos())
            if (
                isinstance(item, FlowPort)
                and not item.is_output
                and item.node_item is not self._source_port.node_item
            ):
                self.connection_requested.emit(self._source_port, item)
            if self._preview_connection is not None:
                self.scene().removeItem(self._preview_connection)
            self._source_port = None
            self._preview_connection = None
            event.accept()
            return
        super().mouseReleaseEvent(event)


class FlowchartEditor(QWidget):
    back_requested = Signal()
    flow_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.entity = None
        self.project_root: Path | None = None
        self.canvas = FlowCanvas()
        self.node_items: dict[str, FlowNode] = {}
        self.connection_items: list[FlowConnection] = []
        self.pending_position = QPointF()

        self.entity_label = QLabel("Nenhuma entidade selecionada")
        self.entity_label.setObjectName("ViewportTitle")
        add_button = QPushButton("+ Adicionar bloco")
        delete_button = QPushButton("Excluir selecionado")
        save_button = QPushButton("Salvar Flowchart")
        bar = QHBoxLayout()
        bar.addWidget(self.entity_label)
        bar.addStretch()
        bar.addWidget(add_button)
        bar.addWidget(delete_button)
        bar.addWidget(save_button)
        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.canvas)

        add_button.clicked.connect(self._add_from_toolbar)
        delete_button.clicked.connect(self.delete_selected)
        save_button.clicked.connect(self.save_flow)
        self.canvas.add_node_requested.connect(self.open_node_search)
        self.canvas.connection_requested.connect(self.connect_ports)
        self.canvas.delete_requested.connect(self.delete_selected)

    def set_project_root(self, project_root: Path) -> None:
        self.project_root = project_root

    def open_flow(self, entity) -> None:
        if self.entity is not None and self.entity is not entity:
            self.save_flow()
        self.entity = entity
        self.entity_label.setText(f"Flowchart — {entity.name}")
        self.canvas.scene().clear()
        self.node_items.clear()
        self.connection_items.clear()
        data = entity.blueprint or {"version": 3, "nodes": [], "connections": []}
        self._migrate_legacy_data(data)
        for node in data.get("nodes", []):
            if isinstance(node, dict):
                item = FlowNode(node, self)
                self.node_items[str(node.get("id"))] = item
                self.canvas.scene().addItem(item)
        for connection in data.get("connections", []):
            if isinstance(connection, dict) and "from_node" in connection:
                self._add_connection_item(connection)
        self.canvas.scene().setSceneRect(-2000, -1500, 4000, 3000)

    def _migrate_legacy_data(self, data: dict[str, object]) -> None:
        nodes = data.setdefault("nodes", [])
        connections = data.setdefault("connections", [])
        if not isinstance(nodes, list) or not isinstance(connections, list):
            return
        legacy = [
            link for link in connections
            if isinstance(link, dict) and "event" in link and "action" in link
        ]
        modern = [
            link for link in connections
            if isinstance(link, dict) and "from_node" in link
        ]
        if not legacy:
            return
        if not nodes:
            x = 40.0
            for link in legacy:
                event_node = {
                    "id": uuid4().hex,
                    "type": link.get("event"),
                    "x": x,
                    "y": 80.0,
                }
                action_node = {
                    "id": uuid4().hex,
                    "type": link.get("action"),
                    "target_scene": link.get("target_scene", ""),
                    "seconds": link.get("seconds", 0),
                    "x": x + 300.0,
                    "y": 80.0,
                }
                nodes.extend((event_node, action_node))
                modern.append(
                    {
                        "id": uuid4().hex,
                        "from_node": event_node["id"],
                        "from_port": "out",
                        "to_node": action_node["id"],
                        "to_port": "in",
                    }
                )
                x += 35.0
        else:
            unused = list(nodes)
            for link in legacy:
                event_node = next(
                    (node for node in unused if node.get("type") == link.get("event")),
                    None,
                )
                if event_node is not None:
                    unused.remove(event_node)
                action_node = next(
                    (node for node in unused if node.get("type") == link.get("action")),
                    None,
                )
                if action_node is not None:
                    unused.remove(action_node)
                if event_node is not None and action_node is not None:
                    modern.append(
                        {
                            "id": uuid4().hex,
                            "from_node": event_node.get("id"),
                            "from_port": "out",
                            "to_node": action_node.get("id"),
                            "to_port": "in",
                        }
                    )
        data["version"] = 3
        data["connections"] = modern
        self.entity.blueprint = data

    def _add_from_toolbar(self) -> None:
        self.open_node_search(
            self.canvas.mapToScene(self.canvas.viewport().rect().center())
        )

    def open_node_search(self, position: QPointF) -> None:
        if self.entity is None:
            return
        dialog = NodeSearchDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        kind = dialog.selected_kind()
        if kind:
            self.add_node(kind, position)

    def add_node(self, kind: str, position: QPointF) -> None:
        if self.entity is None:
            return
        if self.entity.blueprint is None:
            self.entity.blueprint = {
                "version": 3,
                "nodes": [],
                "connections": [],
            }
        node = {
            "id": uuid4().hex,
            "type": kind,
            "x": position.x(),
            "y": position.y(),
        }
        if kind == "wait":
            node["seconds"] = 1.0
        elif kind == "key_pressed":
            node["key"] = "space"
        elif kind == "change_scene":
            node["target_scene"] = ""
        elif kind == "play_animation":
            node["animation_name"] = ""
        elif kind == "show_message":
            node["message_text"] = "Olá, mundo!"
            node["duration"] = 4.0
        self.entity.blueprint.setdefault("nodes", []).append(node)
        item = FlowNode(node, self)
        self.node_items[str(node["id"])] = item
        self.canvas.scene().addItem(item)
        self._emit_changed()

    def edit_node(self, item: FlowNode) -> None:
        kind = str(item.node.get("type", ""))
        changed = False
        if kind == "wait":
            value, accepted = QInputDialog.getDouble(
                self,
                "Configurar Esperar",
                "Tempo em segundos:",
                float(item.node.get("seconds", 1.0)),
                0.0,
                3600.0,
                2,
            )
            if accepted:
                item.node["seconds"] = value
                changed = True
        elif kind == "show_message":
            value, accepted = QInputDialog.getMultiLineText(
                self,
                "Configurar mensagem",
                "Texto exibido no Preview:",
                str(item.node.get("message_text", "Olá, mundo!")),
            )
            if accepted:
                item.node["message_text"] = value
                changed = True
        elif kind == "key_pressed":
            labels = list(KEY_OPTIONS)
            current_key = str(item.node.get("key", "space"))
            current_label = next(
                (
                    label
                    for label, value in KEY_OPTIONS.items()
                    if value == current_key
                ),
                labels[0],
            )
            value, accepted = QInputDialog.getItem(
                self,
                "Configurar tecla",
                "Executar quando pressionar:",
                labels,
                labels.index(current_label),
                False,
            )
            if accepted:
                item.node["key"] = KEY_OPTIONS[value]
                changed = True
        elif kind == "play_animation":
            animation = getattr(self.entity, "animation", None)
            clips = sorted(animation.clips) if animation is not None else []
            current = str(item.node.get("animation_name", ""))
            if current and current not in clips:
                clips.insert(0, current)
            if clips:
                initial = clips.index(current) if current in clips else 0
                value, accepted = QInputDialog.getItem(
                    self,
                    "Configurar animação",
                    "Animação do Player:",
                    clips,
                    initial,
                    False,
                )
                if accepted:
                    item.node["animation_name"] = value
                    changed = True
        elif kind == "change_scene":
            scenes = self._available_scenes()
            current = str(item.node.get("target_scene", ""))
            if current and current not in scenes:
                scenes.insert(0, current)
            if not scenes:
                scenes = [current] if current else ["scenes/Main.scene"]
            initial = scenes.index(current) if current in scenes else 0
            value, accepted = QInputDialog.getItem(
                self,
                "Configurar troca de cena",
                "Cena de destino:",
                scenes,
                initial,
                False,
            )
            if accepted:
                item.node["target_scene"] = value
                changed = True
        if changed:
            self.save_flow()
            self.open_flow(self.entity)

    def _available_scenes(self) -> list[str]:
        if self.project_root is None:
            return []
        scenes_root = self.project_root / "scenes"
        if not scenes_root.is_dir():
            return []
        return [
            path.relative_to(self.project_root).as_posix()
            for path in sorted(scenes_root.rglob("*.scene"))
        ]

    def connect_ports(self, source: FlowPort, target: FlowPort) -> None:
        if self.entity is None:
            return
        if self.entity.blueprint is None:
            return
        connections = self.entity.blueprint.setdefault("connections", [])
        connections[:] = [
            item for item in connections
            if not (
                item.get("from_node") == source.node_item.node.get("id")
                and item.get("from_port") == source.name
            )
            and not (
                item.get("to_node") == target.node_item.node.get("id")
                and item.get("to_port") == target.name
            )
        ]
        data = {
            "id": uuid4().hex,
            "from_node": source.node_item.node.get("id"),
            "from_port": source.name,
            "to_node": target.node_item.node.get("id"),
            "to_port": target.name,
        }
        connections.append(data)
        self._rebuild_connections()
        self._emit_changed()

    def _add_connection_item(self, data: dict[str, object]) -> None:
        source_node = self.node_items.get(str(data.get("from_node")))
        target_node = self.node_items.get(str(data.get("to_node")))
        if source_node is None or target_node is None:
            return
        source = source_node.port(str(data.get("from_port", "out")), True)
        target = target_node.port(str(data.get("to_port", "in")), False)
        if source is None or target is None:
            return
        item = FlowConnection(data, source, target)
        self.connection_items.append(item)
        self.canvas.scene().addItem(item)

    def _rebuild_connections(self) -> None:
        for item in self.connection_items:
            self.canvas.scene().removeItem(item)
        self.connection_items.clear()
        if self.entity is None or self.entity.blueprint is None:
            return
        for data in self.entity.blueprint.get("connections", []):
            if isinstance(data, dict):
                self._add_connection_item(data)

    def update_connection_paths(self) -> None:
        for item in self.connection_items:
            item.update_path()

    def delete_selected(self) -> None:
        if self.entity is None or self.entity.blueprint is None:
            return
        selected = self.canvas.scene().selectedItems()
        node_ids = {
            str(item.node.get("id")) for item in selected if isinstance(item, FlowNode)
        }
        connection_ids = {
            str(item.data.get("id"))
            for item in selected
            if isinstance(item, FlowConnection)
        }
        if not node_ids and not connection_ids:
            return
        nodes = self.entity.blueprint.setdefault("nodes", [])
        nodes[:] = [node for node in nodes if str(node.get("id")) not in node_ids]
        connections = self.entity.blueprint.setdefault("connections", [])
        connections[:] = [
            item for item in connections
            if str(item.get("id")) not in connection_ids
            and str(item.get("from_node")) not in node_ids
            and str(item.get("to_node")) not in node_ids
        ]
        self.open_flow(self.entity)
        self._emit_changed()

    def save_flow(self) -> None:
        if self.entity is None or self.entity.blueprint is None:
            return
        for node_id, item in self.node_items.items():
            item.node["id"] = node_id
            item.node["x"] = item.pos().x()
            item.node["y"] = item.pos().y()
        self._emit_changed()

    def _emit_changed(self) -> None:
        if self.entity is not None:
            self.flow_changed.emit(self.entity.id)
