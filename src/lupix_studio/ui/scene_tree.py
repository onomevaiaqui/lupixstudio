from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.scene.model import SceneEntity, SceneResource


class SceneTree(QWidget):
    """Lista e gerencia as entidades da cena aberta."""

    entity_selected = Signal(str)
    scene_changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.resource: SceneResource | None = None

        self.entity_list = QListWidget()

        self.add_button = QPushButton("Adicionar Objeto")
        self.rename_button = QPushButton("Renomear")
        self.remove_button = QPushButton("Excluir")

        buttons = QHBoxLayout()
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.rename_button)
        buttons.addWidget(self.remove_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self.entity_list)
        layout.addLayout(buttons)

        self.add_button.clicked.connect(
            self._add_entity
        )

        self.rename_button.clicked.connect(
            self._rename_entity
        )

        self.remove_button.clicked.connect(
            self._remove_entity
        )

        self.entity_list.itemSelectionChanged.connect(
            self._emit_selected_entity
        )

    def set_scene(
        self,
        resource: SceneResource | None,
    ) -> None:
        self.resource = resource
        self.refresh()

    def refresh(self) -> None:
        selected_id = self.selected_entity_id()

        self.entity_list.blockSignals(True)

        try:
            self.entity_list.clear()

            if self.resource is None:
                return

            for entity in self.resource.entities:
                item = QListWidgetItem(
                    entity.name
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    entity.id,
                )

                self.entity_list.addItem(
                    item
                )

        finally:
            self.entity_list.blockSignals(False)

        if selected_id is not None:
            self.select_entity(
                selected_id
            )

    def selected_entity_id(
        self,
    ) -> str | None:
        item = self.entity_list.currentItem()

        if item is None:
            return None

        value = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not value:
            return None

        return str(value)

    def select_entity(
        self,
        entity_id: str,
    ) -> None:
        self.entity_list.blockSignals(True)

        try:
            for row in range(
                self.entity_list.count()
            ):
                item = self.entity_list.item(
                    row
                )

                value = item.data(
                    Qt.ItemDataRole.UserRole
                )

                if str(value) == entity_id:
                    self.entity_list.setCurrentRow(
                        row
                    )
                    return

        finally:
            self.entity_list.blockSignals(False)

    def _add_entity(self) -> None:
        if self.resource is None:
            return

        number = 1

        existing_names = {
            entity.name
            for entity in self.resource.entities
        }

        while f"Objeto{number}" in existing_names:
            number += 1

        entity = SceneEntity(
            name=f"Objeto{number}",
            kind="empty",
        )

        self.resource.add_entity(
            entity
        )

        self.refresh()

        self.select_entity(
            entity.id
        )

        self.entity_selected.emit(
            entity.id
        )

        self.scene_changed.emit()

    def _rename_entity(self) -> None:
        if self.resource is None:
            return

        entity_id = self.selected_entity_id()

        if entity_id is None:
            return

        entity = self.resource.entity(
            entity_id
        )

        if entity is None:
            return

        name, accepted = QInputDialog.getText(
            self,
            "Renomear Objeto",
            "Nome:",
            text=entity.name,
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

        self.entity_selected.emit(
            entity.id
        )

        self.scene_changed.emit()

    def _remove_entity(self) -> None:
        if self.resource is None:
            return

        entity_id = self.selected_entity_id()

        if entity_id is None:
            return

        if not self.resource.remove_entity(
            entity_id
        ):
            return

        self.refresh()
        self.scene_changed.emit()

    def _emit_selected_entity(
        self,
    ) -> None:
        entity_id = self.selected_entity_id()

        if entity_id is None:
            return

        self.entity_selected.emit(
            entity_id
        )