# Simulador de Capacidade Operacional

**Autor: Roberto Gianolla Junior**

## Contexto fictício

Uma operação fictícia atende clientes ativos todos os meses. A liderança precisa avaliar se a equipe atual suporta o crescimento esperado e quais mudanças de processo poderiam liberar capacidade humana. Os dados desta demonstração são sintéticos, determinísticos e não representam uma empresa real.

## Problema

Comparar o esforço de um processo manual com um processo parcialmente automatizado, sem transformar capacidade em promessa de economia, demissão ou contratação evitada.

## Abordagem

O projeto gera 24 meses de atendimentos sintéticos, agrega o histórico localmente com DuckDB e calcula indicadores em um motor Python independente da interface. Uma aplicação Streamlit permite escolher um mês, modificar premissas e projetar três anos de crescimento composto. CSVs disponibilizam o histórico consolidado e os cenários projetados.

## Decisões técnicas e analíticas

- O motor usa dataclasses, valida os limites das entradas e retorna valores não aplicáveis com motivo explícito, em vez de infinito.
- Elegibilidade de automação é diferente de automação efetivamente realizada. Ultrapassar a elegibilidade observada exige registrar uma hipótese de expansão.
- Retrabalho é um acréscimo ao tempo humano residual do atendimento automatizado, evitando dupla contagem.
- O contrafactual manual aplica o tempo manual médio também aos atendimentos automatizados; é uma hipótese aritmética, não evidência causal.
- A interface não replica fórmulas: reutiliza o motor e a camada de consultas.

## Resultado de cenário simulado executado

No caso de referência automatizado, executado pelos testes com 10.000 clientes ativos, 0,2 atendimento por cliente/mês, 30 minutos manuais, 60% de automação, 5 minutos residuais e 10% de retrabalho de 10 minutos, a demanda é de 2.000 atendimentos/mês. O modelo calcula 520 horas humanas após automação, contra 1.000 no contrafactual manual, e capacidade planejada de 1.280 horas/mês para 10 pessoas, 160 horas disponíveis e utilização-alvo de 80%.

Esses números são resultados simulados do modelo e não impactos observados em uma empresa.

## Limitações

O modelo mede somente capacidade humana. Não representa fila, prazo de atendimento, variação de produtividade individual, qualidade, custos, sistemas, orçamento ou outros gargalos. Dados sintéticos permitem demonstrar o método, não calibrar uma previsão real.

## Possíveis evoluções

Uma evolução poderia incorporar limites de sistemas, sazonalidade calibrada com dados autorizados, níveis de serviço e análises de sensibilidade. Qualquer uso de dados reais exigiria governança, documentação de origem e validação das regras de negócio.

## Uso de IA no desenvolvimento

O projeto foi desenvolvido com apoio de IA para estruturar código, testes e documentação. Fórmulas, entradas, limites e resultados foram definidos e verificados no repositório; esta descrição não atribui à IA etapas de coleta de dados reais, validação com empresa ou impactos de negócio.
