from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agents.workflow import run_investigation
from .config import settings
from .llm import llm_enabled
from .models import InvestigationRequest, InvestigationResult
from .tools.data_sources import DataContext

app = FastAPI(title="Procurement Fraud Investigator")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

# in-memory store — TODO: persist to PostgreSQL (see ROADMAP.md)
_results: dict[str, InvestigationResult] = {}


@app.get("/api/health")
def health():
    return {"ok": True, "llm": "nvidia-nim" if llm_enabled() else "offline-mock", "data_backend": settings.data_backend}


@app.get("/api/scopes")
def scopes():
    ctx = DataContext.load()
    return {"agencies": ["all", *sorted(ctx.tenders.agency.unique())]}


@app.post("/api/investigations", response_model=InvestigationResult)
def create_investigation(req: InvestigationRequest):
    result = run_investigation(req)
    _results[result.id] = result
    return result


@app.get("/api/investigations/{inv_id}", response_model=InvestigationResult)
def get_investigation(inv_id: str):
    if inv_id not in _results:
        raise HTTPException(404, "Investigation not found")
    return _results[inv_id]
