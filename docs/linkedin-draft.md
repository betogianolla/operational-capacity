# Rascunho de publicação para LinkedIn

Como avaliar se uma equipe consegue absorver o crescimento da demanda e quanto a automação muda sua capacidade operacional?

Essa foi a pergunta de negócio que escolhi transformar em uma ferramenta de apoio à decisão. Orientei e conduzi o projeto: defini o problema, delimitei o que o simulador deveria ajudar a analisar, acompanhei as entregas e solicitei refinamentos na apresentação e na interpretação dos indicadores.

Duas decisões analíticas foram centrais. Primeiro, separar elegibilidade para automação de adoção efetivamente simulada: uma atividade elegível não significa que já foi automatizada, e cenários acima desse limite precisam declarar a hipótese de expansão. Segundo, modelar o retrabalho como tempo humano adicional esperado ao tempo residual, evitando contá-lo duas vezes.

No caso de referência — inteiramente simulado — considerei 10.000 clientes ativos, frequência de 0,2 atendimento por cliente/mês e uma equipe de 10 pessoas, com 160 horas disponíveis por pessoa/mês e utilização-alvo de 80%. Comparei 30 minutos por atendimento manual com automação de 60%, 5 minutos residuais e retrabalho em 10% dos automatizados, com 10 minutos adicionais por ocorrência. O modelo calculou 1.000 horas mensais no processo manual e 520 no cenário automatizado: uma diferença estimada de 480 horas humanas. A capacidade sustentável simulada passou de cerca de 2.560 para 4.923 atendimentos/mês, aumento de aproximadamente 92,3%. Isso não é economia financeira realizada nem prova de efeito causal.

A solução combina Python no motor de cálculo, SQL com DuckDB para consolidar o histórico e Streamlit na interface de cenários e exportação. Dados e resultados são sintéticos; as projeções são cenários determinísticos, não uma previsão validada.

Ferramentas de IA apoiaram a estruturação do modelo, a implementação e a revisão técnica, sob minha orientação.

Demonstração: https://operational-capacity.streamlit.app/

Repositório: https://github.com/betogianolla/operational-capacity
