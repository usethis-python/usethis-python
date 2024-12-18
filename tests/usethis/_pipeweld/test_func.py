from usethis._pipeweld.containers import parallel, series
from usethis._pipeweld.func import add
from usethis._pipeweld.ops import InsertParallel
from usethis._pipeweld.result import WeldResult


class TestAdd:
    def test_empty_series_start(self):
        # Arrange
        step = "A"
        pipeline = series()

        # Act
        result = add(pipeline, step=step)

        # Assert
        assert isinstance(result, WeldResult)
        assert result.instructions == [
            # N.B. None means Place at the start of the pipeline
            InsertParallel(before=None, step="A")
        ]
        assert result.solution == series("A")
        assert result.traceback == [
            # Initial config
            series(),
            # Instruction 1. & simplify
            series("A"),
        ]

    def test_series_singleton_start(self):
        # Arrange
        step = "B"
        pipeline = series("A")

        # Act
        result = add(pipeline, step=step)

        # Assert
        assert isinstance(result, WeldResult)
        assert result.instructions == [
            # N.B. None means Place at the start of the pipeline
            InsertParallel(before=None, step="B")
        ]
        assert result.solution == series(parallel("A", "B"))
        assert result.traceback == [
            # Initial config
            series("A"),
            # Instruction 1.
            series(parallel("A", "B")),
        ]
