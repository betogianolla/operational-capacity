# Instruções do Projeto — Simulador de Capacidade Operacional

Este arquivo complementa `E:\Portfolio\AGENTS.md`. Em caso de conflito, siga a instrução mais restritiva.

## Objetivo

Construir uma aplicação demonstrável para estimar quanto uma operação baseada em clientes ativos pode crescer com a equipe atual e como a automação altera sua capacidade humana. O público são gestores de operações e profissionais de dados.

## Stack e versões

- Linguagem: Python 3.14.3.
- Interface: Streamlit 1.64.0.
- Consultas SQL locais: DuckDB 1.5.6.
- Testes: pytest 9.1.1.

A stack foi escolhida para manter uma aplicação local e simples: Python concentra o cálculo e a geração de dados; Streamlit fornece a interface e a exportação; DuckDB demonstra consultas SQL locais; pytest valida regras críticas. Não usar backend separado, autenticação, serviços pagos ou infraestrutura externa no MVP.

## Organização do código

- `src/`: regras de cálculo, geração de dados e consultas.
- `app.py`: interface Streamlit, que compõe as APIs de `src/` sem repetir fórmulas.
- `tests/`: testes automatizados, sobretudo de cálculos e validações.
- `data/`: dados sintéticos reproduzíveis e artefatos locais derivados, claramente identificados como fictícios.
- `assets/`: imagens ou recursos de apresentação, caso necessários.
- `docs/`: briefing, tarefas e decisões.

## Regras de negócio

- A unidade da base do MVP é **cliente ativo**; demanda mensal é `clientes ativos × atendimentos por cliente por mês`.
- Tempo humano médio após automação: `(1 - percentual automatizado) × tempo manual + percentual automatizado × (tempo residual + percentual de retrabalho × tempo adicional de retrabalho)`.
- O tempo adicional de retrabalho é acréscimo ao tempo residual e não pode ser contabilizado duas vezes.
- Horas necessárias: `demanda mensal × tempo humano médio / 60`.
- Capacidade planejada em horas: `pessoas × horas disponíveis por pessoa × utilização-alvo`.
- Utilização efetiva: `horas necessárias / (pessoas × horas disponíveis por pessoa)`.
- Pessoas necessárias: arredondamento para cima de `horas necessárias / (horas disponíveis por pessoa × utilização-alvo)`.
- Demanda máxima sustentável: `capacidade planejada em horas × 60 / tempo humano médio`.
- Capacidade adicional em relação ao manual: `demanda máxima sustentável automatizada - demanda máxima sustentável manual`; a variação percentual usa a capacidade manual como denominador quando ela for maior que zero.
- Margem de crescimento em relação à demanda atual: `(demanda máxima sustentável / demanda mensal atual) - 1`, quando a demanda atual for maior que zero.
- Horas humanas liberadas: `horas necessárias no manual - horas necessárias após automação`.
- Equivalente de capacidade em pessoas: `horas humanas liberadas / (horas disponíveis por pessoa × utilização-alvo)`; é uma equivalência de capacidade planejada, não uma decisão de pessoal.
- Para tempo humano médio igual a zero, não exibir capacidade infinita como resultado operacional válido; exibir estado de cálculo não aplicável e orientar a revisar a premissa.
- Para denominadores iguais a zero nas métricas comparativas, exibir estado não aplicável em vez de calcular infinito ou percentual indefinido.
- Percentuais devem estar entre 0 e 1; utilização-alvo deve ser maior que 0 e menor ou igual a 1; tempos, base e demanda devem ser não negativos; pessoas e horas disponíveis devem ser positivas.
- O modelo mede capacidade humana. Limites de sistemas, orçamento, qualidade, filas e outros gargalos ficam fora do MVP.
- Horas humanas liberadas representam diferença de esforço estimado, não economia financeira realizada. Equivalente de capacidade em pessoas não representa demissões nem contratações efetivamente evitadas.

## Comandos de instalação, execução e validação

No PowerShell do Windows, com Python 3.14.3 instalado pelo lançador `py`:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\operational_capacity\synthetic_data.py --output-dir data
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Para geração e análise dos dados sintéticos, consulte `docs/data.md`. Para interface, projeções e CSVs, consulte `docs/interface.md`.

## Convenções

- Usar nomes em inglês no código e português na documentação e interface, salvo decisão posterior registrada.
- Manter regras de negócio fora da interface e cobri-las com testes de resultado conhecido.
- Identificar explicitamente todos os dados como sintéticos e fictícios, com método de reprodução e semente documentados.
- Registrar hipóteses e decisões em `docs/decisions.md`; atualizar `docs/tasks.md` com evidências reais.
- Não incluir credenciais, dados confidenciais ou informações internas em arquivos ou logs.
- Não publicar, fazer push ou implantar sem solicitação.

## Critérios de conclusão

- O MVP calcula os indicadores definidos para os processos manual e automatizado, com validações de entrada e testes de resultado conhecido.
- A interface permite alterar premissas, comparar cenários, consultar fórmulas e limitações, e exportar resultados em CSV.
- Dados sintéticos são reproduzíveis, fictícios e têm origem documentada.
- Consultas SQL, documentação e instruções de execução são reproduzíveis.
- Verificações executadas e seus resultados reais estão registrados; revisão não possui problemas impeditivos abertos.

## Papéis reutilizáveis

Consulte apenas o papel relevante:

- Coordenador: [`../../agents/coordinator.md`](../../agents/coordinator.md)
- Desenvolvedor: [`../../agents/developer.md`](../../agents/developer.md)
- Revisor: [`../../agents/reviewer.md`](../../agents/reviewer.md)

Esses arquivos definem papéis reutilizáveis. Eles não executam nem configuram agentes automaticamente; delegação só ocorre quando houver suporte explícito.
