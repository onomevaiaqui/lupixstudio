from PySide6.QtWidgets import QStackedWidget, QWidget

from lupix_studio.ui.start_page import StartPage


class WorkspaceWidget(QWidget):
    """Área central da IDE."""

    def __init__(self) -> None:
        super().__init__()

        self.stack = QStackedWidget(self)

        self.start_page = StartPage()
        self.stack.addWidget(self.start_page)

        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)