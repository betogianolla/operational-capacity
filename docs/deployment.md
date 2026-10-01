# Publicação da demonstração

## Configuração

- Plataforma: Streamlit Community Cloud, modalidade pública gratuita.
- URL: <https://operational-capacity.streamlit.app/>.
- Repositório: `betogianolla/operational-capacity`.
- Branch: `main`.
- Arquivo principal: `app.py`.
- Python: 3.13 foi a versão solicitada para a implantação. A versão efetivamente selecionada/ativa não foi confirmada por inspeção das configurações ou logs do Cloud.
- Dependências de execução: `requirements.txt` (`streamlit==1.64.0`, `duckdb==1.5.6`).

O repositório contém `data/monthly_capacity.csv`, `data/interactions.csv` e os metadados sintéticos necessários à demonstração. A aplicação resolve os caminhos a partir de `app.py`; não depende de caminho local do Windows, segredo ou variável de ambiente.

## Verificações

- **Relato do autor (2026-10-01):** a aplicação abriu sem exigir login; o autor confirmou o funcionamento do histórico, do simulador, das projeções e dos downloads.
- **Resposta HTTP nesta revisão:** uma requisição GET com redirecionamento e cookies em memória recebeu HTTP 200 e retornou o shell HTML do Streamlit. Essa resposta não comprova que a interface executou seus fluxos.
- **Verificação interativa pelo agente:** não realizada, pois não havia ferramenta de navegador interativo disponível.
- **Python/Linux:** a execução efetiva em Python 3.13/Linux não foi inspecionada diretamente. A configuração solicitada foi Python 3.13, mas os logs/configurações do Cloud não estavam acessíveis nesta revisão.
- **Testes automatizados:** não repetidos para documentar a publicação. Os resultados anteriores permanecem registrados em `docs/review.md`.

## Limites e pendências

A demonstração pública foi confirmada pelo autor para uso sem login e para os fluxos principais. Screenshots para o repositório e publicação no LinkedIn ainda não foram realizados. A versão efetiva do Python poderá ser confirmada nos detalhes/logs da aplicação no workspace do Streamlit Community Cloud.
