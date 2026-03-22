from __future__ import annotations

from usethis._file.merge import deep_merge


class TestDeepMerge:
    class TestBasicMerge:
        def test_top_level_key_added(self) -> None:
            target: dict = {"a": 1}
            source: dict = {"b": 2}
            result = deep_merge(target, source)
            assert result == {"a": 1, "b": 2}

    class TestNestedDicts:
        def test_nested_merge(self) -> None:
            target: dict = {"a": {"x": 1}}
            source: dict = {"a": {"y": 2}}
            result = deep_merge(target, source)
            assert result == {"a": {"x": 1, "y": 2}}

        def test_deeply_nested(self) -> None:
            target: dict = {"a": {"b": {"c": 1}}}
            source: dict = {"a": {"b": {"d": 2}}}
            result = deep_merge(target, source)
            assert result == {"a": {"b": {"c": 1, "d": 2}}}

    class TestReplacementOfNonDictValues:
        def test_scalar_replaced_by_scalar(self) -> None:
            target: dict = {"a": 1}
            source: dict = {"a": 2}
            result = deep_merge(target, source)
            assert result == {"a": 2}

        def test_dict_replaced_by_scalar(self) -> None:
            target: dict = {"a": {"x": 1}}
            source: dict = {"a": 99}
            result = deep_merge(target, source)
            assert result == {"a": 99}

        def test_scalar_replaced_by_dict(self) -> None:
            target: dict = {"a": 99}
            source: dict = {"a": {"x": 1}}
            result = deep_merge(target, source)
            assert result == {"a": {"x": 1}}

        def test_list_replaced_by_list(self) -> None:
            target: dict = {"a": [1, 2]}
            source: dict = {"a": [3, 4]}
            result = deep_merge(target, source)
            assert result == {"a": [3, 4]}

    class TestInPlaceMutation:
        def test_returns_target(self) -> None:
            target: dict = {"a": 1}
            source: dict = {"b": 2}
            result = deep_merge(target, source)
            assert result is target

        def test_target_is_mutated(self) -> None:
            target: dict = {"a": 1}
            source: dict = {"b": 2}
            deep_merge(target, source)
            assert target == {"a": 1, "b": 2}

    class TestDisjointKeys:
        def test_disjoint_keys_merged(self) -> None:
            target: dict = {"a": 1, "b": 2}
            source: dict = {"c": 3, "d": 4}
            result = deep_merge(target, source)
            assert result == {"a": 1, "b": 2, "c": 3, "d": 4}

        def test_empty_source(self) -> None:
            target: dict = {"a": 1}
            source: dict = {}
            result = deep_merge(target, source)
            assert result == {"a": 1}

        def test_empty_target(self) -> None:
            target: dict = {}
            source: dict = {"a": 1}
            result = deep_merge(target, source)
            assert result == {"a": 1}
