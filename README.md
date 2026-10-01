# Simulador de Capacidade Operacional

Aplicação local para explorar quanto uma operação baseada em clientes ativos pode crescer com a equipe disponível e como a automação altera sua capacidade humana.

## Problema de negócio

Gestores de operações precisam relacionar volume, tempo de atendimento, automação e disponibilidade de equipe para entender limites de capacidade. O simulador compara um contrafactual manual com o processo automatizado, sem transformar horas liberadas em economia financeira ou decisões de pessoal.

## O que a aplicação permite decidir

- Visualizar demanda, utilização e horas humanas do histórico sintético.
- Comparar capacidade manual e automatizada para premissas explícitas.
- Identificar quando a utilização supera a meta ou as horas requeridas superam as disponíveis.
- Explorar crescimento composto da base por três anos e o déficit estimado de pessoas.

Essas saídas apoiam discussão de capacidade humana. Não são previsão validada, recomendação de contratação/demissão ou estimativa de retorno financeiro.

## Funcionalidades

- Histórico mensal de 24 meses de dados `SYNTHETIC_FICTITIOUS`.
- Simulador de premissas com validação de limites e confirmação para automação acima da elegibilidade observada.
- Comparação de horas, utilização, pessoas necessárias, demanda máxima sustentável, margem de crescimento e capacidade liberada equivalente.
- Projeções compostas de ano-base mais três anos.
- Downloads CSV do histórico consolidado e dos cenários hipotéticos, com origem e hipóteses identificadas.

## Stack e arquitetura

Python 3.14.3 concentra o domínio e o gerador. DuckDB 1.5.6 consolida os CSVs sintéticos via SQL. Streamlit 1.64.0 apresenta a interface. pytest 9.1.1 valida regras e fluxos da interface.

```text
CSVs sintéticos → consultas DuckDB → motor Python puro → Streamlit / CSVs em memória
```

As fórmulas estão em `src/operational_capacity/calculations.py`; a interface não as reimplementa. Consulte [docs/data.md](docs/data.md) e [docs/interface.md](docs/interface.md) para detalhes.

## Instalação e execução no Windows

Pré-requisito: Python **3.14.3** instalado com o lançador do Windows (`py`). Em um terminal novo, na raiz do projeto:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\operational_capacity\synthetic_data.py --output-dir data
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m streamlit run app.py
```

O último comando abre a interface local e não depende de `PYTHONPATH` ou de um ambiente virtual previamente ativado. Se os dados estiverem ausentes, a tela também informa o comando de geração.

## Preparação para Linux e hospedagem

O ponto de entrada é `app.py`, na raiz do repositório. A aplicação localiza `src/` e `data/` a partir do próprio arquivo com `pathlib`; não depende de `E:\\`, de separadores do Windows, de variáveis locais ou de credenciais.

Para uma hospedagem Linux, recomenda-se **Python 3.13**. O projeto aceita Python 3.11 a 3.14 (`pyproject.toml`), enquanto as versões fixadas de Streamlit e DuckDB declaram suporte a Python 3.13. Em um ambiente Linux novo, instale apenas as dependências de execução e inicie a partir da raiz clonada:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Os CSVs sintéticos da demonstração (`data/monthly_capacity.csv`, `data/interactions.csv` e seus metadados) são versionados. Assim, eles já estarão presentes em um clone novo e não são regenerados a cada interação. Caso sejam removidos, a mensagem da aplicação informa o comando reproduzível `python src/operational_capacity/synthetic_data.py --output-dir data`.

Esta preparação não configura hospedagem, segredo, serviço externo nem variável de ambiente.

## Exemplo numérico verificado

O motor foi executado e testado com 10.000 clientes ativos, 0,2 atendimentos por cliente/mês, 30 min manuais, 60% de automação, 5 min residuais, 10% de retrabalho de 10 min, 10 pessoas, 160 h por pessoa e utilização-alvo de 80%.

Resultados simulados: 2.000 atendimentos/mês; 1.000 h manuais; 520 h automatizadas; 480 h liberadas; utilização de 62,5% versus 32,5%; 8 versus 5 pessoas necessárias; e capacidade máxima de 2.560 versus 4.923,076923 atendimentos/mês. O equivalente contínuo de capacidade liberada é 3,75 pessoas; a diferença entre dimensionamentos inteiros é 3 pessoas — métricas distintas.

## Dados sintéticos e IA no desenvolvimento

Os dados são determinísticos, fictícios e marcados como `SYNTHETIC_FICTITIOUS`; não representam empresas, pessoas ou impactos reais. A semente e as distribuições estão documentadas em [docs/data.md](docs/data.md).

IA generativa foi usada como ferramenta de apoio ao desenvolvimento deste projeto, incluindo elaboração e refinamento de código, testes e documentação. Os resultados registrados são os efetivamente executados nas verificações documentadas; a IA não fornece evidência de impacto operacional real.

## Hipóteses e limitações

- O modelo mede somente capacidade humana.
- Sistemas, orçamento, qualidade, filas, prazos e outros gargalos não são modelados.
- O contrafactual manual assume que o tempo manual médio se aplicaria aos atendimentos automatizados.
- Médias sem observações permanecem ausentes; quando necessárias, usam premissas sintéticas explícitas.
- Capacidade equivalente não é economia realizada, contratação evitada ou demissão.

## Verificação atual

Consulte [docs/review.md](docs/review.md) para o parecer de revisão, verificações automatizadas e limites da inspeção visual.
