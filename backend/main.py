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

# Caminho do frontend
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
logging.info(f"Montando static em: {FRONTEND_DIR} (existe? {FRONTEND_DIR.exists()})")

# Monta arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

# Função para servir qualquer página HTML
def serve_html(filename: str):
    file_path = FRONTEND_DIR / filename
    if not file_path.exists():
        logging.error(f"Arquivo {file_path} não encontrado.")
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado.")
    return FileResponse(file_path)

# Rotas das páginas
@app.get("/", include_in_schema=False)
async def home():
    return serve_html("index.html")

@app.get("/sobre", include_in_schema=False)
async def sobre():
    return serve_html("sobre.html")


# API
app.include_router(api_router)
