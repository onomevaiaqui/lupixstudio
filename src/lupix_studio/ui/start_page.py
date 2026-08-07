from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class StartPage(QWidget):
    """Tela inicial do Lupix Studio."""

    new_project_requested = Signal()
    open_project_requested = Signal()

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
        new_project_button.clicked.connect(self.new_project_requested.emit)

        open_project_button = QPushButton("Abrir Projeto")
        open_project_button.clicked.connect(self.open_project_requested.emit)

        recent_label = QLabel("Projetos Recentes")
        recent_label.setObjectName("SectionTitle")

        empty_recent = QLabel("Nenhum projeto recente")
        empty_recent.setObjectName("MutedLabel")

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
        layout.addWidget(empty_recent)
        layout.addStretch()