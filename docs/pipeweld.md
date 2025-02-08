# Pipeweld utility

Pipeweld is a utility for adding and removing steps from arbitrary pipelines given some
expected reference structure.

## On the Name "Pipeweld"

The idea is we're "welding" new components in and out of our pipeline. In addition,
"pipe weld" sounds a bit like like "pipe well".

## Concepts

### What do we mean by a pipeline?

The fundamental component of a pipeline is a _step_. A pipeline consists of steps
arranged in series and/or parallel. Parallel steps are executed simultaneously, and
series steps are executed in sequence.

Mathematically, this sort of pipeline can be modelled as a Series-Parallel graph, where
the nodes are steps.

### A simple example

Consider the following simple pipeline consisting of 3 steps: A, B, and C:

```Text
(A | B) + C
```

The informal notation above indicates a pipeline of two parallel steps A and B in series
with the final step C.

### A more complicated example

We can also consider more a more complicated pipeline in the below diagram:

```Text
(A | B | (C + D)) + E + (F | G) 
```

Here, A and B are in parallel with the series of steps C and D; those steps are all
in series with step E, and then finally also in
series we have the parallel steps F and G.

### Dependency

The next important concept is of dependencies between steps. A step can have
pre-requisites, which must be executed before it; as well as post-requisites, which must
be execute after it. Note that a dependency of either type must actually exist in the
pipeline; it is not pipeweld's responsibility to add missing dependencies.

## Solving the problem of dependencies

As mentioned earlier, we can model the pipeline as a Series-Parallel graph (SP-graph).
To insert a new step after its pre-requisites and before its post-requisites, we can
follow the following algorithm:

Iterate through each node starting from the source. If the node branches into parallel
branches, consider each of its parallel components (i.e. each series subgraph).
There are four cases:

1. The component contains neither a pre-requisite nor a post-requisite node.
2. The component contains a pre-requisite node but no post-requisite node.
3. The component contains a post-requisite node but no pre-requisite node.
4. The component contains both a pre-requisite and a post-requisite node.

All components in case 1 can be left as-is.

All components in case 2 can be moved to a new parallel subgraph placed in series
before the existing one, or do-nothing if all the components are in case 2.

All components in case 3 can be moved to a new parallel subgraph placed in series
after the existing one, or do nothing if all the components are in case 3.

For components in case 4, it might be that a post-requisite occurs before a
pre-requisite, in which case the dependencies are contradictory, and we will ignore
the post-requisite (see explanation) and treat the case like case 2.
Otherwise, we can move the post-requisite and all subsequent nodes in the component to
the same parallel subgraph as those in case 3, placed in series after the existing one.
Then, the remainder of the component can be placed in series before the parallel
subgraph (the same as in case 2).

After applying this transformation, return to the source and repeat the process until
no parallel blocks are of case 4, in which case the process is idempotent.

The immediate successor of the latest case 2 block (if any, otherwise if no latest case
2 block then use the source node) should be identified. The new step can be placed in
parallel with the successor, unless the successor is a post-requisite, in which case the
new step can be placed in series before the successor.

If this solution does not satisfy all post-requisites, it means that either the
pre-requisites and post-requisites are contradictory, including the possibility that
they are impossible to satisfy with current pipeline structure without modifying its
logical structure.

### Why we choose to prefer to satisfy pre-requisites over post-requisites

We would prefer to comply with the pre-requisites since if the previous pipeline
(before adding the new step) was able to run successfully then it is fairly unlikely
that the post-requisites would fail to run successfully just because the new step is
run after it (in other words, true post-requisites are likely to be very uncommon).

## Complex pipelines might not be supported on all platforms

Depending on how you implement your pipeline, some complex pipelines might not be
supported. For example, in Bitbucket Pipelines, having series steps inside a parallel
block is not supported, so the above pipeline would not be possible to implement at
present.

Rudimentary pipeline software may not even support parallelism.

Pipeweld can be configured to respect these two restrictions and avoid modifying a
pipeline in a way that would create an impossible-to-represent pipeline for your use
case.

If you are using a platform with a different sort of restriction then please open an
issue for this to be supported.

### Handling restrictions on parallelism

If parallelism is not supported, then the solution is the same as above, except the
new step should not be inserted in parallel but rather in series with the identified
node (similar to the case of where the identified node is a post-requisite).

### Handling restrictions on composition depth

If parallelism is only possible between nodes and not full subgraphs then the solution
is the same as above, except the new step should only be inserted in parallel with the
identified node if the identified node is not already in a parallel subgraph. Otherwise,
the new step should be inserted in series before the identified node.

## Introducing Configuration Groups

Pipeline steps often share configuration in the way they are to be executed, e.g. in the
case of pre-commit, two hooks (i.e. pipeline steps) might share the same repo
(i.e. a configuration group).

For example, consider the following diagram:

```Text
A + [B + C]
```

The above three steps are in series, but B and C are in the same configuration group.
A configuration group must be in series, i.e. every node must have a single predecessor
and successor. Steps cannot be in multiple configuration groups. All configuration
groups can be compared with some equivalence relation; so two groups might have
different members but have the same group type (e.g. they have the same configuration
metadata).

Configuration groups are usually a way to improve performance and improve clarity
in pipeline declaration syntax. However, there may be some circumstances where it is
mandatory that steps must be in the same group for correctness of execution.

In Pipeweld, you can specify that sets of steps are compatible to be in the same type
of group as the new step being added, and/or mandatory to be in the same group. Unless
specified, it is assumed that steps are not compatible to be in the same type of group.

### Handling Configuration Groups

If it is mandatory for a step to be in the same configuration group as a set of other
steps, then we can apply the same algorithm above to the SP-subgraph associated with the
configuration group. If the solution satisfies the dependencies (post-requisites and
pre-requisites), then we are done. Otherwise, there is a contradiction, so we need to
choose whether it is better to satisfy dependencies or configuration groups. Pipeweld
would choose to satisfy dependencies in this case and will backtrack to resolve without
the condition that the configuration group is mandatory (basically, it will ignore this
constraint).

If it is merely optional for a step to be in the same configuration group as another set
of steps, then this is basically a cosmetic decision which can determined after the
new step has been inserted; should it form a configuration group with its predecessor,
or successor, or both? Pipeweld will choose to form with both if possible, and with any
existing group in precedence to creating a new group (including combining the
predecessor and successor steps' groups into a single group, if they the two groups are
of the same type). Any further tiebreaks will be broken by preferring to form a group
with the predecessor rather than the successor.

There is also the possibility that the new step is inserted into the middle of an
configuration group but is not compatible with that group's type. In that case,
Pipeweld will "break-up" the group into two separate groups (of the same type as the
original). Singleton groups will not be collapsed.

## Removing a step

Removing a step is a simpler problem than adding a step. We can simply remove the step
and then if the step's successor or predecessor are in the same group type, the groups
can be merged, provided the predecessor's only successor was the removed step, and the
successor's only predecessor was the added step.

## The interface

Here are some considerations for the Pipeweld interface.

1. We want to be able to actually modify the pipeline file, e.g. a YAML file. In
usethis, at time of writing this is achieved by representing the pipeline as a
pydantic object and then updating the specialized ruamel.yaml class once changes have
been made to the pydantic object. If pipeweld can represent its solution in a way that
makes it straightforward to modify the pydantic objects, that would be ideal.
2. Without configuration groups, a pipeline can be represented as a composition of
lists, sets, and steps. Lists represent Series blocks, Sets represent parallel blocks.
Nesting sets-in-sets or series-in-series could be forbidden for simplicity, although
potentially it would be simpler to simply accept these cases.
3. Configuration groups add complexity, but they are effectively a special kind of
Series arrangement so could be represented with their own collection type. The group
type needs to be represented, perhaps by a name attribute.
4. Dependencies are only necessary to declare for a step being added. This can just
be a collection of steps which are pre-requisites, and a collection which are
post-requisites. This requires some way to identify steps; either step objects could
be named, and then we reference by name, or we could refer to the objects themselves,
e.g. the user could just represent steps with integer IDs or with string names directly
since we never need to access step metadata. For now, string names of the steps would
be sufficient.
5. Should a solution be the modified pipeline representation or the instructions on how
to modify the pipeline? We could also return both. Instructions on how to modify are
likely to be more useful. There are four operations needed to represent modification
when adding a step; "insert as successor" and "insert after in parallel",
"insert after in series", and "split group". To remove a step requires two more;
"remove" (a unary operation), and "combine groups". A list of these operations would
represent the instructions on how to modify the pipeline. If this is our objective, then
Pipeweld needs to be either be able to generate these instructions given a
before-and-after view of the pipeline, or it needs to keep track of modification
instructions in the progress of determining the solution. The latter seems like it would
be simpler.
6. While flexibility is helpful, a canonical form for a pipeline that the outermost
level is always a list, is helpful to require.

## Worked solutions for adding steps

These examples will be useful for writing unit tests.

### Example 1 (Empty Series Start)

```Python
step = "A"
pipeline = []
prerequisites = []
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [InsertParallel(None, "A")] # N.B. Place at the start of the pipeline
solution = ["A"]
traceback = [
    # Initial config
    [],
    # Instruction 1.
    [{"A"}],
    ["A"], # Simplify
]
```

### Example 2 (Series Singleton Start)

```Python
step = "B"
pipeline = ["A"]
prerequisites = []
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [InsertParallel(None, "B")]
solution = [{"A", "B"}]
traceback = [
    # Initial config
    ["A"],
    # Instruction 1.
    [{"A", "B"}],
]
```

### Example 3 (Parallel Singleton Start)

```Python
step = "B"
pipeline = [{"A"}]
prerequisites = []
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [InsertParallel(None, "B")]
solution = [{"A", "B"}]
traceback = [
    # Initial config
    [{"A"}],
    # Instruction 1.
    [{"A", "B"}],
]
```

### Example 4 (Series Two Element Start)

```Python
step = "C"
pipeline = ["A", "B"]
prerequisites = []
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [InsertParallel(None, "C")]
solution = [{"A", "C"} "B"]
traceback = [
    # Initial config
    ["A", "B"],
    # Instruction 1.
    [{"A", "C"}, "B"],
]
```

### Example 5 (Pre-requisite)

```Python
step = "C"
pipeline = ["A", "B"]
prerequisites = ["A"]
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [InsertParallel("A", "C")]
solution = ["A", {"B", "C"}]
traceback = [
    # Initial config
    ["A", "B"],
    # Instruction 1.
    ["A", {"B", "C"}],
]
```

### Example 6 (Mixed dependency parallelism of steps)

```Python
step = "C"
pipeline = [{"A", "B"}]
prerequisites = ["A"]
postrequisites = ["B"]
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [
    InsertParallel(None, "A"),
    InsertParallel("B", "B"), # Optional insofar as it is a no-op
    InsertSuccessor("A", "C"), # Note; successor since the pre-requisites might be in a
                               # parallel block (although not in this case). If C was
                               # OK to be in a parallel block with A's successor B then
                               # we would use InsertParallel, but in this case it isn't.
]
solution = ["A", "C", "B"]
traceback = [
    # Initial config
    [{"A", "B"}],
    # Instruction 1.
    [{"A"}, {"B"}],
    ["A", "B"], # Simplify
    # Instruction 2.
    ["A", {"B"}],
    ["A", "B"], # Simplify
    # Instruction 3.
    ["A", "C", "B"],
]
```

### Example 7 (Multi-level hierarchy)

```Python
step = "E"
pipeline = ["A", {"B", ["C", "D"]}]
prerequisites = ["C"]
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [InsertParallel("C", "E")]
solution = ["A", {"B", ["C", {"D", "E"}]}]
traceback = [
    # Initial config
    ["A", {"B", ["C", "D"]}],
    # Instruction 1.
    ["A", {"B", ["C", {"D", "E"}]}],
]
```

### Example 8 (Mixed dependency parallelism of series)

```Python
step = "E"
pipeline = [{["A", "B"], ["C", "D"]}]
prerequisites = ["A"]
postrequisites = ["D"]
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [
    # Move the case 2 block to a new parallel block (although there is only one so
    # it doesn't look parallel)
    InsertParallel(None, "A"),
    InsertSuccessor("A", "B"), # Successor since B is part of a series block with A
                               # InsertSeries would jump out of any parallelism but we
                               # want to keep the series block intact
    # Move the case 3 block to a new parallel block (again its a singleton parallelism
    # so it won't look parallel)
    InsertParallel("D", "C"),
    InsertSuccessor("C", "D"), # Successor since C is part of a series block with D
    # Add the new step
    InsertParallel("A", "E"), # Parallel rather than successor because it's safe to put
                              # E with B without violating post-requisites.
]
solution = ["A", {"E", "B"}, "C", "D"]
# Note how this is achieved with a traceback. It's worth considering the need to
# simplify the representation of the pipeline whenever moving a step; are we moving it
# out of a singleton block that can be collapsed? If inserting in series, we need to
# see whether the element is already in series (just insert into existing series) or
# parallel (insert into a new series block). If inserting in parallel, we need to see
# whether the element already has a parallel block as its successor (just insert into
# that block), or a step (insert both into a new parallel block). In simplified 
# representation, a step cannot have a series block as its successor, only a step.
traceback = [
    # Initial config
    [{["A", "B"], ["C", "D"]}],
    # Instruction 1.
    [{{"A"}, ["B"], ["C", "D"]}],
    [{"A", "B", ["C", "D"]}], # Simplify 
    # Instruction 2.
    [{["A", "B"], ["C", "D"]}],
    # Instruction 3.
    [{["A", "B"], ["D"]}, {"C"}], 
    [{["A", "B"], "D"}, "C"], # Simplify
    # Instruction 4.
    [{["A", "B"]}, ["C", "D"]],
    [["A", "B"], ["C", "D"]], # Simplify
    ["A", "B", "C", "D"], # Simplify
    # Instruction 5.
    ["A", {"E", "B"}, "C", "D"],
]
```

### Example 9 (Configuration Groups)

```Python
step = "E"
pipeline = ["A", Group(["B", "C"], "x")]
prerequisites = ["B"]
postrequisites = []
compatible_config_groups = ["x"]
mandatory_config_groups = []
max_depth = None
...
instructions = [
    SplitGroup("B"),         # We are about to InsertParallel to B but configuration
                             # groups must be in series, so split first.
    InsertParallel("B", "E")
]
# Note the motivation here: we want to maximize parallelism so we are willing to break
# up the dependency group!
solution = ["A", Group(["B"], "x"), {Group(["C"], "x"), "E"}]
traceback = [
    # Initial config
    ["A", Group(["B", "C"], "x")],
    # Instruction 1.
    ["A", Group(["B"], "x"), Group(["C"], "x")],
    # Instruction 2.
    ["A", Group(["B"], "x"), {Group(["C"], "x"), "E"}],
]
```

### Example 10 (Configuration Groups with zero depth)

```Python
step = "E"
pipeline = ["A", Group(["B", "C"], "x")]
prerequisites = ["B"]
postrequisites = []
compatible_config_groups = ["x"]
mandatory_config_group = []
max_depth = 0
...
instructions = [
    InsertSuccessor("B", "E"),# Normally would insert in parallel since B's successor C
                              # is not a post-requisite, however max depth is 0 so we
                              # insert as a successor instead.          
]
solution = ["A", Group(["B", "E", "C"], "x")]
traceback = [
    # Initial config
    ["A", Group(["B", "C"], "x")],
    # Instruction 1.
    ["A", Group(["B", "E", "C"], "x")],
]
```

### Example 11 (Configuration Groups with mixed dependencies)

```Python
step = "E"
pipeline = ["A", Group(["B", "C"], "x")]
prerequisites = ["B"]
postrequisites = ["C"]
compatible_config_groups = ["x"]
mandatory_config_group = []
max_depth = None
...
instructions = [
    InsertSuccessor("B", "E") # Insert as a successor since B's successor C is a post
                             # requisite, and B is in a compatible configuration group.
]
solution = ["A", Group(["B", "E", "C"], "x")]
traceback = [
    # Initial config
    ["A", Group(["B", "C"], "x")],
    # Instruction 1.
    ["A", Group(["B", "E", "C"], "x")],
]
```

### Example 12 (Breaking up a configuration group)

```Python
step = "E"
pipeline = ["A", Group(["B", "C"], "x")]
prerequisites = ["B"]
postrequisites = ["C"]
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [
    SplitGroup("B"),         # We are about to InsertSeries to B, so split first to
                             # avoid adding to the incompatible group.
    InsertSeries("B", "E")   # Insert as in series since B's successor C is a
                             # post-requisite, and B is in an incompatible configuration
                             # group.
]
solution = ["A", Group(["B"], "x"), "E", Group(["C"], "x")]
traceback = [
    # Initial config
    ["A", Group(["B", "C"], "x")],
    # Instruction 1.
    ["A", Group(["B", "E", "C"], "x")],
]
```

### Example 13 (Mixed compatibility)

```Python
step = "E"
pipeline = ["A", Group(["B"], "x"), Group(["C"], "y")]
prerequisites = ["B"]
postrequisites = []
compatible_config_groups = ["y"]
mandatory_config_group = []
max_depth = None
...
instructions = [
    InsertSeries("B", "E")   # Insert in series since B's successor C is a
                             # post-requisite (so we don't want to insert parallel),
                             # and B is in an incompatible configuration group.
                             # (so we don't want to insert successor).
    AddToGroup("B", "y"),    # The successor to B is in a compatible configuration group
                             # and B only has one successor (C) so we can form a group.
                             # We need to check this when inserting series.
]
solution = ["A", Group(["B"], "x"), Group(["B", "C"], "y")]
traceback = [
    # Initial config
    ["A", Group(["B"], "x"), Group(["C"], "y")],
    # Instruction 1.
    ["A", Group(["B"], "x"), "E", Group(["C"], "y")],
    # Instruction 2.
    ["A", Group(["B"], "x"), Group(["E"], "y"), Group(["C"], "y")],
    ["A", Group(["B"], "x"), Group(["B", "C"], "y")] # Simplify - the step which is
                                                     # newly added to a group
                                                     # has a single successor in the
                                                     # same group.
]
```

### Example 14 (Parallel to group)

```Python
step = "E"
pipeline = ["A", Group(["B", "C"], "x")]
prerequisites = ["A"]
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [
    InsertParallel("A", "E"),
]
solution = ["A", {Group(["B", "C"], "x"), "E"}]
traceback = [
    # Initial config
    ["A", Group(["B", "C"], "x")],
    # Instruction 1.
    ["A", {Group(["B", "C"], "x"), "E"}],
]
```

### Example 15 (Parallelism forbidden)

```Python
step = "D"
pipeline = ["A", "B", "C"]
prerequisites = ["B"]
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = 0
...
instructions = [
    InsertSuccessor("B", "D") # usually we would insert in parallel since B's successor
                           # C is not a post-requisite, but B's successor is C which 
                           # is at depth 0 !< 0 so we insert as a successor.
]
solution = ["A", "B", "D", "C"]
traceback = [
    # Initial config
    ["A", "B", "C"],
    # Instruction 1.
    ["A", "B", "D", "C"],
]
```

### Example 16 (Max depth of 1)

```Python
step = "D"
pipeline = ["A", {"B", "C"}]
prerequisites = ["B"]
postrequisites = []
compatible_config_groups = []
mandatory_config_group = []
max_depth = 1
...
instructions = [
    InsertParallel("B", "D") # Insert in parallel since B's successor C is not a
                             # post-requisite, and the successor to B is the sink node
                             # i.e. at depth 0 < 1. 
]
solution = ["A", {"B", "C"}, "D"]
traceback = [
    # Initial config
    ["A", {"B", "C"}],
    # Instruction 1.
    ["A", {"B", "C"}, {"D"}]
    ["A", {"B", "C"}, "D"] # Simplify
]
```

### Example 17 (Contradictory mixed dependencies)

```Python
step = "D"
pipeline = ["A", "B", "C"]
prerequisites = ["C"]
postrequisites = ["B"]
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [
    InsertParallel("C", "D") # We ignore the post-requisite because of the
                              # contradiction
]
solution = ["A", "B", "C", "D"]
traceback = [
    # Initial config
    ["A", "B", "C"],
    # Instruction 1.
    ["A", "B", "C", {"D"}],
    ["A", "B", "C", "D"], # Simplify
]
```

### Example 18 (Contradictory mixed dependencies in parallel)

```Python
step = "D"
pipeline = [{["A", "B"], "C"}]
prerequisites = ["B"]
postrequisites = ["A"]
compatible_config_groups = []
mandatory_config_group = []
max_depth = None
...
instructions = [
    # Ignoring the impossible-to-satisfy post-requisite, we treat the A-B series as
    # a case 2 parallel component. Not all the components are in case 2 (C is in
    # case 1) so we need to move the case 2 block.
    InsertParallel(None, "A"),
    InsertSuccessor("A", "B"),
    # Now, all parallel blocks are pure case 2 and case 1 so we can insert the step
    InsertParallel("B", "D"), # in parallel since B's successor C is not a
                              # post-requisite
]
solution = ["A", "B", {"C", "D"}]
traceback = [
    # Initial config
    [{["A", "B"], "C"}],
    # Instruction 1.
    [{"A"}, {["B"], "C"}],
    ["A", {"B", "C"}], # Simplify since we have moved step B
    # Instruction 2.
    [["A", "B"], {"C"}],
    [["A", "B"], "C"], # Simplify since we have moved step B
    ["A", "B", "C"], # Simplify since we have collapsed a singleton parallelism
    # Instruction 3.
    ["A", "B", {"C", "D"}],
]
```
