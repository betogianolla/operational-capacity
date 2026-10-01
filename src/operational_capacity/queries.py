"""Consultas DuckDB e integração mensal com o motor de capacidade."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import duckdb

from .calculations import CapacityInputs, CapacityResults, calculate_capacity


@dataclass(frozen=True)
class MonthlyConsolidation:
    month: str
    active_customers: int
    team_members: int
    available_hours_per_person_per_month: float
    target_utilization_fraction: float
    manual_minutes_assumption: float
    automated_residual_minutes_assumption: float
    automated_rework_fraction_assumption: float
    rework_additional_minutes_assumption: float
    total_interactions: int
    interactions_per_active_customer: float
    eligible_interactions: int
    eligible_interaction_fraction: float
    automated_interactions: int
    automated_interaction_fraction: float
    average_manual_minutes: float | None
    average_automated_residual_minutes: float | None
    automated_rework_fraction: float | None
    average_rework_additional_minutes: float | None
    total_human_hours_direct: float


@dataclass(frozen=True)
class MonthlyCapacityAnalysis:
    consolidation: MonthlyConsolidation
    capacity: CapacityResults
    model_input_sources: Mapping[str, str]


MONTHLY_CONSOLIDATION_SQL = """
WITH interaction_stats AS (
    SELECT
        month,
        COUNT(interaction_id) AS total_interactions,
        COUNT(interaction_id) FILTER (WHERE automation_eligible) AS eligible_interactions,
        COUNT(interaction_id) FILTER (WHERE process = 'automated') AS automated_interactions,
        AVG(manual_minutes) FILTER (WHERE process = 'manual') AS average_manual_minutes,
        AVG(residual_minutes) FILTER (WHERE process = 'automated') AS average_automated_residual_minutes,
        AVG(CASE WHEN process = 'automated' THEN CAST(requires_rework AS INTEGER) END)
            AS automated_rework_fraction,
        AVG(rework_additional_minutes)
            FILTER (WHERE process = 'automated' AND requires_rework) AS average_rework_additional_minutes,
        SUM(human_minutes_actual) AS total_human_minutes_direct
    FROM interactions
    GROUP BY month
)
SELECT
    CAST(m.month AS VARCHAR) AS month,
    CAST(m.active_customers AS BIGINT) AS active_customers,
    CAST(m.team_members AS BIGINT) AS team_members,
    CAST(m.available_hours_per_person_per_month AS DOUBLE) AS available_hours_per_person_per_month,
    CAST(m.target_utilization_fraction AS DOUBLE) AS target_utilization_fraction,
    CAST(m.manual_minutes_assumption AS DOUBLE) AS manual_minutes_assumption,
    CAST(m.automated_residual_minutes_assumption AS DOUBLE) AS automated_residual_minutes_assumption,
    CAST(m.automated_rework_fraction_assumption AS DOUBLE) AS automated_rework_fraction_assumption,
    CAST(m.rework_additional_minutes_assumption AS DOUBLE) AS rework_additional_minutes_assumption,
    COALESCE(s.total_interactions, 0)::BIGINT AS total_interactions,
    COALESCE(s.total_interactions, 0)::DOUBLE / NULLIF(m.active_customers, 0)
        AS interactions_per_active_customer,
    COALESCE(s.eligible_interactions, 0)::BIGINT AS eligible_interactions,
    COALESCE(s.eligible_interactions, 0)::DOUBLE / NULLIF(COALESCE(s.total_interactions, 0), 0)
        AS eligible_interaction_fraction,
    COALESCE(s.automated_interactions, 0)::BIGINT AS automated_interactions,
    COALESCE(s.automated_interactions, 0)::DOUBLE / NULLIF(COALESCE(s.total_interactions, 0), 0)
        AS automated_interaction_fraction,
    s.average_manual_minutes,
    s.average_automated_residual_minutes,
    s.automated_rework_fraction,
    s.average_rework_additional_minutes,
    COALESCE(s.total_human_minutes_direct, 0) / 60.0 AS total_human_hours_direct
FROM monthly_capacity AS m
LEFT JOIN interaction_stats AS s ON m.month = s.month
ORDER BY m.month
"""


def load_monthly_consolidation(
    monthly_capacity_path: Path, interactions_path: Path
) -> list[MonthlyConsolidation]:
    """Agrega os CSVs sintéticos por mês usando DuckDB local em memória."""

    with duckdb.connect(":memory:") as connection:
        _create_csv_view(connection, "monthly_capacity", monthly_capacity_path)
        _create_csv_view(connection, "interactions", interactions_path)
        cursor = connection.execute(MONTHLY_CONSOLIDATION_SQL)
        columns = [column[0] for column in cursor.description]
        return [MonthlyConsolidation(**dict(zip(columns, row, strict=True))) for row in cursor.fetchall()]


def analyze_monthly_capacity(
    monthly_capacity_path: Path, interactions_path: Path
) -> list[MonthlyCapacityAnalysis]:
    """Calcula indicadores mensais e confere o motor contra os tempos agregados."""

    analyses: list[MonthlyCapacityAnalysis] = []
    for consolidation in load_monthly_consolidation(monthly_capacity_path, interactions_path):
        manual_minutes, manual_source = _value_or_assumption(
            consolidation.average_manual_minutes,
            consolidation.manual_minutes_assumption,
            "média manual observada",
            "premissa manual sintética explícita",
        )
        residual_minutes, residual_source = _value_or_assumption(
            consolidation.average_automated_residual_minutes,
            consolidation.automated_residual_minutes_assumption,
            "média residual observada",
            "premissa residual sintética explícita (sem atendimentos automatizados)",
        )
        rework_fraction, rework_source = _value_or_assumption(
            consolidation.automated_rework_fraction,
            consolidation.automated_rework_fraction_assumption,
            "taxa de retrabalho observada",
            "premissa de retrabalho sintética explícita (sem atendimentos automatizados)",
        )
        rework_minutes, rework_minutes_source = _value_or_assumption(
            consolidation.average_rework_additional_minutes,
            consolidation.rework_additional_minutes_assumption,
            "média de retrabalho observada",
            "premissa de retrabalho sintética explícita (sem casos de retrabalho)",
        )
        capacity = calculate_capacity(
            CapacityInputs(
                base_units=consolidation.active_customers,
                interactions_per_unit_per_month=consolidation.interactions_per_active_customer,
                manual_minutes_per_interaction=manual_minutes,
                automation_fraction=consolidation.automated_interaction_fraction,
                automated_residual_minutes_per_interaction=residual_minutes,
                automated_rework_fraction=rework_fraction,
                rework_additional_minutes_per_interaction=rework_minutes,
                team_members=consolidation.team_members,
                available_hours_per_person_per_month=consolidation.available_hours_per_person_per_month,
                target_utilization_fraction=consolidation.target_utilization_fraction,
            )
        )
        analyses.append(
            MonthlyCapacityAnalysis(
                consolidation=consolidation,
                capacity=capacity,
                model_input_sources={
                    "manual_minutes_per_interaction": manual_source,
                    "automated_residual_minutes_per_interaction": residual_source,
                    "automated_rework_fraction": rework_source,
                    "rework_additional_minutes_per_interaction": rework_minutes_source,
                },
            )
        )
    return analyses


def _create_csv_view(connection: duckdb.DuckDBPyConnection, name: str, path: Path) -> None:
    escaped_path = path.resolve().as_posix().replace("'", "''")
    connection.execute(
        f"CREATE VIEW {name} AS SELECT * FROM read_csv_auto('{escaped_path}', header = true)"
    )


def _value_or_assumption(
    observed_value: float | None,
    assumption: float,
    observed_label: str,
    assumption_label: str,
) -> tuple[float, str]:
    if observed_value is None:
        return assumption, assumption_label
    return observed_value, observed_label


def main() -> None:
    parser = argparse.ArgumentParser(description="Consolida dados sintéticos com DuckDB.")
    parser.add_argument("--monthly-path", type=Path, default=Path("data/monthly_capacity.csv"))
    parser.add_argument("--interactions-path", type=Path, default=Path("data/interactions.csv"))
    arguments = parser.parse_args()
    analyses = analyze_monthly_capacity(arguments.monthly_path, arguments.interactions_path)
    for analysis in analyses[:3]:
        print(
            f"{analysis.consolidation.month}: "
            f"{analysis.consolidation.total_interactions} atendimentos, "
            f"{analysis.capacity.automated_required_hours:.2f} h humanas, "
            f"{analysis.consolidation.automated_interaction_fraction:.2%} automatizados"
        )


if __name__ == "__main__":
    main()
