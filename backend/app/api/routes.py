# app/api/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.models.schemas import GithubInput
from app.services.github_service import analisar_github

router = APIRouter()

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

@router.get("/", response_class=HTMLResponse)
async def root():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html não encontrado.")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))

@router.post("/analisar")
async def analisar(input: GithubInput):
    return await analisar_github(input.github_url)
