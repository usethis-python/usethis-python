from __future__ import annotations

from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from ruamel.yaml.comments import (
    CommentedMap,
)

if TYPE_CHECKING:
    from typing import Any

    from usethis._integrations.file.yaml.io_ import YAMLLiteral


def update_ruamel_yaml_map(
    cmap: YAMLLiteral,
    new_contents: dict[str, Any],
    *,
    preserve_comments: bool,
) -> None:
    """Update the values of a ruamel.yaml map in-place using a diff-like algorithm.

    Updates preserve ruamel.yaml-specific metadata such as comments.

    Args:
        cmap: The ruamel.yaml object to update.
        new_contents: The new contents to update the map with.
        preserve_comments: Whether to preserve comments in the map.

    Raises:
        TypeError: If the provided `cmap` is not a CommentedMap.
    """
    """Update the values of a ruamel.yaml map in-place using a diff-like algorithm."""
    if not isinstance(cmap, CommentedMap):
        msg = f"Expected CommentedMap, but got '{type(cmap)}'."
        raise TypeError(msg)

    if not preserve_comments:
        msg = "Removing existing comments on over-written content not yet supported."
        raise NotImplementedError(msg)

    for key, value in new_contents.items():
        if key not in cmap:
            cmap[key] = value
        elif isinstance(value, dict):
            if not isinstance(cmap[key], CommentedMap):
                cmap[key] = CommentedMap()
            update_ruamel_yaml_map(
                cmap[key],
                value,
                preserve_comments=True,
            )
        elif isinstance(value, list):
            lcs_list_update(cmap[key], value)
        else:
            cmap[key] = value

    # Ensure order matches
    cmap_copy = cmap.copy()
    for key in cmap_copy:
        del cmap[key]
    for key in new_contents:
        cmap[key] = cmap_copy[key]


def lcs_list_update(original: list, new: list) -> None:
    """Update in-place using a longest common subsequence solver.

    This makes `original` identical to `new`, but respects subtypes of list such as
    CommentedSeq provided by ruamel.yaml by performing safe, in-place updates in a way
    that doesn't lose important metadata associated with individual list items.
    """
    # N.B. this implementation is somewhat AI-generated.

    # Create shared integer mappings for unhashable sequences
    int_original, int_new = _shared_id_sequences(original, new)

    # Run SequenceMatcher on the integer representations
    sm = SequenceMatcher(None, int_original, int_new, autojunk=False)
    original_idx = 0

    # Process the opcodes with respect to the original sequences
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            # Move forward for equal segments
            original_idx += i2 - i1

        elif op == "replace":
            # Replace elements individually in `original` with elements from `new`
            replacement_length = min(i2 - i1, j2 - j1)
            for k in range(replacement_length):
                original[original_idx + k] = new[j1 + k]

            # If new segment is longer, insert the additional items
            for k in range(replacement_length, j2 - j1):
                original.insert(original_idx + k, new[j1 + k])

            # If original segment was longer, delete the extra items
            for _ in range(replacement_length, i2 - i1):
                del original[original_idx + replacement_length]

            original_idx += j2 - j1

        elif op == "delete":
            # Delete each element individually
            for _ in range(i1, i2):
                del original[original_idx]

        elif op == "insert":
            # Insert each element individually from `new`
            for k in range(j1, j2):
                original.insert(original_idx, new[k])
                original_idx += 1


def _shared_id_sequences(*seqs: list[Any]) -> list[list[int]]:
    """Map list elements to integers which are equal iff the objects are with __eq__."""
    # Don't use "in" because that would mean the elements must be hashable,
    # which we don't want to require. This means we have to loop over every element,
    # every time.

    # We also can't use a dict mapping elements to ints for the same reason; instead
    # we can store this information as a list of elements, where the index corresponds
    # to the integer representation.

    iseqs = []
    rep = []

    for seq in seqs:
        iseq = []
        for element in seq:
            for idx, rep_element in enumerate(rep):
                if element == rep_element:
                    iseq.append(idx)
                    break
            else:
                iseq.append(len(rep))
                rep.append(element)

        iseqs.append(iseq)

    return iseqs
