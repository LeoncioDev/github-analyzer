from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from dotenv import load_dotenv
from app.api.routes import router as api_router

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Corrigindo o caminho para frontend
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # sobe 3 níveis para o root do projeto
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        logging.error(f"Arquivo {index_path} não encontrado.")
        raise HTTPException(status_code=404, detail="Arquivo index.html não encontrado.")
    return FileResponse(index_path)

app.include_router(api_router)
