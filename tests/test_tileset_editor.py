from lupix_studio.ui.tileset_editor import (
    TileSetCanvas,
    TileSetEditor,
)


def test_tileset_editor_classes_exist() -> None:
    assert TileSetEditor.__name__ == "TileSetEditor"
    assert TileSetCanvas.__name__ == "TileSetCanvas"


def test_tileset_index_formula() -> None:
    columns = 10
    column = 3
    row = 2

    tile_index = (
        row * columns
        + column
    )

    assert tile_index == 23