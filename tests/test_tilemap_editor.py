from lupix_studio.ui.tilemap_editor import (
    TileMapCanvas,
    TileMapEditor,
)


def test_tilemap_editor_classes_exist() -> None:
    assert (
        TileMapCanvas.__name__
        == "TileMapCanvas"
    )

    assert (
        TileMapEditor.__name__
        == "TileMapEditor"
    )