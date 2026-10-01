from __future__ import annotations

from dataclasses import replace

import pytest

from operational_capacity import CapacityInputs, InputValidationError, calculate_capacity


@pytest.fixture
def reference_inputs() -> CapacityInputs:
    return CapacityInputs(
        base_units=10_000,
        interactions_per_unit_per_month=0.2,
        manual_minutes_per_interaction=30,
        automation_fraction=0.6,
        automated_residual_minutes_per_interaction=5,
        automated_rework_fraction=0.1,
        rework_additional_minutes_per_interaction=10,
        team_members=10,
        available_hours_per_person_per_month=160,
        target_utilization_fraction=0.8,
    )


def test_reference_case(reference_inputs: CapacityInputs) -> None:
    result = calculate_capacity(reference_inputs)

    assert result.monthly_demand_interactions == pytest.approx(2_000)
    assert result.automated_human_minutes_per_interaction == pytest.approx(15.6)
    assert result.manual_required_hours == pytest.approx(1_000)
    assert result.automated_required_hours == pytest.approx(520)
    assert result.released_human_hours == pytest.approx(480)
    assert result.planned_team_capacity_hours == pytest.approx(1_280)
    assert result.manual_effective_utilization_fraction == pytest.approx(0.625)
    assert result.automated_effective_utilization_fraction == pytest.approx(0.325)
    assert result.manual_required_people == 8
    assert result.automated_required_people == 5
    assert result.manual_sustainable_interactions_per_month == pytest.approx(2_560)
    assert result.automated_sustainable_interactions_per_month == pytest.approx(4_923.076923076923)
    assert result.capacity_change_fraction == pytest.approx(0.9230769230769231)
    assert result.manual_growth_margin_fraction == pytest.approx(0.28)
    assert result.automated_growth_margin_fraction == pytest.approx(1.4615384615384617)
    assert result.released_capacity_people_equivalent == pytest.approx(3.75)
    assert result.rounded_staffing_difference_people == 3
    assert result.not_applicable_reasons == {}


def test_initial_documented_case() -> None:
    result = calculate_capacity(
        CapacityInputs(
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
    )

    assert result.monthly_demand_interactions == pytest.approx(200)
    assert result.automated_human_minutes_per_interaction == pytest.approx(21.5)
    assert result.manual_required_hours == pytest.approx(100)
    assert result.automated_required_hours == pytest.approx(71.66666666666667)
    assert result.released_human_hours == pytest.approx(28.33333333333333)
    assert result.planned_team_capacity_hours == pytest.approx(128)
    assert result.manual_effective_utilization_fraction == pytest.approx(0.625)
    assert result.automated_effective_utilization_fraction == pytest.approx(0.4479166666666667)
    assert result.manual_required_people == 1
    assert result.automated_required_people == 1
    assert result.manual_sustainable_interactions_per_month == pytest.approx(256)
    assert result.automated_sustainable_interactions_per_month == pytest.approx(357.2093023255814)
    assert result.capacity_change_fraction == pytest.approx(0.39534883720930236)
    assert result.manual_growth_margin_fraction == pytest.approx(0.28)
    assert result.automated_growth_margin_fraction == pytest.approx(0.786046511627907)
    assert result.released_capacity_people_equivalent == pytest.approx(0.22135416666666663)


def test_zero_automation_matches_manual_process(reference_inputs: CapacityInputs) -> None:
    result = calculate_capacity(replace(reference_inputs, automation_fraction=0))

    assert result.automated_human_minutes_per_interaction == pytest.approx(
        result.manual_human_minutes_per_interaction
    )
    assert result.automated_required_hours == pytest.approx(result.manual_required_hours)
    assert result.automated_sustainable_interactions_per_month == pytest.approx(
        result.manual_sustainable_interactions_per_month
    )
    assert result.capacity_change_fraction == pytest.approx(0)
    assert result.released_human_hours == pytest.approx(0)


def test_full_automation_uses_residual_and_rework_time(reference_inputs: CapacityInputs) -> None:
    result = calculate_capacity(replace(reference_inputs, automation_fraction=1))

    assert result.automated_human_minutes_per_interaction == pytest.approx(6)
    assert result.automated_required_hours == pytest.approx(200)


@pytest.mark.parametrize(
    ("rework_fraction", "expected_minutes"),
    [(0, 5), (1, 15)],
)
def test_rework_fraction_boundaries(
    reference_inputs: CapacityInputs, rework_fraction: float, expected_minutes: float
) -> None:
    result = calculate_capacity(
        replace(reference_inputs, automation_fraction=1, automated_rework_fraction=rework_fraction)
    )

    assert result.automated_human_minutes_per_interaction == pytest.approx(expected_minutes)


def test_zero_demand_returns_zero_work_and_not_applicable_growth_margin(
    reference_inputs: CapacityInputs,
) -> None:
    result = calculate_capacity(replace(reference_inputs, base_units=0))

    assert result.monthly_demand_interactions == 0
    assert result.manual_required_hours == 0
    assert result.automated_required_hours == 0
    assert result.manual_required_people == 0
    assert result.automated_required_people == 0
    assert result.manual_growth_margin_fraction is None
    assert result.automated_growth_margin_fraction is None
    assert "demanda mensal é igual a zero" in result.not_applicable_reasons[
        "manual_growth_margin_fraction"
    ].lower()


def test_zero_human_time_marks_capacity_metrics_not_applicable(reference_inputs: CapacityInputs) -> None:
    result = calculate_capacity(
        replace(
            reference_inputs,
            manual_minutes_per_interaction=0,
            automation_fraction=1,
            automated_residual_minutes_per_interaction=0,
            automated_rework_fraction=0,
            rework_additional_minutes_per_interaction=0,
        )
    )

    assert result.manual_sustainable_interactions_per_month is None
    assert result.automated_sustainable_interactions_per_month is None
    assert result.capacity_change_interactions_per_month is None
    assert result.capacity_change_fraction is None
    assert "tempo humano médio é igual a zero" in result.not_applicable_reasons[
        "manual_sustainable_interactions_per_month"
    ].lower()


@pytest.mark.parametrize(
    "changes",
    [
        {"automation_fraction": -0.01},
        {"automation_fraction": 1.01},
        {"automated_rework_fraction": -0.01},
        {"automated_rework_fraction": 1.01},
        {"target_utilization_fraction": 0},
        {"target_utilization_fraction": 1.01},
        {"base_units": -1},
        {"interactions_per_unit_per_month": -0.1},
        {"manual_minutes_per_interaction": -1},
        {"automated_residual_minutes_per_interaction": -1},
        {"rework_additional_minutes_per_interaction": -1},
        {"team_members": 0},
        {"team_members": 1.5},
        {"available_hours_per_person_per_month": 0},
        {"available_hours_per_person_per_month": float("inf")},
    ],
)
def test_invalid_inputs_are_rejected(reference_inputs: CapacityInputs, changes: dict[str, float]) -> None:
    with pytest.raises(InputValidationError):
        calculate_capacity(replace(reference_inputs, **changes))


def test_automation_can_increase_human_work(reference_inputs: CapacityInputs) -> None:
    result = calculate_capacity(
        replace(
            reference_inputs,
            manual_minutes_per_interaction=10,
            automation_fraction=1,
            automated_residual_minutes_per_interaction=20,
            automated_rework_fraction=1,
            rework_additional_minutes_per_interaction=10,
        )
    )

    assert result.automated_human_minutes_per_interaction == pytest.approx(30)
    assert result.released_human_hours == pytest.approx(-666.6666666666666)
    assert result.capacity_change_fraction == pytest.approx(-0.6666666666666666)
    assert result.released_capacity_people_equivalent < 0


def test_demand_growth_scales_required_hours(reference_inputs: CapacityInputs) -> None:
    baseline = calculate_capacity(reference_inputs)
    doubled_demand = calculate_capacity(replace(reference_inputs, base_units=20_000))

    assert doubled_demand.monthly_demand_interactions == pytest.approx(
        baseline.monthly_demand_interactions * 2
    )
    assert doubled_demand.manual_required_hours == pytest.approx(baseline.manual_required_hours * 2)
    assert doubled_demand.automated_required_hours == pytest.approx(
        baseline.automated_required_hours * 2
    )
