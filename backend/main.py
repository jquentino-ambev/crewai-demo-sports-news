from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from crewai.project.crew_loader import load_crew

ROOT = Path(__file__).resolve().parent.parent
CREW_DEFINITION = ROOT / "crew.jsonc"
REPORT_FILE = ROOT / "report.html"
_run_lock = Lock()

app = FastAPI(title="Sports Journal Crew API")


class RunRequest(BaseModel):
    tema: str = Field(min_length=1, description="Tema esportivo a pesquisar")


class RunResponse(BaseModel):
    result: Any
    report_file: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
def run_crew(request: RunRequest) -> RunResponse:
    try:
        with _run_lock:
            crew, default_inputs = load_crew(CREW_DEFINITION)
            result = crew.kickoff(inputs={**default_inputs, "tema": request.tema})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return RunResponse(result=getattr(result, "raw", str(result)), report_file=str(REPORT_FILE))
