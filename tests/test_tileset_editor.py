from lupix_studio.ui.tileset_editor import (
    TileSetCanvas,
    TileSetEditor,
)


def test_tileset_editor_classes_exist() -> None:
    assert TileSetEditor.__name__ == "TileSetEditor"
    assert TileSetCanvas.__name__ == "TileSetCanvas"