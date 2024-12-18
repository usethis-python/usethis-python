from usethis._pipeweld.containers import Series
from usethis._pipeweld.func import add
from usethis._pipeweld.ops import InsertSeries
from usethis._pipeweld.result import WeldResult


class TestAdd:
    def test_empty_series_start(self):
        # Arrange
        step = "A"
        pipeline = Series([])

        # Act
        result = add(pipeline, step=step)

        # Assert
        assert isinstance(result, WeldResult)
        assert result.instructions == [
            # N.B. None means Place at the start of the pipeline
            InsertSeries(before=None, step="A")
        ]
        assert result.solution == Series(["A"])
        assert result.traceback == [
            # Initial config
            Series([]),
            # Instruction 1.
            Series(["A"]),
        ]
