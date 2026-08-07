from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Janela principal do Lupix Studio."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Lupix Studio")
        self.resize(1280, 720)

        title = QLabel("LUPIX STUDIO")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Desenvolvimento de jogos para o Lupi")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)