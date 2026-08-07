DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1f22;
}

QWidget {
    background-color: #1e1f22;
    color: #e6e6e6;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QMenuBar {
    background-color: #25262a;
    color: #e6e6e6;
    border-bottom: 1px solid #35363b;
    padding: 2px;
}

QMenuBar::item {
    padding: 6px 10px;
    background: transparent;
}

QMenuBar::item:selected {
    background-color: #35363b;
}

QMenu {
    background-color: #25262a;
    color: #e6e6e6;
    border: 1px solid #3a3b40;
}

QMenu::item {
    padding: 6px 24px 6px 10px;
}

QMenu::item:selected {
    background-color: #3a3b40;
}

QDockWidget {
    color: #e6e6e6;
}

QDockWidget::title {
    background-color: #292a2f;
    border-bottom: 1px solid #3a3b40;
    padding: 7px;
    text-align: left;
}

QTreeWidget {
    background-color: #232429;
    border: none;
    outline: none;
}

QTreeWidget::item {
    padding: 5px;
}

QTreeWidget::item:selected {
    background-color: #3a506b;
}

QTreeWidget::item:hover {
    background-color: #303238;
}

QTabWidget::pane {
    border: none;
}

QTabBar::tab {
    background-color: #292a2f;
    padding: 7px 14px;
    border-right: 1px solid #35363b;
}

QTabBar::tab:selected {
    background-color: #34363c;
}

QTextEdit {
    background-color: #1c1d20;
    color: #d8d8d8;
    border: none;
}

QStatusBar {
    background-color: #25262a;
    color: #bfc1c5;
    border-top: 1px solid #35363b;
}

QLabel#ViewportTitle {
    color: #8f939b;
    font-size: 14pt;
    font-weight: 600;
}

QLabel#StartTitle {
    font-size: 28pt;
    font-weight: 700;
    color: #f2f2f2;
}

QLabel#StartSubtitle {
    font-size: 12pt;
    color: #9da1a8;
}

QLabel#SectionTitle {
    font-size: 11pt;
    font-weight: 600;
    margin-top: 10px;
}

QLabel#MutedLabel {
    color: #777b83;
}

QPushButton {
    background-color: #2d2f34;
    color: #e6e6e6;
    border: 1px solid #3b3d43;
    border-radius: 5px;
    padding: 9px 14px;
}

QPushButton:hover {
    background-color: #383b41;
}

QPushButton:pressed {
    background-color: #24262a;
}

QPushButton#PrimaryButton {
    background-color: #3b5f8a;
    border: 1px solid #4b74a4;
}

QPushButton#PrimaryButton:hover {
    background-color: #466d9d;
}
"""