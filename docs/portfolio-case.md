# Estudo de caso — Simulador de Capacidade Operacional

[Read in English](portfolio-case.en.md) · [README em português](../README.pt-BR.md) · [README in English](../README.md)

**Autor e responsável pela condução do projeto: Roberto Gianolla Junior**

> “Projeto concebido e desenvolvido sob a orientação de Roberto Gianolla Junior, responsável pelo direcionamento do problema de negócio, acompanhamento das entregas e refinamento da solução.”

## 1. Problema identificado

Uma liderança de operações precisa responder a uma pergunta recorrente antes de aceitar mais demanda ou investir em automação: **a equipe atual consegue absorver o crescimento, e qual capacidade humana a automação pode liberar?**

O desafio não é apenas contar pessoas. É relacionar o tamanho da base atendida, a frequência de atendimento, o tempo humano por atendimento, o retrabalho e a disponibilidade da equipe em uma leitura que não confunda capacidade potencial com economia realizada.

O contexto deste caso é fictício. Os dados são sintéticos, determinísticos e marcados como `SYNTHETIC_FICTITIOUS`; não representam empresa, cliente ou impacto operacional real.

## 2. Objetivo da solução

Construir uma ferramenta local de apoio à decisão para comparar um processo manual com um processo parcialmente automatizado, identificar a utilização da equipe, estimar a necessidade de pessoas e explorar três anos de crescimento composto.

O resultado é um **modelo determinístico de capacidade operacional**. Não é inferência causal, previsão estatística validada, modelo de filas ou algoritmo de otimização.

## Orientação e contribuição do autor

Roberto Gianolla Junior conduziu a identificação do problema de negócio e o direcionamento da solução. A documentação registra escolhas que traduzem essa orientação em entregas verificáveis:

- clientes ativos foram definidos como unidade demonstrativa da base, sem vincular o caso a um setor ou empresa;
- a ferramenta foi delimitada como apoio à decisão de capacidade humana, sem converter horas liberadas em economia financeira ou recomendação de demissão/contratação;
- elegibilidade de automação foi separada da adoção efetiva, para não tratar limite de processo como resultado realizado;
- o trabalho foi conduzido em etapas com motor de cálculo independente, dados reproduzíveis, consultas SQL, interface, exportação e revisão;
- foram solicitados refinamentos de uso e apresentação: formatação pt-BR, diferenças em pontos percentuais, grupos de entradas, alertas de utilização e preservação de cenários editados ao trocar o mês.

Essas evidências aparecem no briefing, nas decisões, nas tarefas e na documentação da interface. A atribuição não afirma revisão pessoal linha a linha, execução pessoal de todos os testes automatizados ou escrita manual integral do código.

## 3. Como o problema foi traduzido em modelo analítico

### Base, demanda e unidades

Se `B` é a base de clientes ativos e `f` é a frequência em atendimentos por cliente/mês, a demanda mensal é:

`D = B × f`

`D` é medido em atendimentos/mês. A fórmula torna proporcional o efeito da base: mantendo a frequência, 10% mais clientes implica 10% mais atendimentos. A frequência observada no histórico sintético é uma taxa medida; no simulador ela pode ser uma premissa escolhida.

### Tempo humano manual, residual e retrabalho

Para o processo manual, o tempo humano médio é `t_manual`, em minutos/atendimento. Para o processo automatizado, com adoção efetiva `a`, tempo residual `t_residual`, taxa de retrabalho `r` e tempo adicional de retrabalho `t_rework`, o motor calcula:

`t_auto = (1 − a) × t_manual + a × (t_residual + r × t_rework)`

O primeiro termo representa a parcela ainda manual. O segundo representa a parcela automatizada, incluindo o valor esperado do retrabalho. `r × t_rework` é uma média esperada de minutos adicionais por atendimento automatizado; ela não exige independência entre eventos. O retrabalho é adicional ao residual, evitando dupla contagem.

Elegibilidade é a proporção de atendimentos que **poderiam** ser automatizados. Adoção efetiva é a proporção de atendimentos que **foi** automatizada e é a variável `a` usada no cálculo. Se o cenário ultrapassa a elegibilidade observada, a interface exige identificar uma hipótese de expansão da elegibilidade.

### Carga, capacidade e utilização

Para qualquer tempo humano médio `t`, a carga mensal é:

`H = D × t / 60`

`H` é medido em horas/mês; a divisão por 60 converte minutos em horas. Com `P` pessoas, `h` horas disponíveis por pessoa/mês e utilização-alvo `u_target`, a capacidade planejada é:

`C_plan = P × h × u_target`

Já a utilização efetiva usa toda a disponibilidade, antes da meta:

`U_eff = H / (P × h)`

Portanto, utilização efetiva e utilização-alvo são distintas: a primeira descreve a carga relativa à disponibilidade; a segunda é uma decisão de planejamento usada para reservar folga operacional.

### Pessoas e demanda sustentável

A necessidade estimada de pessoas é:

`P_required = ceil(H / (h × u_target))`

O arredondamento para cima é necessário porque pessoas são contadas como unidades inteiras. Os cálculos anteriores mantêm precisão; o arredondamento ocorre apenas no dimensionamento. A demanda máxima sustentável, quando `t > 0`, é:

`D_max = C_plan × 60 / t`

Se o tempo humano médio for zero, o projeto não apresenta infinito como resultado operacional válido: `D_max` e métricas comparativas dependentes ficam não aplicáveis, com explicação.

### Cenários de crescimento

Para crescimento anual `g` e período `y`, a base projetada é:

`B_y = B_0 × (1 + g)^y`

O crescimento é composto e altera apenas a base. Frequência, tempos, automação, equipe, horas disponíveis e utilização-alvo ficam constantes por hipótese explícita. Isso permite analisar sensibilidade de capacidade, não produzir previsão validada.

## 4. Decisões relevantes e justificativas

| Decisão | Justificativa | Implicação para a decisão |
| --- | --- | --- |
| Usar dados sintéticos com semente fixa | Evita dados internos e permite reprodução | Resultados demonstram método, não desempenho de empresa. |
| Usar DuckDB local e motor Python puro | Mantém SQL auditável e regras independentes da interface | Histórico, simulador e CSVs reutilizam a mesma lógica. |
| Comparar com contrafactual manual | Torna visível a mudança de esforço humano | Não prova que automação causou o ganho observado. |
| Mostrar elegibilidade e adoção separadamente | Impede extrapolação silenciosa | Cenários acima da elegibilidade ficam explicitamente hipotéticos. |
| Não monetizar horas liberadas | Evita conclusão financeira sem premissas de custo | Horas e pessoas-equivalentes permanecem indicadores de capacidade. |

## 5. Verificação da solução

- **Testes automatizados:** cobrem fórmulas, limites inválidos, demanda zero, tempo humano zero, ganhos negativos, projeções compostas, dados, SQL, CSVs e fluxos relevantes da interface.
- **Casos conhecidos:** verificam que o motor reproduz resultados esperados com tolerância decimal apropriada, sem arredondar valores intermediários.
- **Reconciliação de horas:** para os dados sintéticos, horas do motor são comparadas à soma direta de `human_minutes_actual / 60`; a maior diferença registrada foi `1,1368683772161603e-12` hora.
- **Reprodução:** em ambiente novo, os comandos documentados foram usados para instalar dependências, gerar dados, executar testes e iniciar a aplicação; o parecer registra 36 testes aprovados e resposta HTTP 200 local.
- **Interface:** testes nativos do Streamlit verificaram carregamento e fluxos como seleção do mês, carregamento explícito de premissas e preservação/restauração de edição. A inspeção visual humana em navegador não foi registrada como concluída; testes não substituem essa avaliação.

Essas verificações são evidências técnicas do projeto. Elas não são apresentadas como ações pessoais do autor além da orientação, acompanhamento e avaliação iterativa registrados.

## 6. Resultados de cenário demonstrativo

O caso de referência, verificado pelos testes, usa 10.000 clientes ativos, 0,2 atendimento por cliente/mês, 30 minutos manuais, 60% de automação efetiva, 5 minutos residuais, 10% de retrabalho com 10 minutos adicionais, 10 pessoas, 160 horas disponíveis por pessoa/mês e utilização-alvo de 80%.

| Indicador | Manual | Automatizado |
| --- | ---: | ---: |
| Demanda | 2.000 atendimentos/mês | 2.000 atendimentos/mês |
| Tempo humano médio | 30 min/atendimento | 15,6 min/atendimento |
| Horas necessárias | 1.000 h/mês | 520 h/mês |
| Utilização efetiva | 62,5% | 32,5% |
| Pessoas necessárias | 8 | 5 |
| Demanda máxima sustentável | 2.560 atendimentos/mês | 4.923,076923 atendimentos/mês |

A comparação produz 480 horas humanas liberadas e 3,75 pessoas-equivalentes de capacidade planejada. O aumento de capacidade é aproximadamente 92,31%; a margem de crescimento sobre a demanda atual é 28% no manual e aproximadamente 146,15% no automatizado. A diferença de três pessoas entre dimensionamentos inteiros não é a mesma medida que 3,75 pessoas-equivalentes contínuas.

Todos os resultados dessa seção são simulados; não são impactos efetivamente realizados.

## 7. Aplicação dos resultados à decisão gerencial

O gestor pode usar o modelo para estruturar perguntas, não para automatizar uma decisão: a equipe comporta um crescimento definido? A utilização ultrapassa a meta antes de chegar a 100%? O ganho depende de adoção acima da elegibilidade observada? A necessidade inteira de pessoas muda, mesmo quando a capacidade equivalente é fracionária?

**Aumento de capacidade** compara `D_max` do automatizado com o manual. **Margem de crescimento** compara `D_max` com a demanda atual. A primeira responde quanto o processo muda; a segunda responde quanto de folga existe no cenário atual. O indicador de pessoas-equivalentes expressa esforço liberado em capacidade planejada; pessoas necessárias expressa dimensionamento inteiro. Nenhum dos dois é decisão de RH ou economia realizada.

## 8. Limitações e evoluções possíveis

O modelo mede apenas capacidade humana. Não inclui sistemas, orçamento, qualidade, fila, prazos, níveis de serviço, produtividade individual, custos ou outros gargalos. Não estabelece causalidade, não prevê estatisticamente a demanda e não otimiza alocação.

Evoluções possíveis incluem limites de sistemas, análises de sensibilidade, níveis de serviço e, somente com autorização e governança adequadas, calibração com dados reais. Qualquer extensão deve preservar a distinção entre resultado simulado e impacto realizado.

## Apoio de IA

“Ferramentas de IA apoiaram a estruturação do modelo, a implementação e a revisão técnica, sob a orientação do autor.” O projeto foi concebido e conduzido por Roberto Gianolla Junior, com avaliação iterativa das entregas, verificação de resultados e refinamento da experiência de uso. A IA não é apresentada como autora principal, nem os resultados sintéticos como impacto real de negócio.
