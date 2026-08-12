from lupix_studio.ui.play_preview import (
    PlayCanvas,
    PlayPreview,
)


def test_play_preview_classes_exist() -> None:
    assert (
        PlayCanvas.__name__
        == "PlayCanvas"
    )

    assert (
        PlayPreview.__name__
        == "PlayPreview"
    )