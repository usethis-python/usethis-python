from usethis._pipeweld.containers import parallel, series
from usethis._pipeweld.func import Partition, _parallel_merge_partitions, add
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
            InsertParallel(after=None, step="A")
        ]
        assert result.solution == series("A")

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
            InsertParallel(after=None, step="B")
        ]
        assert result.solution == series(parallel("A", "B"))

    def test_parallel_singleton_start(self):
        # Arrange
        step = "B"
        pipeline = series(parallel("A"))

        # Act
        result = add(pipeline, step=step)

        # Assert
        assert isinstance(result, WeldResult)
        assert result.instructions == [
            # N.B. None means Place at the start of the pipeline
            InsertParallel(after=None, step="B")
        ]
        assert result.solution == series(parallel("A", "B"))

    def test_two_element_start(self):
        # Arrange
        step = "C"
        pipeline = series("A", "B")

        # Act
        result = add(pipeline, step=step)

        # Assert
        assert isinstance(result, WeldResult)
        assert result.instructions == [
            # N.B. None means Place at the start of the pipeline
            InsertParallel(after=None, step="C")
        ]
        assert result.solution == series(parallel("A", "C"), "B")

    def test_prerequisite(self):
        # Arrange
        step = "C"
        pipeline = series("A", "B")
        prerequisites = {"A"}

        # Act
        result = add(pipeline, step=step, prerequisites=prerequisites)

        # Assert
        assert isinstance(result, WeldResult)
        assert result.instructions == [InsertParallel(after="A", step="C")]
        assert result.solution == series("A", parallel("B", "C"))

    def test_mixed_dependency_parallelism_of_steps(self):
        # Arrange
        step = "C"
        pipeline = series(parallel("A", "B"))
        prerequisites = {"A"}
        postrequisites = {"B"}

        # Act
        result = add(
            pipeline,
            step=step,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
        )

        # Assert
        assert isinstance(result, WeldResult)
        assert result.solution == series("A", "C", "B")
        # TODO - assert about the instructions.


class TestParallelMergePartitions:
    def test_basic(self):
        # Arrange
        partition1 = Partition(
            prerequisite_component=None,
            nondependent_component="C",
            postrequisite_component=None,
            top_ranked_endpoint="C",
        )
        partition2 = Partition(
            prerequisite_component="A",
            nondependent_component=None,
            postrequisite_component="B",
            top_ranked_endpoint="B",
        )

        # Act
        result = _parallel_merge_partitions(partition1, partition2)

        # Assert
        assert result == Partition(
            prerequisite_component="A",
            nondependent_component="C",
            postrequisite_component="B",
            top_ranked_endpoint="B",
        )
