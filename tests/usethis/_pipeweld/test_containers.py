from usethis._pipeweld.containers import (
    DepGroup,
    Parallel,
    Series,
    depgroup,
    parallel,
    series,
)


class TestSeries:
    def test_func(self):
        assert series("a", "b") == Series(["a", "b"])

    def test_hash_same(self):
        assert hash(Series(["a", "b"])) == hash(Series(["a", "b"]))

    def test_hash_different(self):
        assert hash(Series(["a", "b"])) != hash(Series(["b", "a"]))

    def test_getitem(self):
        assert Series(["a", "b"])[0] == "a"

    def test_setitem(self):
        series = Series(["a", "b"])
        series[0] = "c"
        assert series == Series(["c", "b"])

    def test_eq_same(self):
        assert Series(["a", "b"]) == Series(["a", "b"])

    def test_eq_different(self):
        assert Series(["a", "b"]) != Series(["b", "a"])

    def test_eq_wrong_type(self):
        assert Series(["a", "b"]) != ["a", "b"]

    def test_len(self):
        assert len(Series(["a", "b"])) == 2


class TestParallel:
    def test_func(self):
        assert parallel("a", "b") == Parallel(frozenset({"a", "b"}))

    def test_hash_same(self):
        assert hash(Parallel(frozenset({"a", "b"}))) == hash(
            Parallel(frozenset({"a", "b"}))
        )

    def test_hash_different(self):
        assert hash(Parallel(frozenset({"a", "b"}))) != hash(Parallel(frozenset({"a"})))

    def test_or(self):
        assert Parallel(frozenset({"a"})) | Parallel(frozenset({"b"})) == Parallel(
            frozenset({"a", "b"})
        )

    def test_eq_same(self):
        assert Parallel(frozenset({"a", "b"})) == Parallel(frozenset({"a", "b"}))

    def test_eq_subset(self):
        assert Parallel(frozenset({"a", "b"})) != Parallel(frozenset({"a"}))

    def test_eq_superset(self):
        assert Parallel(frozenset({"a"})) != Parallel(frozenset({"a", "b"}))

    def test_eq_wrong_type(self):
        assert Parallel(frozenset({"a", "b"})) != {"a", "b"}
        assert Parallel(frozenset({"a", "b"})) != frozenset({"a", "b"})

    def test_len(self):
        assert len(Parallel(frozenset({"a", "b"}))) == 2


class TestDepGroup:
    def test_func(self):
        assert depgroup("a", "b", config_group="group") == DepGroup(
            series=series("a", "b"), config_group="group"
        )

    def test_hash_same(self):
        assert hash(DepGroup(series=series("a", "b"), config_group="group")) == hash(
            DepGroup(series=series("a", "b"), config_group="group")
        )

    def test_hash_different(self):
        assert hash(DepGroup(series=series("a", "b"), config_group="group")) != hash(
            DepGroup(series=series("b", "a"), config_group="group")
        )
