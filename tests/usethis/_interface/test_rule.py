from pathlib import Path

from usethis._integrations.uv.deps import get_deps_from_group
from usethis._interface.rule import rule
from usethis._test import change_cwd


class TestRule:
    # TODO lots of other more important tests to write.
    def test_ruff_gets_installed(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            rule(rules=["A"])

        # Assert
        assert "ruff" in get_deps_from_group(group="dev")
