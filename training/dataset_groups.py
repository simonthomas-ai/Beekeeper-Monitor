"""Canonical five-group taxonomy for the 1,000-image research candidate set.

Species remain taxonomically distinct in every record. Groups are only a
balanced dataset-sampling and review presentation layer.
"""

GROUPS = {
    "asian_hornet": ("Vespa velutina",),
    "european_hornet": ("Vespa crabro",),
    "honey_bee": ("Apis mellifera",),
    "bumblebees": ("Bombus terrestris", "Bombus lapidarius"),
    "wasps": ("Vespula vulgaris", "Vespula germanica"),
}

GROUP_LABELS = {
    "asian_hornet": "Asiatische Hornisse",
    "european_hornet": "Europäische Hornisse",
    "honey_bee": "Honigbiene",
    "bumblebees": "Hummeln",
    "wasps": "Wespen",
}

SPECIES_TO_GROUP = {
    species: group
    for group, species_names in GROUPS.items()
    for species in species_names
}
SPECIES = tuple(species for members in GROUPS.values() for species in members)


def balanced_quotas(total: int, groups=GROUPS) -> dict[str, int]:
    """Distribute a total evenly across groups in stable declared order."""
    if type(total) is not int or total < 0:
        raise ValueError("total must be a non-negative integer")
    names = tuple(groups)
    if not names:
        raise ValueError("at least one group is required")
    base, remainder = divmod(total, len(names))
    return {name: base + (index < remainder) for index, name in enumerate(names)}


def balanced_taxon_quotas(group: str, total: int) -> dict[str, int]:
    """Distribute one group's target evenly across its scientific taxa."""
    if group not in GROUPS:
        raise ValueError("unknown dataset group")
    names = GROUPS[group]
    base, remainder = divmod(total, len(names))
    return {name: base + (index < remainder) for index, name in enumerate(names)}


def group_for_species(species: str) -> str:
    try:
        return SPECIES_TO_GROUP[species]
    except KeyError as exc:
        raise ValueError(f"species is not part of the five-group dataset: {species}") from exc
