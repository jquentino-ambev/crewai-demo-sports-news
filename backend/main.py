from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from crewai.project.crew_loader import load_crew

ROOT = Path(__file__).resolve().parent.parent
CREW_DEFINITION = ROOT / "crew.jsonc"
REPORT_FILE = ROOT / "report.html"
_run_lock = Lock()

app = FastAPI(title="Sports Journal Crew API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    tema: str = Field(min_length=1, description="Tema esportivo a pesquisar")


class RunResponse(BaseModel):
    report_html: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
def run_crew(request: RunRequest) -> RunResponse:
    try:
        with _run_lock:
            crew, default_inputs = load_crew(CREW_DEFINITION)
            crew.kickoff(inputs={**default_inputs, "tema": request.tema})
            try:
                report_html = REPORT_FILE.read_text(encoding="utf-8")
            except FileNotFoundError as exc:
                raise HTTPException(status_code=500, detail="A crew terminou sem gerar report.html.") from exc
            except OSError as exc:
                raise HTTPException(status_code=500, detail=f"Não foi possível ler report.html: {exc}") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao executar a crew: {exc}") from exc

    return RunResponse(report_html=report_html)
