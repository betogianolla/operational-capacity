from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_app_loads_with_two_tabs_and_synthetic_warning() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run(timeout=30)

    assert not app.exception
    assert len(app.tabs) == 2
    assert app.selectbox(key="history_month").value == "2025-12-01"
    assert any("dados sintéticos" in caption.value.lower() for caption in app.caption)


def test_app_requires_explicit_eligibility_expansion() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run(timeout=30)
    app.selectbox(key="history_month").set_value("2024-01-01").run(timeout=30)
    app.button(key="load_premises").click().run(timeout=30)
    assert app.number_input(key="sim_base").value == 8238
    assert app.number_input(key="sim_demand_rate").value == pytest.approx(1762 / 8238)
    automation = app.number_input(key="sim_automation_pct")
    automation.set_value(100).run(timeout=30)

    assert any("excede a elegibilidade" in warning.value.lower() for warning in app.warning)
    confirmation = app.checkbox(key="eligibility_expansion")
    confirmation.set_value(True).run(timeout=30)
    assert any("cenário hipotético" in info.value.lower() for info in app.info)


def test_changing_reference_month_preserves_edits_until_explicit_load() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run(timeout=30)
    app.number_input(key="sim_base").set_value(9999).run(timeout=30)
    app.selectbox(key="history_month").set_value("2024-01-01").run(timeout=30)

    assert app.number_input(key="sim_base").value == 9999
    assert any("nenhuma alteração foi sobrescrita" in info.value.lower() for info in app.info)
    app.button(key="restore_premises").click().run(timeout=30)
    assert app.number_input(key="sim_base").value != 9999
