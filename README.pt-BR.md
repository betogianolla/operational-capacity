# Simulador de Capacidade Operacional

[Read in English](README.md) · [Estudo de caso em português](docs/portfolio-case.md) · [Portfolio case in English](docs/portfolio-case.en.md)

**[Abrir demonstração online](https://operational-capacity.streamlit.app/)** · Hospedada publicamente no Streamlit Community Cloud.

**Autor e responsável pela condução do projeto: Roberto Gianolla Junior**

> “Projeto concebido e desenvolvido sob a orientação de Roberto Gianolla Junior, responsável pelo direcionamento do problema de negócio, acompanhamento das entregas e refinamento da solução.”

## 1. Problema identificado

Como avaliar se uma equipe consegue absorver o crescimento da demanda e quanto a automação amplia sua capacidade operacional? Este projeto trata essa decisão por meio de um modelo local e determinístico de capacidade. Usa **clientes ativos** como unidade demonstrativa da base atendida e compara um contrafactual manual com um processo parcialmente automatizado.

Os dados e resultados são sintéticos e simulados. Não descrevem uma empresa real, economia realizada, decisão de pessoal ou impacto de negócio observado.

## 2. Objetivo da solução

A aplicação Streamlit permite ao gestor inspecionar um histórico sintético, alterar premissas explícitas, comparar capacidade manual e automatizada e projetar três anos de crescimento composto. Ela apoia uma discussão de capacidade; não é previsão estatística validada, inferência causal, modelo de filas ou algoritmo de otimização.

![Simulador de crescimento com premissas, elegibilidade observada para automação e resumo do cenário.](assets/simulator.png)

*As premissas e o resumo do cenário exibidos acima usam dados sintéticos.*

## Contribuição profissional do autor

Roberto Gianolla Junior identificou e escolheu o problema de negócio, definiu o objetivo de apoio à decisão e conduziu o escopo iterativo registrado na documentação. Exemplos concretos incluem a escolha de **clientes ativos** como unidade da base, a exigência de distinguir elegibilidade de adoção efetiva da automação, a exclusão de economia financeira e recomendações de pessoal, e o tratamento explícito de retrabalho, demanda zero e resultados não aplicáveis.

O histórico do projeto também registra a orientação para manter o motor de cálculo independente da interface, preservar cenários editados ao trocar o mês de referência e refinar a experiência com formatação pt-BR, diferenças em pontos percentuais, entradas agrupadas e avisos quando a utilização supera a meta. Essas decisões estão em [docs/decisions.md](docs/decisions.md), [docs/briefing.md](docs/briefing.md) e [docs/interface.md](docs/interface.md).

Esta atribuição descreve direcionamento, acompanhamento das entregas, refinamentos solicitados e análise crítica dos indicadores. Não afirma que o autor fez revisão linha a linha, executou pessoalmente todos os testes automatizados ou escreveu manualmente todo o código.

## 3. Tradução do problema em modelo analítico

O modelo é determinístico: as mesmas entradas produzem as mesmas saídas.

- **A demanda é proporcional à base atendida:** `D = B × f`, em que `B` são clientes ativos e `f` são atendimentos por cliente por mês.
- **O tempo humano após automação é uma média ponderada:** `t_auto = (1 − a) × t_manual + a × (t_residual + r × t_rework)`. `a` é a adoção efetiva, não a elegibilidade. O termo `r × t_rework` é o tempo adicional esperado de retrabalho por atendimento automatizado; é um valor esperado e não exige independência entre eventos.
- **Minutos são convertidos em horas mensais:** `H = D × t / 60`.
- **Capacidade e utilização:** a capacidade planejada é `C_plan = P × h × u_target`, enquanto a utilização efetiva é `U_eff = H / (P × h)`. A meta é um limiar de planejamento; não é a mesma medida que a utilização efetiva.
- **O dimensionamento é discreto:** `P_required = ceil(H / (h × u_target))`. Cálculos intermediários mantêm precisão; apenas pessoas necessárias são arredondadas para cima.
- **A demanda máxima sustentável:** `D_max = C_plan × 60 / t`, quando o tempo humano é maior que zero.
- **Cenários de crescimento:** `B_y = B_0 × (1 + g)^y`. Apenas a base cresce de forma composta; as demais premissas permanecem constantes por hipótese de cenário.

Taxas históricas são medidas nos dados sintéticos. Valores da simulação são premissas escolhidas, mesmo quando iniciados a partir de um mês histórico. Elegibilidade é um limite de referência; adoção efetiva é a entrada usada pelo motor.

## 4. Decisões relevantes e justificativas

- **Dados sintéticos e reproduzíveis:** 24 meses e 47.074 atendimentos fictícios evitam dados confidenciais e permitem demonstração reproduzível.
- **Contrafactual manual:** a média manual mensal é aplicada aos atendimentos automatizados. A comparação é auditável, mas não demonstra causalidade.
- **Retrabalho adicional ao tempo residual:** evita dupla contagem.
- **Elegibilidade diferente de adoção:** adoção acima da elegibilidade observada exige hipótese explícita de expansão.
- **Sem infinito operacional:** com tempo humano zero, capacidade sustentável e métricas relacionadas são não aplicáveis e explicadas.

## 5. Verificação da solução

Testes automatizados verificam fórmulas, regras de validação, casos extremos, projeções compostas, conteúdo dos CSVs, geração determinística, agregação SQL e fluxos relevantes do Streamlit. Casos conhecidos conferem resultados esperados. A camada de dados também reconcilia as horas humanas mensais do motor com a soma direta dos tempos dos atendimentos; a maior diferença documentada foi `1,1368683772161603e-12` hora, compatível com precisão de ponto flutuante.

A reprodução foi verificada em ambiente novo com os comandos documentados de instalação, geração, testes e inicialização do Streamlit. O parecer registra uma execução aprovada de 36 testes e resposta HTTP 200 do servidor local. O autor relata que a aplicação hospedada carregou sem exigir login e que o histórico, o simulador, as projeções e os downloads funcionaram. Esse relato é registrado separadamente da resposta HTTP observada nesta revisão; não havia navegador interativo disponível para repetir esses fluxos. A configuração e os limites da verificação estão em [docs/deployment.md](docs/deployment.md).

## 6. Cenário demonstrativo

No caso de referência verificado — 10.000 clientes ativos, 0,2 atendimento por cliente/mês, 30 minutos manuais, 60% de automação, 5 minutos residuais, 10% de retrabalho de 10 minutos, 10 pessoas, 160 horas disponíveis por pessoa/mês e utilização-alvo de 80% — o modelo retorna:

- 2.000 atendimentos/mês; 15,6 minutos humanos por atendimento após automação;
- 1.000 horas manuais versus 520 automatizadas; 1.280 horas planejadas da equipe;
- utilização efetiva manual de 62,5% versus 32,5% automatizada;
- 8 pessoas necessárias no manual versus 5 no automatizado;
- 2.560 atendimentos/mês sustentáveis no manual versus 4.923,076923 no automatizado;
- 480 horas humanas liberadas e 3,75 pessoas-equivalentes de capacidade.

São resultados simulados usados para verificar o modelo, não impactos realizados.

## 7. Aplicação dos resultados à decisão gerencial

A aplicação distingue **aumento de capacidade** — variação percentual da demanda sustentável entre processo automatizado e manual — de **margem de crescimento** — folga entre demanda sustentável e demanda atual. Também distingue **capacidade equivalente de pessoas**, contínua (horas liberadas divididas pela capacidade planejada por pessoa), de **pessoas necessárias**, um dimensionamento inteiro. Nenhuma medida representa demissão, contratação, contratação evitada ou economia financeira realizada.

O gestor pode usar a comparação para identificar se um cenário ultrapassa a utilização-alvo, quando a equipe disponível é insuficiente e quais premissas precisam de validação operacional antes de uma decisão.

## 8. Limitações

O modelo representa apenas capacidade humana. Não modela sistemas, orçamento, qualidade, filas, níveis de serviço, prazos, produtividade individual ou outros gargalos. Não é evidência de ganho causal da automação nem previsão validada. Dados sintéticos demonstram o método; não calibram uma operação real.

## Arquitetura e execução

`app.py` é o ponto de entrada. A interface Streamlit compõe um motor Python puro, consultas locais a CSVs com DuckDB e exportações CSV em memória. Os CSVs sintéticos são versionados em `data/`, portanto um clone novo já contém os dados demonstrativos.

As dependências de execução são `duckdb==1.5.6` e `streamlit==1.64.0`. Python 3.13 é recomendado para hospedagem Linux; o projeto declara compatibilidade com Python 3.11 a 3.14. Para execução local no Windows com o ambiente validado em Python 3.14.3:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\operational_capacity\synthetic_data.py --output-dir data
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Consulte a [documentação dos dados](docs/data.md), a [documentação da interface](docs/interface.md) e o [parecer de revisão](docs/review.md).

## Apoio de IA

“Ferramentas de IA apoiaram a estruturação do modelo, a implementação e a revisão técnica, sob a orientação do autor.” O projeto foi concebido e conduzido por Roberto Gianolla Junior, com avaliação iterativa das entregas, verificação de resultados e refinamento da experiência de uso. A IA não é apresentada como autora principal, e resultados sintéticos não são apresentados como impacto real de negócio.
