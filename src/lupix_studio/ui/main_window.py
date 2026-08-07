from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from lupix_studio.ui.workspace import WorkspaceWidget


class MainWindow(QMainWindow):
    """Janela principal do Lupix Studio."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Lupix Studio")
        self.resize(1440, 900)

        self._create_menu()
        self._create_workspace()
        self._create_project_dock()
        self._create_inspector_dock()
        self._create_bottom_dock()
        self._create_status_bar()

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        edit_menu = self.menuBar().addMenu("Editar")
        project_menu = self.menuBar().addMenu("Projeto")
        help_menu = self.menuBar().addMenu("Ajuda")

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu.addAction(QAction("Desfazer", self))
        edit_menu.addAction(QAction("Refazer", self))

        project_menu.addAction(QAction("Executar", self))
        project_menu.addAction(QAction("Exportar", self))

        help_menu.addAction(QAction("Sobre", self))

    def _create_workspace(self) -> None:
        self.workspace = WorkspaceWidget()
        self.setCentralWidget(self.workspace)

    def _create_project_dock(self) -> None:
        dock = QDockWidget("Projeto", self)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        tree = QTreeWidget()
        tree.setHeaderHidden(True)

        root = QTreeWidgetItem(["Projeto"])
        root.addChild(QTreeWidgetItem(["Cenas"]))
        root.addChild(QTreeWidgetItem(["Sprites"]))
        root.addChild(QTreeWidgetItem(["TileSets"]))
        root.addChild(QTreeWidgetItem(["Mapas"]))
        root.addChild(QTreeWidgetItem(["Scripts"]))
        root.addChild(QTreeWidgetItem(["Áudio"]))

        tree.addTopLevelItem(root)
        root.setExpanded(True)

        dock.setWidget(tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _create_inspector_dock(self) -> None:
        dock = QDockWidget("Inspector", self)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Nenhum objeto selecionado")
        title.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(title)
        layout.addStretch()

        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _create_bottom_dock(self) -> None:
        dock = QDockWidget("Saída", self)

        tabs = QTabWidget()

        console = QTextEdit()
        console.setReadOnly(True)
        console.setPlainText("Lupix Studio pronto.")

        problems = QTextEdit()
        problems.setReadOnly(True)

        tabs.addTab(console, "Console")
        tabs.addTab(problems, "Problemas")

        dock.setWidget(tabs)

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    def _create_status_bar(self) -> None:
        status = QStatusBar()
        status.showMessage("Pronto")
        self.setStatusBar(status)