import json
from pathlib import Path

from lupix_studio.core.paths import ensure_directories, user_data_dir

RECENT_PROJECTS_FILE = "recent_projects.json"


def recent_projects_file() -> Path:
    return user_data_dir() / RECENT_PROJECTS_FILE


class RecentProjectsManager:
    """Gerencia a lista de projetos recentes."""

    def __init__(self, limit: int = 10) -> None:
        self.limit = limit

    def load(self) -> list[Path]:
        ensure_directories()
        path = recent_projects_file()

        if not path.exists():
            return []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(data, list):
            return []

        projects: list[Path] = []

        for item in data:
            project_path = Path(str(item))

            if (project_path / "lupix.project").exists():
                projects.append(project_path)

        return projects[: self.limit]

    def save(self, projects: list[Path]) -> None:
        ensure_directories()

        normalized = [
            str(project.resolve())
            for project in projects[: self.limit]
        ]

        recent_projects_file().write_text(
            json.dumps(normalized, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, project: Path) -> list[Path]:
        project = project.resolve()

        projects = [
            item
            for item in self.load()
            if item.resolve() != project
        ]

        projects.insert(0, project)
        projects = projects[: self.limit]

        self.save(projects)

        return projects