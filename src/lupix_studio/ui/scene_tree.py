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
    scene_changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.resource: SceneResource | None = None

        self.tree = QTreeWidget()

        self.tree.setHeaderLabels(
            [
                "Entidade",
                "Componentes",
            ]
        )

        self.tree.setColumnWidth(
    0,
    130,
)

        self.tree.setAlternatingRowColors(
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
        selected_id = (
            self.selected_entity_id()
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
                    "",
                ]
            )

            root.setData(
                0,
                Qt.ItemDataRole.UserRole,
                "__scene__",
            )

            root.setExpanded(
                True
            )

            self.tree.addTopLevelItem(
                root
            )

            for entity in self.resource.entities:
                item = self._create_entity_item(
                    entity
                )

                root.addChild(
                    item
                )

            if selected_id is not None:
                self._select_entity_internal(
                    selected_id
                )

            self.tree.expandAll()

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
                self._component_text(
                    entity
                ),
            ]
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            entity.id,
        )

        tooltip = self._component_tooltip(
            entity
        )

        item.setToolTip(
            1,
            tooltip,
        )

        return item

    def _component_text(
        self,
        entity: SceneEntity,
    ) -> str:
        symbols: list[str] = []

        if entity.sprite is not None:
            symbols.append("🎨")

        if entity.camera is not None:
            symbols.append("📷")

        if entity.tilemap is not None:
            symbols.append("▦")

        if entity.collider is not None:
            symbols.append("◇")

        if entity.player_controller is not None:
            symbols.append("▶")

        if not symbols:
            return "—"

        return "  ".join(symbols)

    def _component_tooltip(
        self,
        entity: SceneEntity,
    ) -> str:
        components: list[str] = []

        if entity.sprite is not None:
            components.append(
                "Sprite"
            )

        if entity.camera is not None:
            camera_text = "Camera"

            if entity.camera.active:
                camera_text += " (ativa)"

            components.append(
                camera_text
            )

        if entity.tilemap is not None:
            components.append(
                "TileMap"
            )

        if entity.collider is not None:
            collider_text = "Collider"

            if not entity.collider.enabled:
                collider_text += " (desativado)"

            components.append(
                collider_text
            )

        if entity.player_controller is not None:
            player_text = (
                "Player Controller"
            )

            if not entity.player_controller.enabled:
                player_text += " (desativado)"

            components.append(
                player_text
            )

        if not components:
            return "Nenhum componente"

        return "\n".join(
            components
        )

    def selected_entity_id(
        self,
    ) -> str | None:
        items = (
            self.tree.selectedItems()
        )

        if not items:
            return None

        value = items[0].data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if (
            not value
            or value == "__scene__"
        ):
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

    def _on_selection_changed(
        self,
    ) -> None:
        entity_id = (
            self.selected_entity_id()
        )

        self._update_buttons()

        if entity_id is None:
            return

        self.entity_selected.emit(
            entity_id
        )

    def _on_item_double_clicked(
        self,
        item: QTreeWidgetItem,
        column: int,
    ) -> None:
        del column

        value = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if (
            not value
            or value == "__scene__"
        ):
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

        value = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if not value:
            return

        menu = QMenu(
            self
        )

        if value == "__scene__":
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

        has_entity = (
            self.selected_entity_id()
            is not None
        )

        self.add_button.setEnabled(
            has_scene
        )

        self.remove_button.setEnabled(
            has_entity
        )