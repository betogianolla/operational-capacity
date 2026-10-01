"""Projeções e CSVs reutilizáveis pela interface, sem dependência de Streamlit."""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from io import StringIO
from typing import Iterable

from .calculations import CapacityInputs, CapacityResults, calculate_capacity
from .queries import MonthlyCapacityAnalysis
from .synthetic_data import SYNTHETIC_LABEL


@dataclass(frozen=True)
class GrowthProjection:
    """Resultado anual de um cenário composto, mantendo premissas não-base constantes."""

    year_offset: int
    active_customers: float
    capacity: CapacityResults
    people_deficit: int
    utilization_exceeds_target: bool


def project_compound_growth(
    inputs: CapacityInputs, annual_growth_fraction: float, years: int = 3
) -> list[GrowthProjection]:
    """Projeta ano-base e anos futuros com crescimento composto da base."""

    if annual_growth_fraction < 0:
        raise ValueError("annual_growth_fraction deve ser maior ou igual a zero.")
    if years < 0:
        raise ValueError("years deve ser maior ou igual a zero.")

    projections: list[GrowthProjection] = []
    for year_offset in range(years + 1):
        projected_inputs = replace(
            inputs, base_units=inputs.base_units * (1 + annual_growth_fraction) ** year_offset
        )
        capacity = calculate_capacity(projected_inputs)
        projections.append(
            GrowthProjection(
                year_offset=year_offset,
                active_customers=projected_inputs.base_units,
                capacity=capacity,
                people_deficit=max(0, capacity.automated_required_people - inputs.team_members),
                utilization_exceeds_target=(
                    capacity.automated_effective_utilization_fraction
                    > inputs.target_utilization_fraction
                ),
            )
        )
    return projections


def historical_consolidation_csv(analyses: Iterable[MonthlyCapacityAnalysis]) -> bytes:
    """Serializa o histórico consolidado com origem e unidades explícitas."""

    headers = [
        "data_origin",
        "month",
        "active_customers",
        "total_interactions_per_month",
        "interactions_per_active_customer_per_month",
        "eligible_interaction_fraction",
        "automated_interaction_fraction",
        "observed_human_hours_per_month",
        "manual_counterfactual_hours_per_month",
        "automated_effective_utilization_fraction",
        "target_utilization_fraction",
        "team_members",
        "available_hours_per_person_per_month",
        "manual_minutes_source",
        "residual_minutes_source",
        "rework_fraction_source",
        "rework_additional_minutes_source",
        "methodology_note",
    ]
    rows = []
    for analysis in analyses:
        source = analysis.model_input_sources
        consolidation = analysis.consolidation
        capacity = analysis.capacity
        rows.append(
            {
                "data_origin": SYNTHETIC_LABEL,
                "month": consolidation.month,
                "active_customers": consolidation.active_customers,
                "total_interactions_per_month": consolidation.total_interactions,
                "interactions_per_active_customer_per_month": consolidation.interactions_per_active_customer,
                "eligible_interaction_fraction": consolidation.eligible_interaction_fraction,
                "automated_interaction_fraction": consolidation.automated_interaction_fraction,
                "observed_human_hours_per_month": consolidation.total_human_hours_direct,
                "manual_counterfactual_hours_per_month": capacity.manual_required_hours,
                "automated_effective_utilization_fraction": capacity.automated_effective_utilization_fraction,
                "target_utilization_fraction": consolidation.target_utilization_fraction,
                "team_members": consolidation.team_members,
                "available_hours_per_person_per_month": consolidation.available_hours_per_person_per_month,
                "manual_minutes_source": source["manual_minutes_per_interaction"],
                "residual_minutes_source": source["automated_residual_minutes_per_interaction"],
                "rework_fraction_source": source["automated_rework_fraction"],
                "rework_additional_minutes_source": source[
                    "rework_additional_minutes_per_interaction"
                ],
                "methodology_note": "Horas observadas são sintéticas; contrafactual manual é hipótese, não causalidade.",
            }
        )
    return _to_csv_bytes(headers, rows)


def projected_scenarios_csv(
    projections: Iterable[GrowthProjection],
    inputs: CapacityInputs,
    annual_growth_fraction: float,
) -> bytes:
    """Serializa projeções hipotéticas e todas as premissas necessárias para reproduzi-las."""

    headers = [
        "data_origin",
        "scenario_type",
        "year_offset",
        "annual_growth_fraction",
        "active_customers",
        "interactions_per_unit_per_month",
        "automation_fraction",
        "manual_minutes_per_interaction",
        "automated_residual_minutes_per_interaction",
        "automated_rework_fraction",
        "rework_additional_minutes_per_interaction",
        "team_members",
        "available_hours_per_person_per_month",
        "target_utilization_fraction",
        "demand_interactions_per_month",
        "automated_required_hours_per_month",
        "automated_required_people",
        "people_deficit",
        "automated_effective_utilization_fraction",
        "utilization_exceeds_target",
        "hypothesis_note",
    ]
    rows = []
    for projection in projections:
        capacity = projection.capacity
        rows.append(
            {
                "data_origin": SYNTHETIC_LABEL,
                "scenario_type": "HYPOTHETICAL_GROWTH_SCENARIO",
                "year_offset": projection.year_offset,
                "annual_growth_fraction": annual_growth_fraction,
                "active_customers": projection.active_customers,
                "interactions_per_unit_per_month": inputs.interactions_per_unit_per_month,
                "automation_fraction": inputs.automation_fraction,
                "manual_minutes_per_interaction": inputs.manual_minutes_per_interaction,
                "automated_residual_minutes_per_interaction": inputs.automated_residual_minutes_per_interaction,
                "automated_rework_fraction": inputs.automated_rework_fraction,
                "rework_additional_minutes_per_interaction": inputs.rework_additional_minutes_per_interaction,
                "team_members": inputs.team_members,
                "available_hours_per_person_per_month": inputs.available_hours_per_person_per_month,
                "target_utilization_fraction": inputs.target_utilization_fraction,
                "demand_interactions_per_month": capacity.monthly_demand_interactions,
                "automated_required_hours_per_month": capacity.automated_required_hours,
                "automated_required_people": capacity.automated_required_people,
                "people_deficit": projection.people_deficit,
                "automated_effective_utilization_fraction": capacity.automated_effective_utilization_fraction,
                "utilization_exceeds_target": projection.utilization_exceeds_target,
                "hypothesis_note": "Crescimento composto da base; demais premissas constantes; não é previsão validada.",
            }
        )
    return _to_csv_bytes(headers, rows)


def _to_csv_bytes(headers: list[str], rows: list[dict[str, object]]) -> bytes:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")
