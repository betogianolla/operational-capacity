# Portfolio Case — Operational Capacity Simulator

[Leia em português](portfolio-case.md) · [README in English](../README.md) · [README em português](../README.pt-BR.md)

**Author and project lead: Roberto Gianolla Junior**

> “Project conceived and developed under the guidance of Roberto Gianolla Junior, responsible for directing the business problem, following deliveries, and refining the solution.”

## 1. Identified problem

Operations leadership needs to answer a recurring question before accepting more demand or investing in automation: **can the current team absorb growth, and how much human capacity can automation release?**

The challenge is not simply counting people. It is connecting the size of the served base, service frequency, human time per interaction, rework, and team availability without mistaking potential capacity for realized savings.

This case is fictitious. The data are deterministic, synthetic, and marked `SYNTHETIC_FICTITIOUS`; they do not represent a company, customer, or real operational impact.

## 2. Solution objective

Build a local decision-support tool that compares a manual process with a partially automated process, identifies team utilization, estimates required people, and explores three years of compounded growth.

The result is a **deterministic operational capacity model**. It is not causal inference, a validated statistical forecast, a queueing model, or an optimization algorithm.

## Author guidance and contribution

Roberto Gianolla Junior led the identification of the business problem and the direction of the solution. The documentation records choices that translate this guidance into verifiable deliverables:

- active customers were defined as the demonstrative base unit, without tying the case to a sector or company;
- the tool was bounded as human-capacity decision support, without converting released hours into financial savings or layoff/hiring recommendations;
- automation eligibility was separated from actual adoption, so a process limit is not treated as a realized result;
- work was conducted in stages with an independent calculation engine, reproducible data, SQL queries, interface, exports, and review;
- usability and presentation refinements were requested: pt-BR formatting, percentage-point differences, grouped inputs, utilization alerts, and preservation of edited scenarios when the reference month changes.

These records appear in the briefing, decisions, tasks, and interface documentation. This attribution does not claim a personal line-by-line code review, personal execution of every automated test, or fully manual authorship of the code.

## 3. Translating the problem into an analytical model

### Base, demand, and units

If `B` is the active-customer base and `f` is interactions per customer/month, monthly demand is:

`D = B × f`

`D` is measured in interactions/month. The formula makes the base effect proportional: holding frequency constant, 10% more customers means 10% more interactions. Historical frequency is a measured rate in the synthetic data; in the simulator it can be a selected assumption.

### Manual human time, residual time, and rework

For the manual process, mean human time is `t_manual`, in minutes/interaction. For the automated process, with actual adoption `a`, residual time `t_residual`, rework rate `r`, and additional rework time `t_rework`, the engine computes:

`t_auto = (1 − a) × t_manual + a × (t_residual + r × t_rework)`

The first term represents the still-manual share. The second represents the automated share, including expected rework. `r × t_rework` is an expected additional number of minutes per automated interaction; it does not require event independence. Rework is additional to residual time, avoiding double counting.

Eligibility is the share of interactions that **could** be automated. Actual adoption is the share that **was** automated and is the engine input `a`. If a scenario exceeds observed eligibility, the interface requires an explicit eligibility-expansion assumption.

### Workload, capacity, and utilization

For any mean human time `t`, monthly workload is:

`H = D × t / 60`

`H` is measured in hours/month; dividing by 60 converts minutes to hours. With `P` people, `h` available hours per person/month, and target utilization `u_target`, planned capacity is:

`C_plan = P × h × u_target`

Effective utilization uses all availability before the target:

`U_eff = H / (P × h)`

Effective utilization and target utilization are therefore distinct: the first describes workload relative to availability; the second is a planning decision used to reserve operating slack.

### People and sustainable demand

Estimated required people are:

`P_required = ceil(H / (h × u_target))`

Rounding up is necessary because people are counted as whole units. Earlier calculations retain precision; rounding occurs only in staffing. Sustainable demand, when `t > 0`, is:

`D_max = C_plan × 60 / t`

If mean human time is zero, the project does not present infinity as a valid operational result: `D_max` and dependent comparison metrics are not applicable and include an explanation.

### Growth scenarios

For annual growth `g` and period `y`, the projected base is:

`B_y = B_0 × (1 + g)^y`

Growth is compounded and changes only the base. Frequency, times, automation, team, available hours, and target utilization remain constant by explicit scenario assumption. This enables capacity sensitivity analysis, not a validated forecast.

## 4. Relevant decisions and rationale

| Decision | Rationale | Decision implication |
| --- | --- | --- |
| Use synthetic data with a fixed seed | Avoids internal data and allows reproduction | Results demonstrate a method, not company performance. |
| Use local DuckDB and a pure Python engine | Keeps SQL auditable and rules independent from the interface | History, simulator, and CSVs reuse the same logic. |
| Compare against a manual counterfactual | Makes the change in human effort visible | Does not prove automation caused an observed gain. |
| Show eligibility and adoption separately | Prevents silent extrapolation | Scenarios above eligibility are explicitly hypothetical. |
| Do not monetize released hours | Avoids financial conclusions without cost assumptions | Hours and equivalent people remain capacity indicators. |

## 5. Solution verification

- **Automated tests:** cover formulas, invalid limits, zero demand, zero human time, negative gains, compounded projections, data, SQL, CSVs, and relevant interface flows.
- **Known cases:** verify that the engine reproduces expected results with appropriate decimal tolerance, without rounding intermediate values.
- **Hours reconciliation:** for synthetic data, engine hours are compared with the direct sum of `human_minutes_actual / 60`; the largest recorded difference was `1.1368683772161603e-12` hours.
- **Reproduction:** in a new environment, documented commands installed dependencies, generated data, ran tests, and started the application; the review records 36 passing tests and a local HTTP 200 response.
- **Interface:** Streamlit native tests verified loading and flows such as month selection, explicit premise loading, and preserving/restoring edits. Human browser-based visual inspection was not recorded as completed; tests do not replace that evaluation.

These checks are technical evidence for the project. They are not presented as the author’s personal actions beyond the documented direction, follow-up, and iterative assessment.

## 6. Demonstrative scenario results

The test-verified reference case uses 10,000 active customers, 0.2 interactions/customer/month, 30 manual minutes, 60% actual automation, 5 residual minutes, 10% rework with 10 additional minutes, 10 people, 160 available hours/person/month, and 80% target utilization.

| Metric | Manual | Automated |
| --- | ---: | ---: |
| Demand | 2,000 interactions/month | 2,000 interactions/month |
| Mean human time | 30 min/interaction | 15.6 min/interaction |
| Required hours | 1,000 h/month | 520 h/month |
| Effective utilization | 62.5% | 32.5% |
| Required people | 8 | 5 |
| Sustainable demand | 2,560 interactions/month | 4,923.076923 interactions/month |

The comparison produces 480 released human hours and 3.75 planned-capacity equivalent people. Capacity increase is approximately 92.31%; growth margin over current demand is 28% for manual and approximately 146.15% for automated. The difference of three people between integer staffing counts is not the same measure as 3.75 continuous equivalent people.

All results in this section are simulated; they are not realized impacts.

## 7. Applying results to management decisions

Managers can use the model to structure questions, not automate a decision: does the team support a defined growth rate? Does utilization exceed its target before it reaches 100%? Does the gain depend on adoption above observed eligibility? Does the integer staffing requirement change even when equivalent capacity is fractional?

**Capacity increase** compares automated and manual `D_max`. **Growth margin** compares `D_max` with current demand. The first answers how the process changes; the second answers how much slack exists in the current scenario. Equivalent people express released effort in planned capacity; required people express integer staffing. Neither is an HR decision or a realized saving.

## 8. Limitations and possible evolution

The model measures human capacity only. It excludes systems, budget, quality, queues, lead times, service levels, individual productivity, costs, and other bottlenecks. It does not establish causality, statistically forecast demand, or optimize allocation.

Potential extensions include system constraints, sensitivity analysis, service levels, and—only with appropriate authorization and governance—calibration with real data. Any extension should preserve the distinction between a simulated result and realized impact.

## AI support

“AI tools supported model structuring, implementation, and technical review, under the author’s guidance.” The project was conceived and led by Roberto Gianolla Junior, with iterative delivery assessment, result verification, and user-experience refinement. AI is not presented as the principal author, nor are synthetic results presented as real business impact.
