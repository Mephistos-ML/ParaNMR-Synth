from paranmr_synth.core.sampling import sample_diamagnetic_shifts


def test_diamagnetic_sampling_is_seeded_and_order_independent():
    first = sample_diamagnetic_shifts(
        atom_labels=("H3", "H1", "H2"),
        geometry_checksum="geometry-a",
        seed=42,
        range_min_ppm=0.0,
        range_max_ppm=10.0,
    )
    reordered = sample_diamagnetic_shifts(
        atom_labels=("H2", "H3", "H1"),
        geometry_checksum="geometry-a",
        seed=42,
        range_min_ppm=0.0,
        range_max_ppm=10.0,
    )
    changed_seed = sample_diamagnetic_shifts(
        atom_labels=("H1", "H2", "H3"),
        geometry_checksum="geometry-a",
        seed=43,
        range_min_ppm=0.0,
        range_max_ppm=10.0,
    )

    assert first == reordered
    assert first != changed_seed
    assert all(0.0 <= value <= 10.0 for value in first.values())


def test_diamagnetic_sampling_uses_geometry_identity():
    first = sample_diamagnetic_shifts(
        atom_labels=("H1",),
        geometry_checksum="geometry-a",
        seed=42,
        range_min_ppm=0.0,
        range_max_ppm=10.0,
    )
    second = sample_diamagnetic_shifts(
        atom_labels=("H1",),
        geometry_checksum="geometry-b",
        seed=42,
        range_min_ppm=0.0,
        range_max_ppm=10.0,
    )

    assert first != second
