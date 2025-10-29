import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

from app.api.routes import router as api_router

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Criação da aplicação FastAPI
app = FastAPI()

# Middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajuste do caminho para o diretório frontend
BASE_DIR = Path(__file__).resolve().parent       # backend/
PROJECT_ROOT = BASE_DIR.parent                   # github-analyzer-main/
FRONTEND_DIR = PROJECT_ROOT / "frontend"         # github-analyzer-main/frontend

print(f"Montando static em: {FRONTEND_DIR} (existe? {FRONTEND_DIR.exists()})")

# Montagem da pasta estática
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Rotas para os HTMLs principais
def serve_html(file_name: str):
    path = FRONTEND_DIR / file_name
    if not path.exists():
        logging.error(f"Arquivo {path} não encontrado.")
        raise HTTPException(status_code=404, detail=f"Arquivo {file_name} não encontrado.")
    return FileResponse(path)

@app.get("/", include_in_schema=False)
async def serve_index():
    return serve_html("index.html")

@app.get("/sobre", include_in_schema=False)
async def serve_sobre():
    return serve_html("sobre.html")

# Se no futuro quiser adicionar /contato ou outros HTMLs, basta criar a rota igual:
# @app.get("/contato", include_in_schema=False)
# async def serve_contato():
#     return serve_html("contato.html")

# Incluindo rotas da API
app.include_router(api_router)
