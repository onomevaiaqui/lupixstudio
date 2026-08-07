from pathlib import Path

from lupix_studio.settings.recent_projects import RecentProjectsManager


def test_recent_projects_adds_new_project(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = tmp_path / "MeuJogo"
    project.mkdir()
    (project / "lupix.project").write_text(
        "{}",
        encoding="utf-8",
    )

    manager = RecentProjectsManager(limit=5)

    monkeypatch.setattr(
        "lupix_studio.settings.recent_projects.recent_projects_file",
        lambda: tmp_path / "recent_projects.json",
    )

    projects = manager.add(project)

    assert projects[0] == project.resolve()


def test_recent_projects_removes_duplicates(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = tmp_path / "MeuJogo"
    project.mkdir()
    (project / "lupix.project").write_text(
        "{}",
        encoding="utf-8",
    )

    manager = RecentProjectsManager(limit=5)

    monkeypatch.setattr(
        "lupix_studio.settings.recent_projects.recent_projects_file",
        lambda: tmp_path / "recent_projects.json",
    )

    manager.add(project)
    projects = manager.add(project)

    assert len(projects) == 1