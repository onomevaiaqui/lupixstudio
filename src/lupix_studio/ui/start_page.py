from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ProjectRow(QWidget):
    open_requested = Signal(Path)

    def __init__(
        self,
        project_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.project_path = Path(project_path)
        self.setObjectName("ProjectRow")

        folder_icon = QLabel()
        folder_icon.setFixedSize(42, 42)
        folder_icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        folder_path = self._resource(
            "icon_folder.png"
        )

        if folder_path.exists():
            pixmap = QPixmap(str(folder_path))
            folder_icon.setPixmap(
                pixmap.scaled(
                    28,
                    28,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        name_label = QLabel(
            self.project_path.name
        )
        name_label.setObjectName("ProjectName")

        path_label = QLabel(
            str(self.project_path)
        )
        path_label.setObjectName("ProjectPath")
        path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.addWidget(name_label)
        text_layout.addWidget(path_label)

        open_button = QPushButton()
        open_button.setObjectName(
            "ProjectOpenButton"
        )
        open_button.setToolTip(
            "Abrir projeto"
        )
        open_button.setFixedSize(50, 44)

        play_path = self._resource(
            "icon_play.png"
        )

        if play_path.exists():
            open_button.setIcon(
                QIcon(str(play_path))
            )
            open_button.setIconSize(
                QSize(22, 22)
            )
        else:
            open_button.setText("▶")

        open_button.clicked.connect(
            lambda: self.open_requested.emit(
                self.project_path
            )
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            16,
            7,
            12,
            7,
        )
        layout.setSpacing(12)
        layout.addWidget(folder_icon)
        layout.addLayout(text_layout, 1)
        layout.addWidget(open_button)

    @staticmethod
    def _resource(
        name: str,
    ) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "resources"
            / name
        )


class StartPage(QWidget):
    new_project_requested = Signal()
    open_project_requested = Signal()
    recent_project_requested = Signal(Path)
    delete_project_requested = Signal(Path)

    def __init__(self) -> None:
        super().__init__()

        self._projects: list[Path] = []

        self.setObjectName("StartPage")
        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.background_pixmap = QPixmap(
            str(
                self._resource(
                    "start_background.png"
                )
            )
        )

        self._build_ui()
        self._apply_style()

    def _resource(
        self,
        name: str,
    ) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "resources"
            / name
        )

    def paintEvent(
        self,
        event,
    ) -> None:
        painter = QPainter(self)

        if not self.background_pixmap.isNull():
            scaled = self.background_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

            x = (
                self.width()
                - scaled.width()
            ) // 2

            y = (
                self.height()
                - scaled.height()
            ) // 2

            painter.drawPixmap(
                x,
                y,
                scaled,
            )
        else:
            painter.fillRect(
                self.rect(),
                QColor("#081427"),
            )

        painter.end()

        super().paintEvent(event)

    def _build_ui(self) -> None:
        page = QVBoxLayout(self)

        page.setContentsMargins(
            30,
            18,
            30,
            18,
        )

        page.setSpacing(0)

        page.addStretch(1)

        # ----------------------------------------------------------
        # Logo
        # ----------------------------------------------------------
        logo_row = QHBoxLayout()
        logo_row.addStretch()

        logo = QLabel()
        logo.setObjectName("LogoImage")
        logo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        logo.setFixedSize(
            390,
            210,
        )

        logo_path = self._resource(
            "lupix_logo.png"
        )

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))

            if not pixmap.isNull():
                logo.setPixmap(
                    pixmap.scaled(
                        380,
                        205,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )

        logo_row.addWidget(logo)
        logo_row.addStretch()

        page.addLayout(logo_row)
        page.addSpacing(16)

        # ----------------------------------------------------------
        # Central column - no container widget, no opaque rectangle.
        # ----------------------------------------------------------
        actions_row = QHBoxLayout()
        actions_row.addStretch(1)

        actions = QHBoxLayout()
        actions.setSpacing(14)

        self.new_button = self._action_button(
            "icon_new.png",
            "Novo Projeto",
        )

        self.import_button = self._action_button(
            "icon_import.png",
            "Importar Projeto",
        )

        self.delete_button = self._action_button(
            "icon_delete.png",
            "Excluir Projeto",
        )

        self.settings_button = self._action_button(
            "icon_settings.png",
            "Configurações",
        )

        for button in (
            self.new_button,
            self.import_button,
            self.delete_button,
            self.settings_button,
        ):
            actions.addWidget(button)

        actions_row.addLayout(actions)
        actions_row.addStretch(1)

        page.addLayout(actions_row)
        page.addSpacing(18)

        # ----------------------------------------------------------
        # Header
        # ----------------------------------------------------------
        header_row = QHBoxLayout()
        header_row.addStretch(1)

        header = QHBoxLayout()
        header.setSpacing(10)

        folder_icon = QLabel()
        folder_icon.setFixedSize(
            28,
            28,
        )

        folder_path = self._resource(
            "icon_folder.png"
        )

        if folder_path.exists():
            pixmap = QPixmap(
                str(folder_path)
            )

            folder_icon.setPixmap(
                pixmap.scaled(
                    24,
                    24,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        title = QLabel(
            "Projetos Recentes"
        )
        title.setObjectName(
            "ProjectsTitle"
        )

        self.search_wrapper = QFrame()
        self.search_wrapper.setObjectName(
            "SearchWrapper"
        )
        self.search_wrapper.setFixedWidth(
            360
        )

        search_layout = QHBoxLayout(
            self.search_wrapper
        )

        search_layout.setContentsMargins(
            12,
            0,
            8,
            0,
        )

        search_layout.setSpacing(
            8
        )

        search_icon = QLabel()
        search_icon.setFixedSize(
            22,
            22,
        )

        search_path = self._resource(
            "icon_search.png"
        )

        if search_path.exists():
            pixmap = QPixmap(
                str(search_path)
            )

            search_icon.setPixmap(
                pixmap.scaled(
                    19,
                    19,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName(
            "ProjectSearch"
        )
        self.search_edit.setPlaceholderText(
            "Buscar projetos..."
        )
        self.search_edit.setClearButtonEnabled(
            True
        )

        search_layout.addWidget(
            search_icon
        )
        search_layout.addWidget(
            self.search_edit
        )

        header.addWidget(folder_icon)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(
            self.search_wrapper
        )

        header_wrapper = QWidget()
        header_wrapper.setObjectName(
            "TransparentWidget"
        )
        header_wrapper.setFixedWidth(
            980
        )
        header_wrapper.setLayout(
            header
        )

        header_row.addWidget(
            header_wrapper
        )
        header_row.addStretch(1)

        page.addLayout(
            header_row
        )
        page.addSpacing(10)

        # ----------------------------------------------------------
        # Projects list
        # ----------------------------------------------------------
        list_row = QHBoxLayout()
        list_row.addStretch(1)

        self.project_list = QListWidget()
        self.project_list.setObjectName(
            "ProjectList"
        )
        self.project_list.setFixedWidth(
            980
        )
        self.project_list.setMinimumHeight(
            300
        )
        self.project_list.setMaximumHeight(
            380
        )
        self.project_list.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        self.project_list.setSpacing(0)

        self.project_list.itemDoubleClicked.connect(
            self._open_selected_item
        )

        list_row.addWidget(
            self.project_list
        )

        list_row.addStretch(1)

        page.addLayout(
            list_row
        )

        page.addSpacing(12)

        footer = QLabel(
            "Lupix Studio  —  Crie. Teste. Jogue."
        )
        footer.setObjectName(
            "FooterLabel"
        )
        footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        page.addWidget(
            footer
        )

        page.addStretch(1)

        self.new_button.clicked.connect(
            self.new_project_requested.emit
        )

        self.import_button.clicked.connect(
            self.open_project_requested.emit
        )

        self.delete_button.clicked.connect(
            self._request_delete_selected
        )

        self.settings_button.clicked.connect(
            self._show_settings_placeholder
        )

    def _action_button(
        self,
        icon_name: str,
        text: str,
    ) -> QPushButton:
        button = QPushButton(
            text
        )

        button.setObjectName(
            "ActionButton"
        )

        button.setFixedSize(
            232,
            105,
        )

        button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        icon_path = self._resource(
            icon_name
        )

        if icon_path.exists():
            button.setIcon(
                QIcon(str(icon_path))
            )

            button.setIconSize(
                QSize(34, 34)
            )

        return button

    def set_recent_projects(
        self,
        projects: list[Path],
    ) -> None:
        self._projects = [
            Path(project)
            for project in projects
        ]

        self._rebuild_project_list(
            self._projects
        )

    def _rebuild_project_list(
        self,
        projects: list[Path],
    ) -> None:
        self.project_list.clear()

        if not projects:
            item = QListWidgetItem(
                "Nenhum projeto encontrado."
            )

            item.setFlags(
                Qt.ItemFlag.NoItemFlags
            )

            item.setSizeHint(
                QSize(0, 64)
            )

            self.project_list.addItem(
                item
            )

            return

        for project_path in projects:
            item = QListWidgetItem()

            item.setData(
                Qt.ItemDataRole.UserRole,
                str(project_path),
            )

            item.setSizeHint(
                QSize(0, 66)
            )

            row = ProjectRow(
                project_path
            )

            row.open_requested.connect(
                self.recent_project_requested.emit
            )

            self.project_list.addItem(
                item
            )

            self.project_list.setItemWidget(
                item,
                row,
            )

    def _filter_projects(
        self,
        text: str,
    ) -> None:
        query = text.strip().lower()

        if not query:
            self._rebuild_project_list(
                self._projects
            )
            return

        filtered = [
            project
            for project in self._projects
            if (
                query
                in project.name.lower()
                or query
                in str(project).lower()
            )
        ]

        self._rebuild_project_list(
            filtered
        )

    def _selected_project(
        self,
    ) -> Path | None:
        item = self.project_list.currentItem()

        if item is None:
            return None

        value = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not value:
            return None

        return Path(
            str(value)
        )

    def _open_selected_item(
        self,
        item: QListWidgetItem,
    ) -> None:
        value = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not value:
            return

        self.recent_project_requested.emit(
            Path(str(value))
        )

    def _request_delete_selected(
        self,
    ) -> None:
        project = self._selected_project()

        if project is None:
            QMessageBox.information(
                self,
                "Excluir Projeto",
                (
                    "Selecione um projeto na lista "
                    "antes de excluir."
                ),
            )
            return

        self.delete_project_requested.emit(
            project
        )

    def _show_settings_placeholder(
        self,
    ) -> None:
        QMessageBox.information(
            self,
            "Configurações",
            (
                "O painel de configurações será "
                "adicionado em uma próxima etapa."
            ),
        )

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget#StartPage {
                background: transparent;
                color: #f5f7fb;
            }

            QWidget#TransparentWidget,
            QLabel,
            QFrame {
                background: transparent;
            }

            QPushButton#ActionButton {
                color: #ffffff;
                background-color: rgba(7, 24, 49, 222);
                border: 1px solid #385477;
                border-radius: 13px;
                padding: 12px 16px;
                font-size: 16px;
                font-weight: 700;
                text-align: left;
            }

            QPushButton#ActionButton:hover {
                border: 2px solid #ffc928;
                background-color: rgba(16, 46, 79, 235);
            }

            QLabel#ProjectsTitle {
                color: #ffffff;
                font-size: 21px;
                font-weight: 700;
            }

            QFrame#SearchWrapper {
                min-height: 42px;
                max-height: 42px;
                border: 1px solid #385477;
                border-radius: 10px;
                background-color: rgba(4, 18, 39, 220);
            }

            QLineEdit#ProjectSearch {
                min-height: 34px;
                border: none;
                color: #dce6f7;
                background: transparent;
                font-size: 14px;
            }

            QListWidget#ProjectList {
                border: 1px solid #385477;
                border-radius: 12px;
                padding: 8px;
                outline: none;
                background-color: rgba(4, 18, 39, 205);
            }

            QListWidget#ProjectList::item {
                border: none;
                border-bottom: 1px solid rgba(61, 86, 119, 145);
                background: transparent;
            }

            QListWidget#ProjectList::item:selected {
                background-color: rgba(18, 46, 78, 210);
                border-radius: 8px;
            }

            QWidget#ProjectRow {
                background: transparent;
            }

            QLabel#ProjectName {
                color: #ffffff;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#ProjectPath {
                color: #aebbd0;
                font-size: 12px;
            }

            QPushButton#ProjectOpenButton {
                background-color: rgba(8, 29, 54, 225);
                border: 1px solid #385477;
                border-radius: 9px;
            }

            QPushButton#ProjectOpenButton:hover {
                border: 1px solid #ffc928;
                background-color: rgba(22, 52, 86, 235);
            }

            QLabel#FooterLabel {
                color: #b9c4d6;
                font-size: 13px;
                padding: 0;
            }
            """
        )
