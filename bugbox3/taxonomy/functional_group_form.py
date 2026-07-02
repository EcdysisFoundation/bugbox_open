"""convert functional-group checkbox form state to active traits."""

from __future__ import annotations

from bugbox3.taxonomy.functional_group_validation import infer_missing_parent_traits


def traits_from_checkboxes(checked: dict[str, bool]) -> dict[str, bool]:
    traits = {code: True for code, on in checked.items() if on}
    return infer_missing_parent_traits(traits)
