# Briefing — Simulador de Capacidade Operacional

## Nome do projeto

Simulador de Capacidade Operacional

## Problema de negócio

Gestores precisam estimar quanto uma operação pode crescer com a equipe atual e comparar o efeito de executar atendimentos manualmente ou com automação parcial, sem usar dados internos de empresas.

## Público-alvo

Gestores de operações e profissionais de dados.

## Competências que o projeto demonstrará

- Python, SQL e modelagem de dados.
- Validação de indicadores e regras de negócio.
- Simulação de cenários e comunicação de resultados de negócio.

## Perguntas que deve responder

1. Qual é a demanda mensal em atendimentos e em horas humanas nos processos manual e automatizado?
2. Qual é a capacidade planejada, a utilização efetiva e a demanda máxima sustentável em cada processo?
3. Qual é a capacidade adicional após automação, a margem de crescimento sobre a demanda atual e o equivalente de capacidade em pessoas?
4. Quantas pessoas são estimadas como necessárias em cada cenário de crescimento?

## Fontes de dados e condições de uso

| Fonte | Tipo | Origem ou método | Condições de uso | Observações |
| --- | --- | --- | --- | --- |
| Dados operacionais fictícios | Sintético | Gerador determinístico com semente documentada a ser implementado | Uso livre no portfólio | Sem dados internos, pessoais ou de empresas reais |

## Granularidade, chaves e campos necessários

- Granularidade atual: uma linha por mês de histórico sintético.
- Chave atual: `month`. Cenários serão tratados pela interface em etapa futura, não nos dados históricos desta etapa.
- Campos necessários: clientes ativos, atendimentos por cliente, tempos manual, residual e de retrabalho, percentuais de automação e retrabalho, pessoas, horas disponíveis, utilização-alvo e crescimento projetado.

## Indicadores e regras de cálculo

| Indicador ou regra | Definição | Fórmula ou lógica | Caso de resultado conhecido para validação |
| --- | --- | --- | --- |
| Demanda mensal | Atendimentos previstos por mês | `base × atendimentos por unidade` | Base 100 e 2 atendimentos por cliente = 200 atendimentos |
| Tempo humano médio automatizado | Esforço humano por atendimento após automação | `(1 - a) × tm + a × (tr + r × ta)` | `tm=30`, `a=0,5`, `tr=10`, `r=0,2`, `ta=15` = 21,5 min |
| Horas necessárias | Esforço mensal da operação | `demanda × tempo humano médio / 60` | 200 atendimentos × 21,5 min / 60 = 71,6667 h |
| Capacidade planejada | Horas alocáveis à operação | `pessoas × horas disponíveis × utilização-alvo` | 1 pessoa × 160 h × 0,8 = 128 h |
| Utilização efetiva | Fração das horas disponíveis exigida pela demanda | `horas necessárias / (pessoas × horas disponíveis)` | 71,6667 / 160 = 44,7917% |
| Pessoas necessárias | Pessoas estimadas para atender à demanda na utilização-alvo | `ceil(horas necessárias / (horas disponíveis × utilização-alvo))` | `ceil(71,6667 / 128)` = 1 pessoa |
| Demanda máxima sustentável | Atendimentos que cabem na capacidade planejada | `capacidade planejada × 60 / tempo humano médio` | 128 × 60 / 21,5 = 357,2093 atendimentos |
| Capacidade adicional | Diferença de atendimentos sustentáveis após automação | `capacidade automatizada - capacidade manual` | 357,2093 - 256 = 101,2093 atendimentos |
| Margem de crescimento | Crescimento sustentável sobre a demanda atual | `(capacidade sustentável / demanda atual) - 1` | 357,2093 / 200 - 1 = 78,6047% |
| Equivalente de capacidade em pessoas | Horas liberadas expressas em capacidade planejada por pessoa | `horas liberadas / (horas disponíveis × utilização-alvo)` | 28,3333 / 128 = 0,2214 pessoa equivalente |

### Caso conhecido inicial — entradas e verificação independente

| Entrada | Valor |
| --- | --- |
| Base atendida | 100 clientes ativos |
| Atendimentos por cliente por mês | 2 |
| Tempo manual por atendimento | 30 min |
| Percentual automatizado | 50% |
| Tempo humano residual | 10 min |
| Retrabalho entre automatizados | 20% |
| Tempo adicional de retrabalho | 15 min |
| Equipe | 1 pessoa |
| Horas disponíveis por pessoa por mês | 160 h |
| Utilização-alvo | 80% |

O motor retornou, de forma independente: demanda de 200 atendimentos; 21,5 min automatizados; 100 h manuais; 71,6667 h automatizadas; 28,3333 h liberadas; 128 h de capacidade planejada; utilizações de 62,5% e 44,7917%; 1 e 1 pessoas necessárias; capacidades máximas de 256 e 357,2093 atendimentos; aumento de 39,5349%; margens de 28% e 78,6047%; e equivalente contínuo de 0,2214 pessoa. Esses valores são casos de validação de fórmula, não resultados de negócio medidos.

### Caso de referência da implementação — entradas e verificação independente

| Entrada | Valor |
| --- | --- |
| Base atendida | 10.000 clientes ativos |
| Atendimentos por cliente por mês | 0,2 |
| Tempo manual por atendimento | 30 min |
| Percentual automatizado | 60% |
| Tempo humano residual | 5 min |
| Retrabalho entre automatizados | 10% |
| Tempo adicional de retrabalho | 10 min |
| Equipe | 10 pessoas |
| Horas disponíveis por pessoa por mês | 160 h |
| Utilização-alvo | 80% |

O motor retornou, de forma independente: demanda de 2.000 atendimentos; 15,6 min automatizados; 1.000 h manuais; 520 h automatizadas; 480 h liberadas; 1.280 h de capacidade planejada; utilizações de 62,5% e 32,5%; 8 e 5 pessoas necessárias; capacidades máximas de 2.560 e 4.923,076923 atendimentos; aumento de 92,307692%; margens de 28% e 146,153846%; e equivalente contínuo de 3,75 pessoas. A diferença entre os dimensionamentos arredondados é 3 pessoas e é uma medida distinta do equivalente contínuo. Estes são resultados de validação de fórmula, não resultados de negócio medidos.

## Hipóteses e limitações

- A unidade da base no MVP é cliente ativo; a escolha não pretende representar um setor específico.
- O tempo de retrabalho é adicional ao tempo residual, apenas para atendimentos automatizados que exigem retrabalho.
- A capacidade é humana; sistemas, orçamento, qualidade, filas e outros gargalos estão fora do modelo.
- Dados e cenários são sintéticos, reproduzíveis e fictícios.
- Tempo humano médio igual a zero é uma premissa inválida para estimar capacidade operacional; o sistema não deve exibir infinito.

## Escopo do MVP

- Comparar processo manual e automatizado.
- Calcular demanda em horas, capacidade, utilização, crescimento sustentável e pessoas necessárias.
- Projetar cenários de crescimento da base.
- Alterar premissas na interface, exibir fórmulas e limitações, e exportar resultados em CSV.
- Usar dados sintéticos reproduzíveis e consultas SQL locais.

## Fora do escopo

- Backend separado, autenticação, integração externa, serviços pagos e implantação.
- Economia financeira, ROI, previsão estatística e recomendação de contratação ou demissão.
- Gargalos não humanos e dados reais ou internos de empresas.

## Entregas

- Aplicação local demonstrável.
- Dados sintéticos reproduzíveis, consultas SQL e testes automatizados.
- Documentação de premissas, fórmulas, limitações, execução e validação.
- Exportação de resultados de cenário em CSV.

## Critérios de aceite verificáveis

- O cálculo reproduz os casos conhecidos desta seção dentro de tolerância definida nos testes.
- A interface aceita todas as premissas listadas, rejeita limites inválidos e trata tempo humano médio zero sem infinito operacional.
- A comparação exibe capacidade adicional versus manual, margem de crescimento sobre demanda atual, equivalente em pessoas e pessoas necessárias como inteiro arredondado para cima.
- Dados sintéticos informam explicitamente que são fictícios e podem ser reproduzidos pela semente documentada.
- A exportação CSV contém premissas e resultados do cenário apresentado.
