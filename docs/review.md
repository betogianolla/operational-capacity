# Revisão final do MVP

**Data:** 2026-09-30

## Escopo revisado

Foram inspecionados o briefing, decisões, tarefas, motor de cálculo, gerador sintético, consultas DuckDB, projeções/CSVs, interface Streamlit, README e regras de Git. A revisão foi feita contra os critérios do MVP; testes aprovados não foram usados como único critério de aprovação.

## Problemas encontrados e correções

| Problema | Impacto | Correção |
| --- | --- | --- |
| README ainda descrevia o projeto como etapa de planejamento e tinha próximos passos já concluídos. | Impedia uma reprodução e apresentação coerentes. | README reorganizado como guia de instalação, geração, execução, testes, arquitetura, exemplo verificado e limitações. |
| Comando de bootstrap continha o marcador `<CAMINHO_PYTHON>`. | Não funcionaria sem edição manual em um terminal novo. | Comandos padronizados com `py -3.14` e execução explícita por `.venv\\Scripts\\python.exe`. |
| Meses da interface apareciam em formato numérico. | Apresentação não seguia a convenção pt-BR prevista. | Rótulos e seleção de mês ajustados para `jan/24`, `fev/24` etc. |

## Verificações automatizadas executadas

- `& '.\\.venv\\Scripts\\python.exe' -m pytest -q`: **36 passed in 17.94s**.
- Em ambiente virtual novo, `& '.\\.review-venv\\Scripts\\python.exe' -m pytest -q`: **36 passed in 11.38s**. Houve um aviso de cache causado por uma pasta local preexistente e ignorada (`.pytest_cache`); não afetou a execução dos testes.
- A suíte cobre fórmulas, unidades e arredondamento final; demanda zero; tempo humano médio zero; entradas inválidas; ganhos negativos; proporcionalidade da demanda; geração determinística; SQL com conjunto conhecido; integração motor/SQL; projeção composta; conteúdo dos CSVs; e fluxo da interface com `streamlit.testing.v1.AppTest`.
- O caso de referência verificado calcula 2.000 atendimentos/mês, 15,6 minutos de tempo humano médio após automação, 1.000 horas manuais, 520 horas automatizadas, 480 horas liberadas, 1.280 horas planejadas e 3,75 pessoas-capacidade liberada equivalente.
- `git check-ignore -v` confirmou que `.venv` e `.pytest_tmp` são ignorados. A inspeção de `git status --short` confirmou que o repositório ainda não possui commits e que os arquivos do projeto estão não rastreados, situação esperada nesta etapa.

## Inspeção técnica realizada

- Fórmulas e unidades foram conferidas no motor: atendimentos/mês, minutos por atendimento, horas/mês, frações para percentuais e pessoas. Cálculos internos não arredondam; apenas a necessidade de pessoas é arredondada para cima.
- Histórico, simulador e exportações usam as APIs do motor e da camada SQL/reporting, sem cópia de fórmulas na interface.
- A sessão inicia no mês mais recente; trocar o mês não substitui as premissas editadas. As ações explícitas de carregar e restaurar premissas foram verificadas pelos testes da aplicação.
- A projeção aplica crescimento anual composto à base, preservando as demais premissas, e sinaliza excedente em relação à utilização-alvo e déficit de pessoas.
- Médias sem observações permanecem ausentes. Quando uma média é necessária ao cenário, a origem da premissa substituta é mostrada. Demanda zero e tempo médio humano zero exibem valores não aplicáveis com explicação, não infinito.
- Dados e exportações se identificam como sintéticos/fictícios; a hipótese contrafactual manual e a limitação de capacidade humana estão documentadas.
- Busca por credenciais e caminhos pessoais não encontrou segredos nem caminhos pessoais desnecessários nos arquivos do projeto. `.gitignore` cobre ambiente virtual, caches, segredos locais do Streamlit e artefatos locais.

## Reprodução em ambiente novo

A versão instalada e usada na verificação é **Python 3.14.3**. Em um ambiente virtual novo, foram executados `py -3.14 -m venv .review-venv`, a instalação de `requirements-dev.txt`, a geração com `src\\operational_capacity\\synthetic_data.py --output-dir data`, os testes e a inicialização do Streamlit. O servidor respondeu **HTTP 200** em `localhost:8503`. Os comandos do README não dependem de ativar ambiente virtual nem de configurar `PYTHONPATH`.

Uma configuração de teste com `--basetemp=.pytest_tmp` foi removida de `pyproject.toml`: ela criava uma dependência de uma pasta temporária fixa e indisponível em uma execução isolada. O pytest volta a usar diretórios temporários próprios.

## Inspeção visual

O autor realizou uma avaliação visual pessoal da aplicação e aprovou sua apresentação para o MVP.

Esse registro se limita à avaliação visual e à aprovação informadas pelo autor. Não afirma que foram realizados testes de responsividade ou acessibilidade, revisão linha a linha do código ou outros procedimentos não confirmados. Os testes nativos do Streamlit verificam carregamento e fluxos de componentes; eles são evidência automatizada separada da avaliação visual do autor.

## Pendências

- Criar screenshots reais da aplicação para apoiar a apresentação no repositório.
- Configurar hospedagem online e registrar a URL de demonstração.
- Preparar e publicar uma apresentação do projeto no LinkedIn.
- A aplicação está aprovada para o MVP local; hospedagem e divulgação continuam pendentes.
