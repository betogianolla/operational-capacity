"""Interface Streamlit do Simulador de Capacidade Operacional."""
from __future__ import annotations

import sys
from math import isclose
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

import altair as alt
import pandas as pd
import streamlit as st

from operational_capacity.calculations import CapacityInputs, InputValidationError, calculate_capacity
from operational_capacity.queries import MonthlyCapacityAnalysis, analyze_monthly_capacity
from operational_capacity.reporting import historical_consolidation_csv, project_compound_growth, projected_scenarios_csv

DATA_DIRECTORY = PROJECT_ROOT / "data"
MONTHLY_DATA_PATH = DATA_DIRECTORY / "monthly_capacity.csv"
INTERACTIONS_DATA_PATH = DATA_DIRECTORY / "interactions.csv"
SCENARIO_FIELDS = ("sim_base", "sim_demand_rate", "sim_manual_minutes", "sim_automation_pct", "sim_residual_minutes", "sim_rework_pct", "sim_rework_minutes", "sim_team", "sim_available_hours", "sim_target_pct")
MONTH_ABBREVIATIONS = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


def _number(value: float | None, suffix: str = "", decimals: int = 2) -> str:
    if value is None:
        return "Não aplicável"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".") + suffix


def _integer(value: float | int) -> str:
    return _number(float(value), decimals=0)


def _percentage(value: float | None, decimals: int = 1) -> str:
    return "Não aplicável" if value is None else f"{value * 100:.{decimals}f}%".replace(".", ",")


def _pp(value: float) -> str:
    return f"{value * 100:+.1f} p.p.".replace(".", ",")


def _month_label(month: str) -> str:
    return f"{MONTH_ABBREVIATIONS[int(month[5:7]) - 1]}/{month[2:4]}"


def _load_analyses() -> list[MonthlyCapacityAnalysis] | None:
    if not MONTHLY_DATA_PATH.exists() or not INTERACTIONS_DATA_PATH.exists():
        st.error("Os dados sintéticos ainda não foram gerados.")
        st.code("python src/operational_capacity/synthetic_data.py --output-dir data", language="bash")
        return None
    try:
        return analyze_monthly_capacity(MONTHLY_DATA_PATH, INTERACTIONS_DATA_PATH)
    except Exception as error:
        st.error("Não foi possível carregar os dados sintéticos para esta demonstração.")
        st.caption(f"Detalhe técnico: {error}")
        return None


def _premises(analysis: MonthlyCapacityAnalysis) -> dict[str, float | int]:
    c = analysis.consolidation
    return {
        "sim_base": int(c.active_customers), "sim_demand_rate": c.interactions_per_active_customer,
        "sim_manual_minutes": c.average_manual_minutes if c.average_manual_minutes is not None else c.manual_minutes_assumption,
        "sim_automation_pct": c.automated_interaction_fraction * 100,
        "sim_residual_minutes": c.average_automated_residual_minutes if c.average_automated_residual_minutes is not None else c.automated_residual_minutes_assumption,
        "sim_rework_pct": (c.automated_rework_fraction if c.automated_rework_fraction is not None else c.automated_rework_fraction_assumption) * 100,
        "sim_rework_minutes": c.average_rework_additional_minutes if c.average_rework_additional_minutes is not None else c.rework_additional_minutes_assumption,
        "sim_team": int(c.team_members), "sim_available_hours": c.available_hours_per_person_per_month,
        "sim_target_pct": c.target_utilization_fraction * 100,
    }


def _load_premises(analysis: MonthlyCapacityAnalysis) -> None:
    values = _premises(analysis)
    st.session_state.update(values)
    st.session_state["scenario_reference"] = values
    st.session_state["scenario_loaded_month"] = analysis.consolidation.month


def _scenario_edited() -> bool:
    reference = st.session_state.get("scenario_reference", {})
    return bool(reference) and any(not isclose(float(st.session_state.get(field, 0)), float(reference[field]), rel_tol=0, abs_tol=1e-10) for field in SCENARIO_FIELDS)


def _chart(data: pd.DataFrame, field: str, title: str, percentage: bool = False) -> alt.Chart:
    display = f"{field}_display"
    data = data.copy()
    data[display] = data[field].map(_percentage if percentage else lambda v: _number(v, decimals=0))
    label = "replace(format(datum.value, '.0%'), '.', ',')" if percentage else "replace(replace(replace(format(datum.value, ',.0f'), ',', 'X'), '.', ','), 'X', '.')"
    return alt.Chart(data).mark_line(color="#2c5f8a").encode(
        x=alt.X("Mês:N", axis=alt.Axis(title=None, tickCount=6, labelAngle=0)),
        y=alt.Y(f"{field}:Q", scale=alt.Scale(domainMin=0), axis=alt.Axis(title=None, tickCount=5, labelExpr=label)),
        tooltip=[alt.Tooltip("Mês:N"), alt.Tooltip(f"{display}:N", title=title)],
    ).properties(height=220)


def _history(analyses: list[MonthlyCapacityAnalysis], selected: MonthlyCapacityAnalysis) -> None:
    c, r = selected.consolidation, selected.capacity
    st.caption("⚠️ Dados sintéticos e fictícios — não representam empresa, operação ou impacto real.")
    st.subheader(f"Histórico — {_month_label(c.month)}")
    cards = st.columns(5)
    for card, label, value in zip(cards, ("Clientes ativos", "Atendimentos", "Automação realizada", "Horas humanas observadas", "Utilização efetiva"), (_integer(c.active_customers), _integer(c.total_interactions), _percentage(c.automated_interaction_fraction), _number(c.total_human_hours_direct, " h"), _percentage(r.automated_effective_utilization_fraction))):
        card.metric(label, value)
    delta = r.automated_effective_utilization_fraction - c.target_utilization_fraction
    st.caption(f"Utilização-alvo: {_percentage(c.target_utilization_fraction)} · diferença: {_pp(delta)}.")
    if delta > 0:
        st.warning("A utilização efetiva excede a utilização-alvo, mesmo que ainda esteja abaixo de 100%.")
    if r.automated_effective_utilization_fraction > 1:
        st.warning("As horas requeridas excedem as horas disponíveis. O modelo não calcula filas, atrasos ou prazos de atendimento.")
    data = pd.DataFrame({"Mês": [_month_label(x.consolidation.month) for x in analyses], "Atendimentos": [x.consolidation.total_interactions for x in analyses], "Horas humanas": [x.consolidation.total_human_hours_direct for x in analyses], "Automação": [x.consolidation.automated_interaction_fraction for x in analyses]})
    a, b, d = st.columns(3)
    a.caption("Demanda mensal"); a.altair_chart(_chart(data, "Atendimentos", "Atendimentos"), width="stretch")
    b.caption("Horas humanas mensais"); b.altair_chart(_chart(data, "Horas humanas", "Horas humanas"), width="stretch")
    d.caption("Adoção da automação"); d.altair_chart(_chart(data, "Automação", "Automação realizada", True), width="stretch")
    st.subheader("Trabalho observado e contrafactual manual")
    observed, counterfactual, difference = st.columns(3)
    observed.metric("Horas observadas", _number(c.total_human_hours_direct, " h")); counterfactual.metric("Horas no contrafactual manual", _number(r.manual_required_hours, " h")); difference.metric("Diferença de horas", _number(r.released_human_hours, " h"))
    st.caption("Hipótese: o tempo manual médio também se aplicaria aos atendimentos automatizados; a comparação não demonstra causalidade ou ganho real.")
    fallback = {name: source for name, source in selected.model_input_sources.items() if "premissa" in source.lower()}
    if fallback:
        st.info("Algumas médias não tiveram observações neste mês; foram usadas premissas sintéticas explícitas.")
        st.json(fallback)
    st.download_button("Baixar histórico consolidado (CSV)", historical_consolidation_csv(analyses), "historico_capacidade_sintetico.csv", "text/csv", key="download_history")


def _simulator(selected: MonthlyCapacityAnalysis) -> None:
    if "scenario_reference" not in st.session_state:
        _load_premises(selected)
    edited = _scenario_edited(); loaded = st.session_state["scenario_loaded_month"]
    if loaded != selected.consolidation.month:
        st.info(f"O cenário mantém premissas de {loaded}. O mês de referência mudou para {selected.consolidation.month}; nenhuma alteração foi sobrescrita.")
    buttons = st.columns([1, 1, 3])
    if buttons[0].button("Carregar premissas deste mês", key="load_premises"):
        _load_premises(selected); st.rerun()
    if edited and buttons[1].button("Restaurar premissas carregadas", key="restore_premises"):
        st.session_state.update(st.session_state["scenario_reference"]); st.rerun()
    buttons[2].caption("Cenário editado." if edited else f"Premissas carregadas de {loaded}.")
    st.subheader("Simulador de crescimento")
    demand, process, team = st.columns(3)
    with demand:
        st.markdown("#### Demanda")
        st.number_input("Clientes ativos", min_value=0, step=1, key="sim_base", help="Quantidade inteira de clientes atendidos no mês.")
        st.number_input("Atendimentos por cliente/mês", min_value=0.0, format="%.4f", key="sim_demand_rate", help="Frequência mensal média por cliente ativo.")
    with process:
        st.markdown("#### Processo e automação")
        st.number_input("Tempo manual por atendimento (min)", min_value=0.0, key="sim_manual_minutes", help="Tempo humano se o atendimento fosse manual.")
        st.number_input("Automação realizada (%)", min_value=0.0, max_value=100.0, key="sim_automation_pct", help="Percentual do total executado de forma automatizada.")
        st.number_input("Tempo residual automatizado (min)", min_value=0.0, key="sim_residual_minutes", help="Tempo humano restante em atendimento automatizado.")
        st.number_input("Retrabalho entre automatizados (%)", min_value=0.0, max_value=100.0, key="sim_rework_pct", help="Percentual automatizado com trabalho adicional.")
        st.number_input("Tempo adicional de retrabalho (min)", min_value=0.0, key="sim_rework_minutes", help="Acréscimo aplicado somente aos casos com retrabalho.")
    with team:
        st.markdown("#### Equipe e capacidade")
        st.number_input("Pessoas na equipe", min_value=1, step=1, key="sim_team", help="Quantidade inteira de pessoas disponíveis.")
        st.number_input("Horas disponíveis por pessoa/mês", min_value=0.1, key="sim_available_hours", help="Horas antes de aplicar a utilização-alvo.")
        st.number_input("Utilização-alvo (%)", min_value=0.1, max_value=100.0, key="sim_target_pct", help="Parcela planejada das horas disponíveis.")
    automation = st.session_state["sim_automation_pct"] / 100; eligibility = selected.consolidation.eligible_interaction_fraction
    st.caption(f"Elegibilidade observada: {_percentage(eligibility)}.")
    hypothetical = False
    if automation > eligibility + 1e-12:
        hypothetical = st.checkbox("Confirmo a hipótese de expansão da elegibilidade para exceder a observada.", key="eligibility_expansion")
        if not hypothetical:
            st.warning("A automação simulada excede a elegibilidade observada. Confirme a hipótese de expansão para calcular o cenário.")
            return
        st.info("Cenário hipotético: a elegibilidade foi expandida além do histórico observado.")
    try:
        inputs = CapacityInputs(int(st.session_state["sim_base"]), st.session_state["sim_demand_rate"], st.session_state["sim_manual_minutes"], automation, st.session_state["sim_residual_minutes"], st.session_state["sim_rework_pct"] / 100, st.session_state["sim_rework_minutes"], int(st.session_state["sim_team"]), st.session_state["sim_available_hours"], st.session_state["sim_target_pct"] / 100)
        r = calculate_capacity(inputs)
    except InputValidationError as error:
        st.error(f"Revise as premissas: {error}"); return
    st.subheader("Resumo do cenário")
    cards = st.columns(3); cards[0].metric("Demanda mensal", _integer(r.monthly_demand_interactions)); cards[1].metric("Pessoas disponíveis", _integer(inputs.team_members)); cards[2].metric("Pessoas necessárias", _integer(r.automated_required_people))
    if r.automated_effective_utilization_fraction > inputs.target_utilization_fraction:
        st.warning(f"A utilização automatizada ({_percentage(r.automated_effective_utilization_fraction)}) excede a utilização-alvo ({_percentage(inputs.target_utilization_fraction)}).")
    if r.automated_effective_utilization_fraction > 1:
        st.warning("As horas requeridas excedem as horas disponíveis. O modelo não calcula filas, atrasos ou prazos de atendimento.")
    st.subheader("Comparação de capacidade")
    table = pd.DataFrame({"Indicador": ["Horas necessárias/mês", "Utilização efetiva", "Pessoas necessárias (inteiro)", "Demanda máxima sustentável/mês", "Margem de crescimento sobre a demanda atual"], "Processo manual": [_number(r.manual_required_hours, " h"), _percentage(r.manual_effective_utilization_fraction), _integer(r.manual_required_people), _number(r.manual_sustainable_interactions_per_month, decimals=0), _percentage(r.manual_growth_margin_fraction)], "Processo automatizado": [_number(r.automated_required_hours, " h"), _percentage(r.automated_effective_utilization_fraction), _integer(r.automated_required_people), _number(r.automated_sustainable_interactions_per_month, decimals=0), _percentage(r.automated_growth_margin_fraction)]})
    st.dataframe(table, hide_index=True, width="stretch")
    summary = st.columns(4); summary[0].metric("Capacidade planejada", _number(r.planned_team_capacity_hours, " h/mês")); summary[1].metric("Aumento de capacidade", _percentage(r.capacity_change_fraction)); summary[2].metric("Horas humanas liberadas", _number(r.released_human_hours, " h/mês")); summary[3].metric("Capacidade liberada equivalente", _number(r.released_capacity_people_equivalent, " pessoas"))
    st.caption(f"Unidade: pessoas-equivalentes de capacidade planejada. Dimensionamento inteiro: manual {_integer(r.manual_required_people)}; automatizado {_integer(r.automated_required_people)}; diferença de {r.rounded_staffing_difference_people} pessoas. Não representa contratação, demissão ou economia realizada.")
    for field in ("manual_sustainable_interactions_per_month", "automated_sustainable_interactions_per_month", "capacity_change_fraction", "manual_growth_margin_fraction", "automated_growth_margin_fraction"):
        if getattr(r, field) is None: st.info(r.not_applicable_reasons.get(field, "Resultado não aplicável."))
    growth = st.number_input("Crescimento anual da base para projeção (%)", min_value=0.0, max_value=200.0, value=10.0, key="annual_growth", help="Crescimento composto aplicado somente aos clientes ativos.")
    projections = project_compound_growth(inputs, growth / 100, years=3)
    st.subheader("Projeção de três anos")
    st.caption("Crescimento composto somente da base; demais premissas constantes. Clientes são arredondados só para apresentação; os cálculos mantêm precisão interna. Não é previsão validada.")
    projection_table = pd.DataFrame([{ "Período": "Ano-base" if p.year_offset == 0 else f"Ano {p.year_offset}", "Clientes ativos": _integer(p.active_customers), "Demanda/mês": _integer(p.capacity.monthly_demand_interactions), "Horas necessárias/mês": _number(p.capacity.automated_required_hours, " h"), "Pessoas necessárias": _integer(p.capacity.automated_required_people), "Déficit de pessoas": _integer(p.people_deficit), "Utilização": _percentage(p.capacity.automated_effective_utilization_fraction), "Excede utilização-alvo": "Sim" if p.utilization_exceeds_target else "Não" } for p in projections])
    st.dataframe(projection_table, hide_index=True, width="stretch")
    st.download_button("Baixar cenários projetados (CSV)", projected_scenarios_csv(projections, inputs, growth / 100), "cenarios_crescimento_hipoteticos.csv", "text/csv", key=f"download_projection_{hypothetical}")


def main() -> None:
    st.set_page_config(page_title="Capacidade Operacional", page_icon="📈", layout="wide")
    st.title("Simulador de Capacidade Operacional")
    analyses = _load_analyses()
    if analyses is None: return
    months = [a.consolidation.month for a in analyses]
    selected_month = st.selectbox("Mês de referência", months, index=len(months) - 1, key="history_month", format_func=_month_label)
    selected = next(a for a in analyses if a.consolidation.month == selected_month)
    history, simulator = st.tabs(["Histórico da operação", "Simulador de crescimento"])
    with history: _history(analyses, selected)
    with simulator: _simulator(selected)
    with st.expander("Fórmulas, premissas e limites metodológicos"):
        st.markdown("O motor reutilizado calcula demanda, tempo humano, horas necessárias, capacidade planejada, utilização, pessoas necessárias e demanda máxima sustentável. A automação usa tempo residual mais o acréscimo esperado de retrabalho, sem dupla contagem.")
        st.markdown("O modelo mede capacidade humana e não inclui sistemas, orçamento, qualidade, filas ou prazos. Detalhes: `docs/briefing.md` e `docs/data.md`.")


if __name__ == "__main__": main()
