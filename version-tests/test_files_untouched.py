"""Your files stay as you wrote them: v0.1-S23."""

from support import World, snapshot

READ_ONLY_COMMANDS = [
    (("check",), 0),
    (("list",), 0),
    (("list", "--tag", "快手"), 0),
    (("search", "番茄"), 0),
    (("show", "tomato-egg", "--servings", "4"), 0),
    (("menu", "show", "2026-W47"), 0),
    (("show", "mapo"), 1),
    (("menu", "show", "2026-W48"), 1),
    (("--help",), 0),
]


def test_v0_1_s23_your_files_stay_as_you_wrote_them(world: World) -> None:
    """v0.1-S23: reading commands change nothing, and `shop` changes only its own file."""
    world.copy_example()
    before = snapshot(world.home, world.work)
    for args, code in READ_ONLY_COMMANDS:
        assert world.run(*args).code == code, args
    assert snapshot(world.home, world.work) == before
    for _ in range(2):
        assert world.run("shop", "2026-W47").code == 0
    after = snapshot(world.home, world.work)
    shopping = world.data / "shopping"
    assert set(after.files) - set(before.files) == {shopping / "2026-W47.md"}
    assert set(after.folders) == set(before.folders)
    changed = {path for path in before.files if after.files[path] != before.files[path]}
    assert changed == set()
    assert [path.name for path in shopping.iterdir()] == ["2026-W47.md"]
