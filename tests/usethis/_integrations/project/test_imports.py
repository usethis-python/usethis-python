from pathlib import Path

import grimp
import pytest

from usethis._integrations.project.errors import ImportGraphBuildFailedError
from usethis._integrations.project.imports import (
    LayeredArchitecture,
    _filter_to_submodule,
    _get_child_dependencies,
    _get_graph,
    _get_module_layered_architecture,
    get_layered_architectures,
)
from usethis._test import change_cwd


class TestGetLayeredArchitectures:
    def test_five(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()
        (tmp_path / "salut" / "a").mkdir()
        (tmp_path / "salut" / "a" / "__init__.py").touch()
        (tmp_path / "salut" / "b.py").write_text("""\
import salut.a
""")
        (tmp_path / "salut" / "c.py").write_text("""\
import salut.a
import salut.b
""")
        (tmp_path / "salut" / "d").mkdir()
        (tmp_path / "salut" / "d" / "__init__.py").touch()
        (tmp_path / "salut" / "d" / "e.py").write_text("""\
import salut.a
import salut.b
import salut.d.f
""")
        (tmp_path / "salut" / "d" / "f.py").touch()

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            arch_by_module = get_layered_architectures("salut")

        # Assert
        assert isinstance(arch_by_module, dict)
        for arch in arch_by_module.values():
            assert isinstance(arch, LayeredArchitecture)
        assert len(arch_by_module) == 2
        assert arch_by_module["salut"].layers == [{"c", "d"}, {"b"}, {"a"}]
        assert arch_by_module["salut"].excluded == set()
        assert arch_by_module["salut.d"].layers == [{"e"}, {"f"}]
        assert arch_by_module["salut.d"].excluded == set()


class TestGetModuleLayeredArchitecture:
    def test_three(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()
        (tmp_path / "salut" / "a.py").touch()
        (tmp_path / "salut" / "b.py").write_text("""\
import salut.a
""")
        (tmp_path / "salut" / "c.py").write_text("""\
import salut.a
import salut.b
""")

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")
            arch = _get_module_layered_architecture("salut", graph=graph)

        # Assert
        assert isinstance(arch, LayeredArchitecture)
        assert arch.layers == [{"c"}, {"b"}, {"a"}]
        assert arch.excluded == set()

    def test_independent(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()
        (tmp_path / "salut" / "a.py").touch()
        (tmp_path / "salut" / "b.py").touch()

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")
            arch = _get_module_layered_architecture("salut", graph=graph)

        # Assert
        assert isinstance(arch, LayeredArchitecture)
        assert arch.layers == [{"a", "b"}]
        assert arch.excluded == set()

    def test_cyclic(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()
        (tmp_path / "salut" / "a.py").write_text("""\
import salut.b
""")
        (tmp_path / "salut" / "b.py").write_text("""\
import salut.a
""")

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")
            arch = _get_module_layered_architecture("salut", graph=graph)

        # Assert
        assert isinstance(arch, LayeredArchitecture)
        assert arch.layers == []
        assert arch.excluded == {"a", "b"}

    def test_bottom_heavy(self, tmp_path: Path):
        # For a given package structure, there are multiple possible layered
        # architectures it will comply with. We would prefer one which is "bottom heavy",
        # i.e. one or modules which depend on many independent modules, rather than
        # many independent modules which depend on one module.
        # Consider the following package structure:
        #
        # A
        # └── D
        # └── E
        #     ├── F
        #     └── G
        # B
        # C
        #
        # The following layered architectures are possible:
        # > {"B", "C", "F", "G"}, {"D", "E"}, {"A"}
        # > {'C', 'D', 'B', 'G', 'F'}, {'E'}, {'A'}
        # But this is bottom-heavy, and so preferred:
        # > {"F", "G"}, {"D", "E"}, {"A", "B", "C"}

        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()
        (tmp_path / "salut" / "a.py").touch()
        (tmp_path / "salut" / "b.py").touch()
        (tmp_path / "salut" / "c.py").touch()
        (tmp_path / "salut" / "d.py").write_text("""\
import salut.a
""")
        (tmp_path / "salut" / "e.py").write_text("""\
import salut.a
""")
        (tmp_path / "salut" / "f.py").write_text("""\
import salut.e
""")
        (tmp_path / "salut" / "g.py").write_text("""\
import salut.e
""")

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")
            arch = _get_module_layered_architecture("salut", graph=graph)

        # Assert
        assert isinstance(arch, LayeredArchitecture)
        assert arch.layers == [{"f", "g"}, {"d", "e"}, {"a", "b", "c"}]
        assert arch.excluded == set()


class TestGetChildDependencies:
    def test_three(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()
        (tmp_path / "salut" / "a.py").touch()
        (tmp_path / "salut" / "b.py").write_text("""\
import salut.a
""")
        (tmp_path / "salut" / "c.py").write_text("""\
import salut.a
import salut.b
""")

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")
            deps_by_module = _get_child_dependencies("salut", graph=graph)

        # Assert
        assert deps_by_module == {
            "a": set(),
            "b": {"a"},
            "c": {"a", "b"},
        }

    def test_two(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()
        (tmp_path / "salut" / "a.py").touch()
        (tmp_path / "salut" / "b.py").write_text("""\
import salut.a
""")

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")
            deps_by_module = _get_child_dependencies("salut", graph=graph)

        # Assert
        assert deps_by_module == {
            "a": set(),
            "b": {"a"},
        }

    def test_none(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")
            deps_by_module = _get_child_dependencies("salut", graph=graph)

        # Assert
        assert deps_by_module == {}

    # TODO test sub-module as arg


class TestFilterToSubmodule:
    def test_simple_case(self):
        # Arrange
        modules = {"salut", "salut.a", "salut.b", "salut.c"}

        # Act
        filtered = _filter_to_submodule(modules, submodule="salut")

        # Assert
        assert filtered == {"a", "b", "c"}

    def test_no_submodule(self):
        # Arrange
        modules = {"salut", "salut.a", "salut.b", "salut.c"}

        # Act
        filtered = _filter_to_submodule(modules, submodule="does_not_exist")

        # Assert
        assert filtered == set()

    def test_grandchild(self):
        # Arrange
        modules = {"salut", "salut.a", "salut.b", "salut.c", "salut.a.d"}

        # Act
        filtered = _filter_to_submodule(modules, submodule="salut.a")

        # Assert
        assert filtered == {"d"}

    def test_child_with_children(self):
        # Arrange
        modules = {"salut", "salut.a", "salut.b", "salut.c", "salut.a.d"}

        # Act
        filtered = _filter_to_submodule(modules, submodule="salut")

        # Assert
        assert filtered == {"a", "b", "c"}


class TestGetGraph:
    def test_type(self, tmp_path: Path):
        # Arrange
        (tmp_path / "salut").mkdir()
        (tmp_path / "salut" / "__init__.py").touch()

        # Act
        with change_cwd(tmp_path, add_to_path=True):
            graph = _get_graph("salut")

        # Assert
        assert isinstance(graph, grimp.ImportGraph)

    def test_self(self, tmp_path: Path):
        # Act
        graph = _get_graph("usethis")

        # Assert
        assert isinstance(graph, grimp.ImportGraph)

    def test_does_not_exist(self, tmp_path: Path):
        # Act, Assert
        with pytest.raises(ImportGraphBuildFailedError):
            _get_graph("does_not_exist")
