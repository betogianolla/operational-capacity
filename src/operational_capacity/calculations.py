"""Cálculos puros de capacidade operacional.

As frações retornadas usam a escala de 0 a 1. A camada de apresentação é responsável
por convertê-las para percentuais e por qualquer arredondamento visual.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from types import MappingProxyType
from typing import Mapping


class InputValidationError(ValueError):
    """Indica que uma premissa de capacidade está fora dos limites permitidos."""


@dataclass(frozen=True)
class CapacityInputs:
    """Premissas mensais do modelo, com unidades explícitas nos nomes dos campos."""

    base_units: float
    interactions_per_unit_per_month: float
    manual_minutes_per_interaction: float
    automation_fraction: float
    automated_residual_minutes_per_interaction: float
    automated_rework_fraction: float
    rework_additional_minutes_per_interaction: float
    team_members: int
    available_hours_per_person_per_month: float
    target_utilization_fraction: float


@dataclass(frozen=True)
class CapacityResults:
    """Resultados mensais sem arredondamento de apresentação.

    Campos opcionais são ``None`` quando a métrica não é operacionalmente aplicável.
    O motivo correspondente está em ``not_applicable_reasons``.
    """

    monthly_demand_interactions: float
    manual_human_minutes_per_interaction: float
    automated_human_minutes_per_interaction: float
    manual_required_hours: float
    automated_required_hours: float
    released_human_hours: float
    planned_team_capacity_hours: float
    manual_effective_utilization_fraction: float
    automated_effective_utilization_fraction: float
    manual_required_people: int
    automated_required_people: int
    manual_sustainable_interactions_per_month: float | None
    automated_sustainable_interactions_per_month: float | None
    capacity_change_interactions_per_month: float | None
    capacity_change_fraction: float | None
    manual_growth_margin_fraction: float | None
    automated_growth_margin_fraction: float | None
    released_capacity_people_equivalent: float
    rounded_staffing_difference_people: int
    not_applicable_reasons: Mapping[str, str]


_ZERO_TIME_REASON = (
    "Tempo humano médio é igual a zero; capacidade sustentável não é um resultado "
    "operacional aplicável."
)
_ZERO_DEMAND_REASON = "Demanda mensal é igual a zero; margem de crescimento percentual não é aplicável."
_CAPACITY_CHANGE_REASON = (
    "Variação de capacidade não é aplicável porque a capacidade sustentável manual "
    "ou automatizada não é aplicável."
)


def calculate_capacity(inputs: CapacityInputs) -> CapacityResults:
    """Calcula capacidade humana mensal para processos manual e automatizado.

    Não arredonda valores intermediários. O retrabalho é acrescentado apenas ao tempo
    residual dos atendimentos automatizados, evitando dupla contagem.
    """

    _validate_inputs(inputs)

    demand = inputs.base_units * inputs.interactions_per_unit_per_month
    manual_minutes = inputs.manual_minutes_per_interaction
    automated_minutes = (
        (1 - inputs.automation_fraction) * manual_minutes
        + inputs.automation_fraction
        * (
            inputs.automated_residual_minutes_per_interaction
            + inputs.automated_rework_fraction * inputs.rework_additional_minutes_per_interaction
        )
    )

    manual_required_hours = demand * manual_minutes / 60
    automated_required_hours = demand * automated_minutes / 60
    released_human_hours = manual_required_hours - automated_required_hours

    raw_team_hours = inputs.team_members * inputs.available_hours_per_person_per_month
    planned_team_capacity_hours = raw_team_hours * inputs.target_utilization_fraction
    manual_utilization = manual_required_hours / raw_team_hours
    automated_utilization = automated_required_hours / raw_team_hours
    hours_per_planned_person = (
        inputs.available_hours_per_person_per_month * inputs.target_utilization_fraction
    )
    manual_required_people = ceil(manual_required_hours / hours_per_planned_person)
    automated_required_people = ceil(automated_required_hours / hours_per_planned_person)

    reasons: dict[str, str] = {}
    manual_sustainable = _sustainable_demand(
        planned_team_capacity_hours,
        manual_minutes,
        "manual_sustainable_interactions_per_month",
        reasons,
    )
    automated_sustainable = _sustainable_demand(
        planned_team_capacity_hours,
        automated_minutes,
        "automated_sustainable_interactions_per_month",
        reasons,
    )

    capacity_change, capacity_change_fraction = _capacity_change(
        manual_sustainable, automated_sustainable, reasons
    )
    manual_margin = _growth_margin(
        manual_sustainable, demand, "manual_growth_margin_fraction", reasons
    )
    automated_margin = _growth_margin(
        automated_sustainable, demand, "automated_growth_margin_fraction", reasons
    )

    return CapacityResults(
        monthly_demand_interactions=demand,
        manual_human_minutes_per_interaction=manual_minutes,
        automated_human_minutes_per_interaction=automated_minutes,
        manual_required_hours=manual_required_hours,
        automated_required_hours=automated_required_hours,
        released_human_hours=released_human_hours,
        planned_team_capacity_hours=planned_team_capacity_hours,
        manual_effective_utilization_fraction=manual_utilization,
        automated_effective_utilization_fraction=automated_utilization,
        manual_required_people=manual_required_people,
        automated_required_people=automated_required_people,
        manual_sustainable_interactions_per_month=manual_sustainable,
        automated_sustainable_interactions_per_month=automated_sustainable,
        capacity_change_interactions_per_month=capacity_change,
        capacity_change_fraction=capacity_change_fraction,
        manual_growth_margin_fraction=manual_margin,
        automated_growth_margin_fraction=automated_margin,
        released_capacity_people_equivalent=released_human_hours / hours_per_planned_person,
        rounded_staffing_difference_people=manual_required_people - automated_required_people,
        not_applicable_reasons=MappingProxyType(reasons),
    )


def _validate_inputs(inputs: CapacityInputs) -> None:
    _validate_non_negative("base_units", inputs.base_units)
    _validate_non_negative("interactions_per_unit_per_month", inputs.interactions_per_unit_per_month)
    _validate_non_negative("manual_minutes_per_interaction", inputs.manual_minutes_per_interaction)
    _validate_fraction("automation_fraction", inputs.automation_fraction, allow_zero=True)
    _validate_non_negative(
        "automated_residual_minutes_per_interaction",
        inputs.automated_residual_minutes_per_interaction,
    )
    _validate_fraction("automated_rework_fraction", inputs.automated_rework_fraction, allow_zero=True)
    _validate_non_negative(
        "rework_additional_minutes_per_interaction",
        inputs.rework_additional_minutes_per_interaction,
    )
    _validate_positive_integer("team_members", inputs.team_members)
    _validate_positive("available_hours_per_person_per_month", inputs.available_hours_per_person_per_month)
    _validate_fraction("target_utilization_fraction", inputs.target_utilization_fraction, allow_zero=False)


def _validate_non_negative(name: str, value: float) -> None:
    _validate_finite_number(name, value)
    if value < 0:
        raise InputValidationError(f"{name} deve ser maior ou igual a zero.")


def _validate_positive(name: str, value: float) -> None:
    _validate_finite_number(name, value)
    if value <= 0:
        raise InputValidationError(f"{name} deve ser maior que zero.")


def _validate_fraction(name: str, value: float, *, allow_zero: bool) -> None:
    _validate_finite_number(name, value)
    if value < 0 or value > 1 or (not allow_zero and value == 0):
        qualifier = "maior que zero e menor ou igual a um" if not allow_zero else "entre zero e um"
        raise InputValidationError(f"{name} deve estar {qualifier}.")


def _validate_positive_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise InputValidationError(f"{name} deve ser um inteiro maior que zero.")


def _validate_finite_number(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise InputValidationError(f"{name} deve ser um número finito.")


def _sustainable_demand(
    planned_team_capacity_hours: float,
    human_minutes_per_interaction: float,
    result_name: str,
    reasons: dict[str, str],
) -> float | None:
    if human_minutes_per_interaction == 0:
        reasons[result_name] = _ZERO_TIME_REASON
        return None
    return planned_team_capacity_hours * 60 / human_minutes_per_interaction


def _capacity_change(
    manual_sustainable: float | None,
    automated_sustainable: float | None,
    reasons: dict[str, str],
) -> tuple[float | None, float | None]:
    if manual_sustainable is None or automated_sustainable is None:
        reasons["capacity_change_interactions_per_month"] = _CAPACITY_CHANGE_REASON
        reasons["capacity_change_fraction"] = _CAPACITY_CHANGE_REASON
        return None, None
    if manual_sustainable == 0:
        reason = "Variação de capacidade não é aplicável porque a capacidade manual é igual a zero."
        reasons["capacity_change_fraction"] = reason
        return automated_sustainable - manual_sustainable, None
    change = automated_sustainable - manual_sustainable
    return change, change / manual_sustainable


def _growth_margin(
    sustainable_demand: float | None,
    current_demand: float,
    result_name: str,
    reasons: dict[str, str],
) -> float | None:
    if sustainable_demand is None:
        reasons[result_name] = _ZERO_TIME_REASON
        return None
    if current_demand == 0:
        reasons[result_name] = _ZERO_DEMAND_REASON
        return None
    return sustainable_demand / current_demand - 1
