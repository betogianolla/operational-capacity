from __future__ import annotations

import csv
from io import StringIO

import pytest

from operational_capacity.calculations import CapacityInputs
from operational_capacity.queries import analyze_monthly_capacity
from operational_capacity.reporting import (
    historical_consolidation_csv,
    project_compound_growth,
    projected_scenarios_csv,
)
from operational_capacity.synthetic_data import generate_synthetic_history


def _inputs() -> CapacityInputs:
    return CapacityInputs(
        base_units=100,
        interactions_per_unit_per_month=2,
        manual_minutes_per_interaction=30,
        automation_fraction=0.5,
        automated_residual_minutes_per_interaction=10,
        automated_rework_fraction=0.2,
        rework_additional_minutes_per_interaction=15,
        team_members=1,
        available_hours_per_person_per_month=160,
        target_utilization_fraction=0.8,
    )


def test_compound_projection_keeps_other_inputs_constant() -> None:
    projections = project_compound_growth(_inputs(), annual_growth_fraction=0.10, years=3)

    assert [projection.year_offset for projection in projections] == [0, 1, 2, 3]
    assert projections[0].active_customers == pytest.approx(100)
    assert projections[3].active_customers == pytest.approx(133.1)
    assert projections[3].capacity.monthly_demand_interactions == pytest.approx(266.2)
    assert projections[3].capacity.automated_required_hours == pytest.approx(
        projections[0].capacity.automated_required_hours * 1.331
    )


def test_projected_csv_includes_premises_and_hypothesis() -> None:
    inputs = _inputs()
    content = projected_scenarios_csv(project_compound_growth(inputs, 0.1), inputs, 0.1)
    rows = list(csv.DictReader(StringIO(content.decode("utf-8"))))

    assert len(rows) == 4
    assert rows[0]["data_origin"] == "SYNTHETIC_FICTITIOUS"
    assert rows[0]["scenario_type"] == "HYPOTHETICAL_GROWTH_SCENARIO"
    assert rows[3]["active_customers"] == "133.10000000000005"
    assert "demais premissas constantes" in rows[0]["hypothesis_note"]


def test_historical_csv_identifies_synthetic_origin_and_units(tmp_path) -> None:
    paths = generate_synthetic_history(tmp_path / "data")
    analyses = analyze_monthly_capacity(paths.monthly_capacity_path, paths.interactions_path)
    rows = list(csv.DictReader(StringIO(historical_consolidation_csv(analyses).decode("utf-8"))))

    assert len(rows) == 24
    assert rows[0]["data_origin"] == "SYNTHETIC_FICTITIOUS"
    assert "observed_human_hours_per_month" in rows[0]
    assert "contrafactual manual" in rows[0]["methodology_note"]
