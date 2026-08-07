from lupix_studio.settings.manager import StudioSettings


def test_default_settings() -> None:
    settings = StudioSettings()

    assert settings.theme == "dark"
    assert settings.language == "pt_BR"
    assert settings.recent_projects_limit == 10