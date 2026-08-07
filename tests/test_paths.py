from lupix_studio.core.paths import logs_dir, settings_file, user_data_dir


def test_paths_are_inside_user_data_dir() -> None:
    root = user_data_dir()

    assert logs_dir().parent == root
    assert settings_file().parent == root