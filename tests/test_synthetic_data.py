from __future__ import annotations

import csv

from operational_capacity.synthetic_data import SYNTHETIC_LABEL, generate_synthetic_history


def test_generation_is_reproducible_and_has_24_months(tmp_path) -> None:
    first = generate_synthetic_history(tmp_path / "first")
    second = generate_synthetic_history(tmp_path / "second")

    assert first.monthly_capacity_path.read_bytes() == second.monthly_capacity_path.read_bytes()
    assert first.interactions_path.read_bytes() == second.interactions_path.read_bytes()
    assert first.metadata_path.read_bytes() == second.metadata_path.read_bytes()

    with first.monthly_capacity_path.open(encoding="utf-8", newline="") as file:
        monthly_rows = list(csv.DictReader(file))
    assert len(monthly_rows) == 24
    assert {row["synthetic_data_label"] for row in monthly_rows} == {SYNTHETIC_LABEL}


def test_generated_interactions_have_integrity_and_valid_relationships(tmp_path) -> None:
    paths = generate_synthetic_history(tmp_path / "data")
    with paths.monthly_capacity_path.open(encoding="utf-8", newline="") as file:
        months = {row["month"] for row in csv.DictReader(file)}
    with paths.interactions_path.open(encoding="utf-8", newline="") as file:
        interactions = list(csv.DictReader(file))

    identifiers = [row["interaction_id"] for row in interactions]
    assert len(identifiers) == len(set(identifiers))
    assert interactions
    for row in interactions:
        assert row["month"] in months
        assert row["synthetic_data_label"] == SYNTHETIC_LABEL
        assert row["interaction_id"]
        assert row["interaction_date"]
        assert float(row["manual_minutes"]) >= 0
        assert float(row["human_minutes_actual"]) >= 0
        if row["process"] == "automated":
            assert row["automation_eligible"] == "True"
            assert float(row["residual_minutes"]) >= 0
        else:
            assert row["requires_rework"] == "False"
            assert row["residual_minutes"] == ""
            assert row["rework_additional_minutes"] == ""
        if row["requires_rework"] == "True":
            assert row["process"] == "automated"
            assert float(row["rework_additional_minutes"]) >= 0
