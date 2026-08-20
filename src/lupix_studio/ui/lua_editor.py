from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LuaEditor(QWidget):
    """Editor Lua simples integrado ao Lupix Studio."""

    back_requested = Signal()
    saved = Signal(Path)

    def __init__(self) -> None:
        super().__init__()

        self.current_path: Path | None = None

        self.title_label = QLabel("Editor Lua")
        self.title_label.setStyleSheet(
            "font-size: 16px; font-weight: 600;"
        )

        self.path_label = QLabel()
        self.path_label.setWordWrap(True)

        self.editor = QPlainTextEdit()

        fixed_font = QFontDatabase.systemFont(
            QFontDatabase.SystemFont.FixedFont
        )
        self.editor.setFont(fixed_font)

        self.save_button = QPushButton("Salvar")
        self.back_button = QPushButton("Voltar")

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.back_button)
        buttons.addWidget(self.save_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)
        layout.addWidget(self.title_label)
        layout.addWidget(self.path_label)
        layout.addWidget(self.editor, 1)
        layout.addLayout(buttons)

        self.save_button.clicked.connect(self.save)
        self.back_button.clicked.connect(
            self.back_requested.emit
        )

    def open_file(self, path: Path) -> bool:
        path = Path(path).resolve()

        try:
            content = path.read_text(
                encoding="utf-8"
            )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Erro ao abrir script",
                str(error),
            )
            return False

        self.current_path = path
        self.title_label.setText(
            f"Editor Lua — {path.name}"
        )
        self.path_label.setText(str(path))
        self.editor.setPlainText(content)
        self.editor.document().setModified(False)
        self.editor.setFocus()
        return True

    def save(self) -> bool:
        if self.current_path is None:
            return False

        try:
            self.current_path.write_text(
                self.editor.toPlainText(),
                encoding="utf-8",
            )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Erro ao salvar script",
                str(error),
            )
            return False

        self.editor.document().setModified(False)
        self.saved.emit(self.current_path)
        return True
