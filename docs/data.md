# Dados sintéticos e consultas locais

## Origem e reprodução

Os arquivos em `data/` são integralmente sintéticos e fictícios (`SYNTHETIC_FICTITIOUS`). Eles não representam empresas, clientes, pessoas ou impacto operacional real.

O gerador usa a semente fixa `20260930`, inicia em `2024-01-01` e produz 24 meses consecutivos. A mesma configuração gera os mesmos CSVs e metadados. Os dados atuais foram gerados com 24 meses e 47.074 atendimentos fictícios.

No PowerShell do Windows, a partir da raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:PYTHONPATH = (Resolve-Path .\src)
.\.venv\Scripts\python.exe -m operational_capacity.synthetic_data --output-dir data
.\.venv\Scripts\python.exe -m operational_capacity.queries --monthly-path data\monthly_capacity.csv --interactions-path data\interactions.csv
```

`requirements.txt` fixa DuckDB 1.5.6. O comando de análise consulta os CSVs localmente e imprime uma amostra. A interface disponibiliza downloads CSV em memória, documentados em `docs/interface.md`.

## Tabelas e relacionamento

### `monthly_capacity.csv`

Granularidade: uma linha por mês. Chave: `month` (`YYYY-MM-01`).

| Campo | Unidade | Descrição |
| --- | --- | --- |
| `active_customers` | clientes ativos | Base atendida sintética do mês. |
| `team_members` | pessoas | Equipe disponível para a capacidade humana. |
| `available_hours_per_person_per_month` | horas/pessoa/mês | Horas disponíveis antes da utilização-alvo. |
| `target_utilization_fraction` | fração entre 0 e 1 | Utilização-alvo. |
| `*_assumption` | minutos ou fração | Premissas sintéticas explícitas usadas quando uma média observada não existe. |
| `synthetic_data_label` | texto | Sempre `SYNTHETIC_FICTITIOUS`. |

### `interactions.csv`

Granularidade: uma linha por atendimento sintético. Chave: `interaction_id`. Relação: muitos atendimentos para um mês por `month → monthly_capacity.month`.

| Campo | Unidade | Descrição |
| --- | --- | --- |
| `interaction_date` | data | Data sintética dentro do mês. |
| `process` | categoria | `manual` ou `automated`. |
| `automation_eligible` | booleano | Limite de elegibilidade; somente atendimentos elegíveis podem ser automatizados. |
| `manual_minutes` | minutos/atendimento | Tempo manual contrafactual aplicado a todos os atendimentos do mês. |
| `human_minutes_actual` | minutos/atendimento | Tempo humano do processo observado no dado sintético. |
| `residual_minutes` | minutos/automatizado | Preenchido apenas para automatizados. |
| `requires_rework` | booleano | Só pode ser verdadeiro para automatizados. |
| `rework_additional_minutes` | minutos/caso com retrabalho | Preenchido apenas para automatizados com retrabalho. |

## Distribuições e limites ilustrativos

- Clientes ativos começam próximos de 8.200, crescem cerca de 0,9% ao mês e recebem pequena sazonalidade e variação aleatória limitada.
- Atendimentos por cliente ficam próximos de 0,215/mês, com sazonalidade e variação limitada.
- Elegibilidade começa próxima de 62% e cresce gradualmente, limitada a 82%.
- A automação realizada é zero no primeiro mês e aumenta gradualmente, limitada a 82% dos elegíveis. Logo, automação realizada é sempre menor ou igual à elegibilidade.
- Tempo manual é constante dentro de cada mês (28 a 32,5 min); residual automatizado varia entre 4 e 7 min; retrabalho ocorre próximo de 10% dos automatizados, com acréscimo entre 7 e 13 min.

Esses limites foram escolhidos apenas para uma demonstração plausível e auditável; não são parâmetros de mercado ou evidência de desempenho real.

## Consulta mensal e integração com o motor

`operational_capacity.queries` usa DuckDB em memória para consolidar por mês: clientes ativos, contagens, proporções de elegibilidade e automação realizada, médias de tempos, taxa de retrabalho, horas humanas diretamente somadas e premissas da equipe.

Elegibilidade e automação realizada permanecem distintas: o motor recebe `automated_interaction_fraction`, isto é, a proporção efetivamente automatizada sobre todos os atendimentos. A elegibilidade é mantida como limite para cenários futuros.

Médias de residual, taxa de retrabalho e tempo adicional permanecem ausentes (`NULL`) quando não existem atendimentos automatizados ou casos de retrabalho. A consulta não as substitui por zero. Para alimentar o motor nesses casos, a integração usa a coluna `*_assumption` correspondente da tabela mensal e registra a origem como premissa sintética explícita. Como a fração relacionada é zero, a premissa não altera as horas do mês.

O contrafactual manual assume que `manual_minutes` médio também se aplicaria aos atendimentos automatizados. Para o dado gerado, esse tempo é constante por mês; por isso as horas automatizadas calculadas pelo motor são verificadas contra a soma direta de `human_minutes_actual / 60`. Essa correspondência é uma checagem aritmética do modelo sintético, não demonstra causalidade ou ganho real de automação.

## Evidências de validação desta geração

- A suíte completa executada em 2026-09-30 aprovou 30 testes em 3,83 s, com Python 3.14.3, pytest 9.1.1 e DuckDB 1.5.6.
- Os testes geram os arquivos duas vezes com a mesma configuração e comparam os bytes dos dois CSVs e dos metadados.
- Para os 24 meses gerados em `data/`, a maior diferença absoluta observada entre as horas do motor e a soma direta dos atendimentos foi `1,1368683772161603e-12` hora, compatível com precisão de ponto flutuante.
- A consulta SQL também é validada contra um conjunto pequeno e independente de três atendimentos, incluindo automação e retrabalho.
