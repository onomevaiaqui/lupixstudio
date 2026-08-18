import shutil
from pathlib import Path

path = Path(r'.\src\lupix_studio\ui\main_window.py')

if not path.exists():
    raise SystemExit(f'Arquivo não encontrado: {path.resolve()}')

backup = path.with_suffix(path.suffix + '.bak_start_screen')
if not backup.exists():
    shutil.copy2(path, backup)

text = path.read_text(encoding='utf-8')

if 'import shutil\n' not in text:
    text = text.replace(
        'from pathlib import Path\n',
        'from pathlib import Path\nimport shutil\n',
        1,
    )

anchor = (
    '        self.workspace.start_page.recent_project_requested.connect(\n'
    '            self._on_recent_project\n'
    '        )\n'
)

replacement = anchor + (
    '\n        self.workspace.start_page.delete_project_requested.connect(\n'
    '            self._on_delete_project\n'
    '        )\n'
)

if (
    anchor in text
    and 'delete_project_requested.connect' not in text
):
    text = text.replace(anchor, replacement, 1)

text = text.replace(
    '"Abrir Projeto Lupix",',
    '"Importar Projeto Lupix",',
)

if 'def _on_delete_project(' not in text:
    anchor = '    def _on_recent_project(\n'
    method = '''    def _on_delete_project(
        self,
        path: Path,
    ) -> None:
        project_path = Path(path).resolve()

        if not project_path.exists():
            QMessageBox.warning(
                self,
                "Excluir Projeto",
                "O projeto selecionado não existe mais.",
            )
            self._refresh_recent_projects()
            return

        answer = QMessageBox.question(
            self,
            "Excluir Projeto",
            (
                "Deseja excluir permanentemente o projeto?\\n\\n"
                f"{project_path}\\n\\n"
                "Esta ação remove toda a pasta do projeto "
                "e não pode ser desfeita."
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        if (
            self.current_project is not None
            and self.current_project.root.resolve()
            == project_path
        ):
            QMessageBox.warning(
                self,
                "Excluir Projeto",
                (
                    "Este projeto está aberto. "
                    "Abra outro projeto antes de excluí-lo."
                ),
            )
            return

        try:
            shutil.rmtree(project_path)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Erro ao excluir projeto",
                str(error),
            )
            return

        self._refresh_recent_projects()

        self.statusBar().showMessage(
            f"Projeto excluído: {project_path.name}"
        )

    def _on_recent_project(
'''

    if anchor not in text:
        raise RuntimeError(
            'Método _on_recent_project não encontrado.'
        )

    text = text.replace(anchor, method, 1)

path.write_text(text, encoding='utf-8')

print('main_window.py atualizado.')
print(f'Backup: {backup}')