from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WorkspaceWidget(QWidget):
    """Área central da IDE."""

    def __init__(self) -> None:
        super().__init__()

        label = QLabel("Viewport")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(label)