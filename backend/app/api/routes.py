from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.github_service import buscar_dados_github
from app.services.gpt_service import gerar_analise_gpt
import logging

router = APIRouter()

class GithubInput(BaseModel):
    github_url: str

@router.post("/analisar")
async def analisar(input: GithubInput):
    try:
        if "github.com" not in input.github_url:
            raise HTTPException(status_code=400, detail="URL inválida, use um link do GitHub.")

        username = input.github_url.rstrip("/").split("/")[-1]
        logging.info(f"Analisando perfil GitHub: {username}")

        dados = buscar_dados_github(username)
        analise = gerar_analise_gpt(**dados)

        return {"analise": analise}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Erro na análise: {e}")
        return {"erro": f"Erro ao analisar perfil: {str(e)}"}
