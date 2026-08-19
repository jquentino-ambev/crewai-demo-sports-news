# Status do projeto

## Objetivo

Aplicacao local com CrewAI para pesquisar noticias esportivas sobre um tema, gerar `report.html` e exibi-lo no navegador.

## Implementado

- `crew.jsonc` define uma execucao sequencial com dois agentes:
  - `especialista_em_pesquisar_noti` pesquisa noticias com `SerperDevTool` e `ScrapeWebsiteTool`.
  - `redator` produz `report.html` com `FileWriterTool`.
- Os agentes usam o LLM configurado em `llm_proxy.py`. As variaveis necessarias ficam no `.env`; nunca registrar valores delas neste arquivo.
- A API FastAPI esta em `backend/main.py`:
  - `GET /health` retorna `{"status": "ok"}`.
  - `POST /run` recebe `{"tema": "..."}`, executa a crew e responde `{"report_html": "<html>...</html>"}`.
  - O `Lock` protege tanto a execucao quanto a leitura de `report.html`, para que cada resposta devolva o arquivo gerado pela propria solicitacao.
  - CORS permite somente `http://localhost:5173`, a origem local do Vite.
- O frontend Vite + React esta em `frontend/`:
  - recebe o tema, desabilita os controles durante a execucao e mostra o tempo decorrido;
  - nao define timeout artificial para a requisicao;
  - mostra erros da API, renderiza o HTML em `iframe` isolado e baixa o mesmo conteudo como `report.html`;
  - usa `VITE_API_URL`, com padrao `http://127.0.0.1:8000`. Consulte `frontend/.env.example`.

## Como executar

Em um terminal, inicie a API:

```powershell
uv sync
uv run uvicorn backend.main:app --reload
```

Em outro terminal, inicie o frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. A documentacao da API fica em `http://127.0.0.1:8000/docs`.

## Validacao feita

- `python -m unittest tests.test_main -v`: cobre retorno do relatorio, tema invalido, falha da crew, ausencia do arquivo e serializacao pelo `Lock` sem chamadas externas.
- `npm run build` em `frontend/`: build de producao concluido.
- A crew real nao deve ser executada como teste automatico: ela chama busca/LLM externos e sobrescreve `report.html`.

## Limites atuais

- A requisicao e sincrona e pode permanecer aberta por varios minutos.
- Nao ha autenticacao, fila, polling, cancelamento ou historico de execucoes; isso e adequado ao uso local atual.
- Para producao, configure qualquer proxy ou gateway com timeout maior que a duracao maxima esperada da crew.
- Preserve alteracoes locais nao relacionadas em `backend/main.py` e `report.html` ao continuar o trabalho.
