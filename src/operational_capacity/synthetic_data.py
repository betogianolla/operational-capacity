"""Geração determinística de histórico operacional estritamente fictício."""

from __future__ import annotations

import argparse
import csv
import json
from calendar import monthrange
from dataclasses import asdict, dataclass
from datetime import date
from math import sin
from pathlib import Path
from random import Random


SYNTHETIC_LABEL = "SYNTHETIC_FICTITIOUS"


@dataclass(frozen=True)
class SyntheticHistoryConfig:
    """Configuração fixa que torna os arquivos reproduzíveis."""

    seed: int = 20_260_930
    start_month: date = date(2024, 1, 1)
    month_count: int = 24


@dataclass(frozen=True)
class SyntheticDataPaths:
    monthly_capacity_path: Path
    interactions_path: Path
    metadata_path: Path


MONTHLY_COLUMNS = (
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
)

INTERACTION_COLUMNS = (
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
)


def generate_synthetic_history(
    output_directory: Path, config: SyntheticHistoryConfig = SyntheticHistoryConfig()
) -> SyntheticDataPaths:
    """Gera 24 meses de CSVs fictícios sem datas de geração variáveis.

    A primeira competência mensal tem automação zero para fornecer um caso explícito
    sem automação e, portanto, sem retrabalho. O restante adota automação gradualmente.
    """

    if config.month_count <= 0:
        raise ValueError("month_count deve ser maior que zero.")

    output_directory.mkdir(parents=True, exist_ok=True)
    rng = Random(config.seed)
    monthly_rows: list[dict[str, object]] = []
    interaction_rows: list[dict[str, object]] = []

    for month_index in range(config.month_count):
        month = _add_months(config.start_month, month_index)
        active_customers = round(
            8_200 * (1.009**month_index) * (1 + 0.025 * sin(month_index * 0.8))
            + rng.randint(-80, 80)
        )
        demand_rate = 0.215 + 0.014 * sin(month_index * 0.9) + rng.uniform(-0.006, 0.006)
        interaction_count = round(active_customers * demand_rate)
        eligibility_probability = min(0.82, 0.62 + 0.006 * month_index + rng.uniform(-0.02, 0.02))
        adoption_probability = 0 if month_index == 0 else min(0.82, 0.08 + 0.034 * month_index)
        manual_minutes = 28 + (month_index % 4) * 1.5
        residual_assumption = 5.5
        rework_assumption = 0.10
        rework_additional_assumption = 10.0
        team_members = 9 + month_index // 8

        monthly_rows.append(
            {
                "month": month.isoformat(),
                "active_customers": active_customers,
                "team_members": team_members,
                "available_hours_per_person_per_month": 160,
                "target_utilization_fraction": 0.8,
                "manual_minutes_assumption": manual_minutes,
                "automated_residual_minutes_assumption": residual_assumption,
                "automated_rework_fraction_assumption": rework_assumption,
                "rework_additional_minutes_assumption": rework_additional_assumption,
                "synthetic_data_label": SYNTHETIC_LABEL,
            }
        )

        for interaction_number in range(1, interaction_count + 1):
            eligible = rng.random() < eligibility_probability
            automated = eligible and rng.random() < adoption_probability
            day = rng.randint(1, monthrange(month.year, month.month)[1])
            interaction_date = date(month.year, month.month, day)
            residual_minutes: float | None = None
            rework_additional_minutes: float | None = None
            requires_rework = False

            if automated:
                residual_minutes = round(rng.uniform(4.0, 7.0), 2)
                requires_rework = rng.random() < rework_assumption
                if requires_rework:
                    rework_additional_minutes = round(rng.uniform(7.0, 13.0), 2)
                human_minutes_actual = residual_minutes + (rework_additional_minutes or 0)
                process = "automated"
            else:
                human_minutes_actual = manual_minutes
                process = "manual"

            interaction_rows.append(
                {
                    "interaction_id": f"SYN-{month:%Y%m}-{interaction_number:06d}",
                    "month": month.isoformat(),
                    "interaction_date": interaction_date.isoformat(),
                    "process": process,
                    "automation_eligible": eligible,
                    "manual_minutes": manual_minutes,
                    "human_minutes_actual": human_minutes_actual,
                    "residual_minutes": residual_minutes,
                    "requires_rework": requires_rework,
                    "rework_additional_minutes": rework_additional_minutes,
                    "synthetic_data_label": SYNTHETIC_LABEL,
                }
            )

    monthly_path = output_directory / "monthly_capacity.csv"
    interactions_path = output_directory / "interactions.csv"
    metadata_path = output_directory / "synthetic_data_metadata.json"
    _write_csv(monthly_path, MONTHLY_COLUMNS, monthly_rows)
    _write_csv(interactions_path, INTERACTION_COLUMNS, interaction_rows)
    metadata_path.write_text(
        json.dumps(
            {
                "data_label": SYNTHETIC_LABEL,
                "description": "Dados integralmente fictícios para demonstração de capacidade humana.",
                "seed": config.seed,
                "start_month": config.start_month.isoformat(),
                "month_count": config.month_count,
                "configuration": {**asdict(config), "start_month": config.start_month.isoformat()},
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return SyntheticDataPaths(monthly_path, interactions_path, metadata_path)


def _add_months(start_month: date, offset: int) -> date:
    month_number = start_month.month - 1 + offset
    return date(start_month.year + month_number // 12, month_number % 12 + 1, 1)


def _write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera dados operacionais sintéticos e fictícios.")
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    arguments = parser.parse_args()
    paths = generate_synthetic_history(arguments.output_dir)
    print(f"Dados sintéticos gerados: {paths.monthly_capacity_path}")
    print(f"Atendimentos sintéticos gerados: {paths.interactions_path}")


if __name__ == "__main__":
    main()
