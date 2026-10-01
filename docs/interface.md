# Interface e exportações

## Inicialização no Windows

Em um terminal novo, na raiz do projeto, sem configurar `PYTHONPATH`:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

O `app.py` adiciona `src/` ao caminho de importação antes de carregar o domínio. Se os arquivos de dados não existirem, a aplicação mostra na tela o comando de geração e encerra a renderização sem traceback para o gestor.

## Experiência

- **Histórico da operação:** aviso compacto de dados sintéticos, seleção de mês, indicadores, comparação da utilização com a meta em pontos percentuais, gráficos mensais, contrafactual manual e fontes de premissas substitutas.
- **Simulador de crescimento:** em uma sessão nova inicia com o mês mais recente; entradas são organizadas em Demanda, Processo e automação, e Equipe e capacidade. A interface converte percentuais para frações do motor, compara manual e automatizado, e projeta ano-base mais três anos de crescimento composto da base.
- A automação realizada e a elegibilidade observada são medidas distintas. Se a automação simulada a exceder, a interface exige confirmação da hipótese de expansão e identifica o cenário como hipotético.
- Trocar o mês de referência não altera o cenário que o usuário editou. A ação **Carregar premissas deste mês** aplica a referência de forma explícita; **Restaurar premissas carregadas** descarta edições do cenário atual.
- Clientes ativos e pessoas usam entradas inteiras. Meses, números, percentuais, tabelas, eixos e tooltips são apresentados em pt-BR; projeções preservam precisão interna e arredondam clientes somente para apresentação.
- Utilização acima da meta é destacada mesmo abaixo de 100%. Acima de 100%, a interface explica que as horas requeridas excedem as disponíveis e que filas e prazos não são modelados.
- O expansível metodológico descreve fórmulas, hipóteses e limites sem duplicar a lógica do módulo `calculations.py`.

## CSVs disponíveis

Os downloads ocorrem em memória; a aplicação não grava arquivos de resultados no projeto.

| Arquivo | Linhas | Colunas e unidades principais | Identificação |
| --- | --- | --- | --- |
| `historico_capacidade_sintetico.csv` | Uma por mês | `*_per_month` em atendimentos ou horas/mês; frações entre 0 e 1; pessoas como inteiros | `data_origin=SYNTHETIC_FICTITIOUS` e nota metodológica |
| `cenarios_crescimento_hipoteticos.csv` | Ano-base e três anos projetados | Premissas do cenário, clientes ativos, demanda/mês, horas/mês, pessoas, déficit e frações | `data_origin=SYNTHETIC_FICTITIOUS`, `scenario_type=HYPOTHETICAL_GROWTH_SCENARIO` e hipótese explícita |

Os cenários aplicam crescimento composto somente aos clientes ativos; atendimentos por cliente, automação, tempos, equipe, horas disponíveis e utilização-alvo permanecem constantes. Resultados negativos são preservados. Nenhum arquivo descreve economia realizada, previsão validada ou decisão efetiva de pessoal.

## Evidências de interface

Em 2026-09-30, os testes nativos do Streamlit verificaram: carregamento das duas abas, mês mais recente como referência inicial, carregamento explícito das premissas de jan/24 (8.238 clientes e frequência `1.762 / 8.238`), confirmação de expansão de elegibilidade e preservação/restauração de edições. A suíte completa aprovou 36 testes em 9,90 s. A aplicação respondeu HTTP 200 em `localhost:8502`; a aparência visual não foi inspecionada em navegador neste ambiente.
