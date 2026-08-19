# Sports Journal Crew

Aplicação local que pesquisa notícias esportivas com CrewAI e entrega o relatório HTML gerado.

## Pré-requisitos

- Python compatível com o projeto e [uv](https://docs.astral.sh/uv/)
- Node.js 20+ e npm
- Variáveis exigidas pela CrewAI configuradas no arquivo `.env` (não inclua segredos no repositório)

## Executar localmente

Instale as dependências Python e inicie a API em um terminal:

```powershell
uv sync
uv run uvicorn backend.main:app --reload
```

A API fica disponível em `http://127.0.0.1:8000`; a documentação interativa está em `http://127.0.0.1:8000/docs`.

Em outro terminal, inicie o frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. O frontend usa `http://127.0.0.1:8000` por padrão. Para trocar a URL, copie `frontend/.env.example` para `frontend/.env` e defina `VITE_API_URL`.

## Uso

Informe um tema e selecione **Gerar relatório**. A página mantém a requisição aberta até a crew terminar, sem timeout artificial, mostra o tempo decorrido e apresenta o HTML retornado em uma prévia isolada. O botão de download salva exatamente o mesmo conteúdo como `report.html`.

A API expõe `POST /run` com este contrato:

```json
{ "tema": "futebol brasileiro" }
```

Após a execução, a resposta é:

```json
{ "report_html": "<html>...</html>" }
```

As execuções são serializadas porque todas escrevem no mesmo `report.html`. A origem `http://localhost:5173` é permitida por CORS para o Vite local.

## Verificação

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_main -v
cd frontend
npm run build
```

## Estrutura

- `agents/` — definições dos agentes em JSONC
- `crew.jsonc` — tarefas e configuração da crew
- `backend/` — API FastAPI
- `frontend/` — interface Vite + React
- `tests/` — testes isolados da API
- `knowledge/` — arquivos de conhecimento dos agentes
- `tools/` — ferramentas Python personalizadas
