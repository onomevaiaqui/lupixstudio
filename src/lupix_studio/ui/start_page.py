from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class StartPage(QWidget):
    """Tela inicial do Lupix Studio."""

    new_project_requested = Signal()
    open_project_requested = Signal()
    recent_project_requested = Signal(Path)

    def __init__(self) -> None:
        super().__init__()

        title = QLabel("LUPIX STUDIO")
        title.setObjectName("StartTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Crie jogos para o console Lupi")
        subtitle.setObjectName("StartSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        new_project_button = QPushButton("Novo Projeto")
        new_project_button.setObjectName("PrimaryButton")
        new_project_button.clicked.connect(
            self.new_project_requested.emit
        )

        open_project_button = QPushButton("Abrir Projeto")
        open_project_button.clicked.connect(
            self.open_project_requested.emit
        )

        recent_label = QLabel("Projetos Recentes")
        recent_label.setObjectName("SectionTitle")

        self.recent_list = QListWidget()
        self.recent_list.setMinimumHeight(120)
        self.recent_list.itemDoubleClicked.connect(
            self._on_recent_double_clicked
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(120, 70, 120, 70)
        layout.setSpacing(14)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(24)
        layout.addWidget(new_project_button)
        layout.addWidget(open_project_button)
        layout.addSpacing(32)
        layout.addWidget(recent_label)
        layout.addWidget(self.recent_list)
        layout.addStretch()

    def set_recent_projects(
        self,
        projects: list[Path],
    ) -> None:
        self.recent_list.clear()

        if not projects:
            item = QListWidgetItem("Nenhum projeto recente")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.recent_list.addItem(item)
            return

        for project in projects:
            item = QListWidgetItem(project.name)
            item.setToolTip(str(project))
            item.setData(
                Qt.ItemDataRole.UserRole,
                str(project),
            )

            self.recent_list.addItem(item)

    def _on_recent_double_clicked(
        self,
        item: QListWidgetItem,
    ) -> None:
        value = item.data(Qt.ItemDataRole.UserRole)

        if not value:
            return

        self.recent_project_requested.emit(
            Path(str(value))
        )