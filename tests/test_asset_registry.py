from pathlib import Path

from lupix_studio.assets.registry import AssetRegistry


def test_register_asset(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    asset = project / "assets" / "sprites" / "player.png"

    asset.parent.mkdir(
        parents=True
    )

    asset.write_bytes(b"png")

    registry = AssetRegistry(
        project
    )

    record = registry.register(
        name="player",
        asset_type="sprites",
        path=asset,
        width=32,
        height=32,
        color_count=16,
        compatibility="compatible",
    )

    assert record.id
    assert record.name == "player"
    assert record.path == "assets/sprites/player.png"

    loaded = registry.load()

    assert len(loaded) == 1
    assert loaded[0].id == record.id


def test_register_same_path_updates_record(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    asset = project / "assets" / "sprites" / "player.png"

    asset.parent.mkdir(
        parents=True
    )

    asset.write_bytes(b"png")

    registry = AssetRegistry(
        project
    )

    first = registry.register(
        name="player",
        asset_type="sprites",
        path=asset,
        width=16,
        height=16,
        color_count=8,
        compatibility="compatible",
    )

    second = registry.register(
        name="player",
        asset_type="sprites",
        path=asset,
        width=32,
        height=32,
        color_count=32,
        compatibility="conversion_required",
    )

    assert first.id == second.id
    assert len(registry.load()) == 1
    assert second.width == 32