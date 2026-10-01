from __future__ import annotations

import csv

import pytest

from operational_capacity.queries import analyze_monthly_capacity, load_monthly_consolidation
from operational_capacity.synthetic_data import generate_synthetic_history


def _write_known_csvs(tmp_path):
    monthly_path = tmp_path / "monthly_capacity.csv"
    interactions_path = tmp_path / "interactions.csv"
    monthly_columns = [
        "month",
        "active_customers",
        "team_members",
        "available_hours_per_person_per_month",
        "target_utilization_fraction",
        "manual_minutes_assumption",
        "automated_residual_minutes_assumption",
        "automated_rework_fraction_assumption",
        "rework_additional_minutes_assumption",
        "synthetic_data_label",
    ]
    interaction_columns = [
        "interaction_id",
        "month",
        "interaction_date",
        "process",
        "automation_eligible",
        "manual_minutes",
        "human_minutes_actual",
        "residual_minutes",
        "requires_rework",
        "rework_additional_minutes",
        "synthetic_data_label",
    ]
    with monthly_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=monthly_columns)
        writer.writeheader()
        writer.writerow(
            {
                "month": "2024-01-01",
                "active_customers": 10,
                "team_members": 2,
                "available_hours_per_person_per_month": 160,
                "target_utilization_fraction": 0.8,
                "manual_minutes_assumption": 10,
                "automated_residual_minutes_assumption": 4,
                "automated_rework_fraction_assumption": 0.5,
                "rework_additional_minutes_assumption": 6,
                "synthetic_data_label": "SYNTHETIC_FICTITIOUS",
            }
        )
    rows = [
        ("i-1", "manual", False, 10, 10, "", False, ""),
        ("i-2", "automated", True, 10, 4, 4, False, ""),
        ("i-3", "automated", True, 10, 10, 4, True, 6),
    ]
    with interactions_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=interaction_columns)
        writer.writeheader()
        for identifier, process, eligible, manual, actual, residual, rework, additional in rows:
            writer.writerow(
                {
                    "interaction_id": identifier,
                    "month": "2024-01-01",
                    "interaction_date": "2024-01-15",
                    "process": process,
                    "automation_eligible": eligible,
                    "manual_minutes": manual,
                    "human_minutes_actual": actual,
                    "residual_minutes": residual,
                    "requires_rework": rework,
                    "rework_additional_minutes": additional,
                    "synthetic_data_label": "SYNTHETIC_FICTITIOUS",
                }
            )
    return monthly_path, interactions_path


def test_sql_consolidation_matches_independent_known_values(tmp_path) -> None:
    monthly_path, interactions_path = _write_known_csvs(tmp_path)
    [result] = load_monthly_consolidation(monthly_path, interactions_path)

    assert result.total_interactions == 3
    assert result.interactions_per_active_customer == pytest.approx(0.3)
    assert result.eligible_interactions == 2
    assert result.eligible_interaction_fraction == pytest.approx(2 / 3)
    assert result.automated_interactions == 2
    assert result.automated_interaction_fraction == pytest.approx(2 / 3)
    assert result.average_manual_minutes == pytest.approx(10)
    assert result.average_automated_residual_minutes == pytest.approx(4)
    assert result.automated_rework_fraction == pytest.approx(0.5)
    assert result.average_rework_additional_minutes == pytest.approx(6)
    assert result.total_human_hours_direct == pytest.approx(0.4)

    [analysis] = analyze_monthly_capacity(monthly_path, interactions_path)
    assert analysis.capacity.automated_required_hours == pytest.approx(0.4)


def test_month_without_automation_keeps_automated_means_absent_and_uses_explicit_assumptions(tmp_path) -> None:
    paths = generate_synthetic_history(tmp_path / "data")
    consolidations = load_monthly_consolidation(paths.monthly_capacity_path, paths.interactions_path)
    analyses = analyze_monthly_capacity(paths.monthly_capacity_path, paths.interactions_path)
    first = consolidations[0]
    first_analysis = analyses[0]

    assert first.automated_interactions == 0
    assert first.average_automated_residual_minutes is None
    assert first.automated_rework_fraction is None
    assert first.average_rework_additional_minutes is None
    assert "premissa" in first_analysis.model_input_sources[
        "automated_residual_minutes_per_interaction"
    ]
    assert first_analysis.capacity.automated_required_hours == pytest.approx(
        first.total_human_hours_direct
    )


def test_engine_hours_match_direct_aggregation_for_generated_history(tmp_path) -> None:
    paths = generate_synthetic_history(tmp_path / "data")
    analyses = analyze_monthly_capacity(paths.monthly_capacity_path, paths.interactions_path)

    assert len(analyses) == 24
    for analysis in analyses:
        assert analysis.capacity.automated_required_hours == pytest.approx(
            analysis.consolidation.total_human_hours_direct,
            abs=1e-10,
        )
