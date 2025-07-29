import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from dotenv import load_dotenv

# Carregar variáveis do .env o mais cedo possível
load_dotenv()

print("OPENAI_API_KEY carregada no ambiente:", os.getenv("OPENAI_API_KEY"))

from app.api.routes import router as api_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajuste do caminho para o diretório frontend:
#  - __file__ aponta para backend/main.py
#  - parent é backend/
#  - parent.parent é github-analyzer-main/
BASE_DIR = Path(__file__).resolve().parent       # backend/
PROJECT_ROOT = BASE_DIR.parent                   # github-analyzer-main/
FRONTEND_DIR = PROJECT_ROOT / "frontend"         # github-analyzer-main/frontend

print(f"Montando static em: {FRONTEND_DIR} (existe? {FRONTEND_DIR.exists()})")

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        logging.error(f"Arquivo {index_path} não encontrado.")
        raise HTTPException(status_code=404, detail="Arquivo index.html não encontrado.")
    return FileResponse(index_path)

app.include_router(api_router)
