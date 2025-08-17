from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.github_service import buscar_dados_github
from app.services.gpt_service import gerar_analise_gpt
import logging

router = APIRouter()

# Novo modelo de entrada: agora usamos apenas o nome de usuário
class UsernameInput(BaseModel):
    username: str

@router.post("/analisar")
async def analisar(input: UsernameInput):
    try:
        username = input.username.strip()
        if not username:
            raise HTTPException(status_code=400, detail="Nome de usuário inválido.")

        logging.info(f"🔍 Analisando perfil GitHub: {username}")

        dados = buscar_dados_github(username)
        analise = gerar_analise_gpt(**dados)

        return {"analise": analise}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"❌ Erro na análise: {e}")
        return {"erro": f"Erro ao analisar perfil: {str(e)}"}
