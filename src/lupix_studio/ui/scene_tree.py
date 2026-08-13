from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMenu,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import (
    SceneEntity,
    SceneResource,
)


class SceneTree(QWidget):
    """Hierarquia visual de uma Scene."""

    entity_selected = Signal(str)

    component_selected = Signal(
        str,
        str,
    )

    scene_changed = Signal()

    NODE_SCENE = "scene"
    NODE_ENTITY = "entity"
    NODE_COMPONENT = "component"

    ROLE_NODE_TYPE = (
        Qt.ItemDataRole.UserRole + 1
    )

    ROLE_COMPONENT = (
        Qt.ItemDataRole.UserRole + 2
    )

    def __init__(self) -> None:
        super().__init__()

        self.resource: SceneResource | None = None

        self.tree = QTreeWidget()

        self.tree.setHeaderLabel(
            "Hierarquia"
        )

        self.tree.setAlternatingRowColors(
            True
        )

        self.tree.setIndentation(
            18
        )

        self.tree.setAnimated(
            True
        )

        self.tree.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.add_button = QPushButton(
            "+ Entidade"
        )

        self.remove_button = QPushButton(
            "- Remover"
        )

        controls = QHBoxLayout()

        controls.addWidget(
            self.add_button
        )

        controls.addWidget(
            self.remove_button
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

        layout.addLayout(
            controls
        )

        layout.addWidget(
            self.tree
        )

        self.tree.itemSelectionChanged.connect(
            self._on_selection_changed
        )

        self.tree.itemDoubleClicked.connect(
            self._on_item_double_clicked
        )

        self.tree.customContextMenuRequested.connect(
            self._show_context_menu
        )

        self.add_button.clicked.connect(
            self._add_entity
        )

        self.remove_button.clicked.connect(
            self._remove_selected_entity
        )

        self._update_buttons()

    def set_scene(
        self,
        resource: SceneResource | None,
    ) -> None:
        self.resource = resource

        self.refresh()

    def refresh(self) -> None:
        selected_entity = (
            self.selected_entity_id()
        )

        selected_component = (
            self.selected_component()
        )

        expanded_entities = (
            self._expanded_entity_ids()
        )

        self.tree.blockSignals(
            True
        )

        try:
            self.tree.clear()

            if self.resource is None:
                self._update_buttons()
                return

            root = QTreeWidgetItem(
                [
                    self.resource.name,
                ]
            )

            root.setData(
                0,
                Qt.ItemDataRole.UserRole,
                "__scene__",
            )

            root.setData(
                0,
                self.ROLE_NODE_TYPE,
                self.NODE_SCENE,
            )

            root.setExpanded(
                True
            )

            self.tree.addTopLevelItem(
                root
            )

            for entity in self.resource.entities:
                entity_item = (
                    self._create_entity_item(
                        entity
                    )
                )

                root.addChild(
                    entity_item
                )

                if entity.id in expanded_entities:
                    entity_item.setExpanded(
                        True
                    )

            if selected_entity is not None:
                self._restore_selection(
                    selected_entity,
                    selected_component,
                )

        finally:
            self.tree.blockSignals(
                False
            )

        self._update_buttons()

    def _create_entity_item(
        self,
        entity: SceneEntity,
    ) -> QTreeWidgetItem:
        item = QTreeWidgetItem(
            [
                entity.name,
            ]
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            entity.id,
        )

        item.setData(
            0,
            self.ROLE_NODE_TYPE,
            self.NODE_ENTITY,
        )

        self._add_components(
            item,
            entity,
        )

        return item

    def _add_components(
        self,
        parent: QTreeWidgetItem,
        entity: SceneEntity,
    ) -> None:
        if entity.sprite is not None:
            self._add_component_item(
                parent,
                entity,
                "sprite",
                "Sprite",
            )

        if entity.camera is not None:
            label = "Camera"

            if entity.camera.active:
                label += " (ativa)"

            self._add_component_item(
                parent,
                entity,
                "camera",
                label,
            )

        if entity.tilemap is not None:
            self._add_component_item(
                parent,
                entity,
                "tilemap",
                "TileMap",
            )

        if entity.collider is not None:
            label = "Collider"

            if not entity.collider.enabled:
                label += " (desativado)"

            self._add_component_item(
                parent,
                entity,
                "collider",
                label,
            )

        if entity.player_controller is not None:
            label = "Player Controller"

            if not entity.player_controller.enabled:
                label += " (desativado)"

            self._add_component_item(
                parent,
                entity,
                "player",
                label,
            )

    def _add_component_item(
        self,
        parent: QTreeWidgetItem,
        entity: SceneEntity,
        component: str,
        label: str,
    ) -> None:
        item = QTreeWidgetItem(
            [
                label,
            ]
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            entity.id,
        )

        item.setData(
            0,
            self.ROLE_NODE_TYPE,
            self.NODE_COMPONENT,
        )

        item.setData(
            0,
            self.ROLE_COMPONENT,
            component,
        )

        parent.addChild(
            item
        )

    def _expanded_entity_ids(
        self,
    ) -> set[str]:
        expanded: set[str] = set()

        root = self.tree.topLevelItem(
            0
        )

        if root is None:
            return expanded

        for index in range(
            root.childCount()
        ):
            item = root.child(
                index
            )

            if not item.isExpanded():
                continue

            value = item.data(
                0,
                Qt.ItemDataRole.UserRole,
            )

            if value:
                expanded.add(
                    str(value)
                )

        return expanded

    def selected_entity_id(
        self,
    ) -> str | None:
        items = self.tree.selectedItems()

        if not items:
            return None

        item = items[0]

        node_type = item.data(
            0,
            self.ROLE_NODE_TYPE,
        )

        if node_type not in (
            self.NODE_ENTITY,
            self.NODE_COMPONENT,
        ):
            return None

        value = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if not value:
            return None

        return str(
            value
        )

    def selected_component(
        self,
    ) -> str | None:
        items = self.tree.selectedItems()

        if not items:
            return None

        item = items[0]

        node_type = item.data(
            0,
            self.ROLE_NODE_TYPE,
        )

        if node_type != self.NODE_COMPONENT:
            return None

        value = item.data(
            0,
            self.ROLE_COMPONENT,
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
        self.tree.blockSignals(
            True
        )

        try:
            self._select_entity_internal(
                entity_id
            )

        finally:
            self.tree.blockSignals(
                False
            )

        self._update_buttons()

    def _select_entity_internal(
        self,
        entity_id: str,
    ) -> None:
        root = self.tree.topLevelItem(
            0
        )

        if root is None:
            return

        for index in range(
            root.childCount()
        ):
            item = root.child(
                index
            )

            value = item.data(
                0,
                Qt.ItemDataRole.UserRole,
            )

            if str(value) != entity_id:
                continue

            self.tree.setCurrentItem(
                item
            )

            return

    def _restore_selection(
        self,
        entity_id: str,
        component: str | None,
    ) -> None:
        root = self.tree.topLevelItem(
            0
        )

        if root is None:
            return

        for index in range(
            root.childCount()
        ):
            entity_item = root.child(
                index
            )

            value = entity_item.data(
                0,
                Qt.ItemDataRole.UserRole,
            )

            if str(value) != entity_id:
                continue

            if component is None:
                self.tree.setCurrentItem(
                    entity_item
                )
                return

            for child_index in range(
                entity_item.childCount()
            ):
                component_item = (
                    entity_item.child(
                        child_index
                    )
                )

                component_value = (
                    component_item.data(
                        0,
                        self.ROLE_COMPONENT,
                    )
                )

                if (
                    str(component_value)
                    != component
                ):
                    continue

                entity_item.setExpanded(
                    True
                )

                self.tree.setCurrentItem(
                    component_item
                )

                return

            self.tree.setCurrentItem(
                entity_item
            )

            return

    def _on_selection_changed(
        self,
    ) -> None:
        self._update_buttons()

        items = self.tree.selectedItems()

        if not items:
            return

        item = items[0]

        node_type = item.data(
            0,
            self.ROLE_NODE_TYPE,
        )

        entity_id = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if not entity_id:
            return

        if node_type == self.NODE_ENTITY:
            self.entity_selected.emit(
                str(entity_id)
            )

            return

        if node_type != self.NODE_COMPONENT:
            return

        component = item.data(
            0,
            self.ROLE_COMPONENT,
        )

        if not component:
            return

        self.component_selected.emit(
            str(entity_id),
            str(component),
        )

    def _on_item_double_clicked(
        self,
        item: QTreeWidgetItem,
        column: int,
    ) -> None:
        del column

        node_type = item.data(
            0,
            self.ROLE_NODE_TYPE,
        )

        if node_type != self.NODE_ENTITY:
            return

        value = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if not value:
            return

        self._rename_entity(
            str(value)
        )

    def _show_context_menu(
        self,
        position,
    ) -> None:
        item = self.tree.itemAt(
            position
        )

        if item is None:
            return

        node_type = item.data(
            0,
            self.ROLE_NODE_TYPE,
        )

        if node_type == self.NODE_SCENE:
            menu = QMenu(
                self
            )

            add_action = menu.addAction(
                "Adicionar Entidade"
            )

            selected_action = menu.exec(
                self.tree.viewport().mapToGlobal(
                    position
                )
            )

            if selected_action is add_action:
                self._add_entity()

            return

        if node_type != self.NODE_ENTITY:
            return

        value = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if not value:
            return

        menu = QMenu(
            self
        )

        rename_action = menu.addAction(
            "Renomear"
        )

        remove_action = menu.addAction(
            "Remover"
        )

        selected_action = menu.exec(
            self.tree.viewport().mapToGlobal(
                position
            )
        )

        entity_id = str(
            value
        )

        if selected_action is rename_action:
            self._rename_entity(
                entity_id
            )

        elif selected_action is remove_action:
            self._remove_entity(
                entity_id
            )

    def _add_entity(self) -> None:
        if self.resource is None:
            return

        name, accepted = (
            QInputDialog.getText(
                self,
                "Nova Entidade",
                "Nome:",
                text="Entity",
            )
        )

        if not accepted:
            return

        name = name.strip()

        if not name:
            return

        entity = SceneEntity(
            name=name
        )

        self.resource.add_entity(
            entity
        )

        self.refresh()

        self.select_entity(
            entity.id
        )

        self.scene_changed.emit()

    def _remove_selected_entity(
        self,
    ) -> None:
        entity_id = (
            self.selected_entity_id()
        )

        if entity_id is None:
            return

        self._remove_entity(
            entity_id
        )

    def _remove_entity(
        self,
        entity_id: str,
    ) -> None:
        if self.resource is None:
            return

        removed = (
            self.resource.remove_entity(
                entity_id
            )
        )

        if not removed:
            return

        self.refresh()

        self.scene_changed.emit()

    def _rename_entity(
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

        name, accepted = (
            QInputDialog.getText(
                self,
                "Renomear Entidade",
                "Nome:",
                text=entity.name,
            )
        )

        if not accepted:
            return

        name = name.strip()

        if not name:
            return

        entity.name = name

        self.refresh()

        self.select_entity(
            entity.id
        )

        self.scene_changed.emit()

    def _update_buttons(self) -> None:
        has_scene = (
            self.resource is not None
        )

        items = self.tree.selectedItems()

        selected_entity_node = False

        if items:
            node_type = items[0].data(
                0,
                self.ROLE_NODE_TYPE,
            )

            selected_entity_node = (
                node_type
                == self.NODE_ENTITY
            )

        self.add_button.setEnabled(
            has_scene
        )

        self.remove_button.setEnabled(
            selected_entity_node
        )