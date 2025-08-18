from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.github_service import buscar_dados_github, buscar_dados_github_com_filtros
from app.services.gpt_service import gerar_analise_gpt
import logging

router = APIRouter()

class UsernameInput(BaseModel):
    username: str

class FiltrosInput(BaseModel):
    linguagens: Optional[List[str]] = []
    habilidades: Optional[List[str]] = []
    competencias: Optional[List[str]] = []
    metodologias: Optional[List[str]] = []
    minRepos: Optional[int] = 0
    minStars: Optional[int] = 0
    minFollowers: Optional[int] = 0
    atividadeRecente: Optional[bool] = False
    localizacao: Optional[str] = None

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

@router.post("/analisar-com-filtros")
async def analisar_com_filtros(filtros: FiltrosInput):
    try:
        logging.info(f"🔍 Buscando candidatos com filtros: {filtros}")

        # Verifica se ao menos um filtro foi preenchido
        if not any([
            filtros.linguagens,
            filtros.habilidades,
            filtros.competencias,
            filtros.metodologias,
            filtros.minRepos > 0,
            filtros.minStars > 0,
            filtros.minFollowers > 0,
            filtros.atividadeRecente,
            filtros.localizacao
        ]):
            raise HTTPException(status_code=400, detail="É necessário informar ao menos um filtro válido para busca.")

        # Concatena todas as palavras-chave selecionadas
        palavras_chave = filtros.habilidades + filtros.competencias + filtros.metodologias
        keywords_str = " ".join(palavras_chave) if palavras_chave else None

        dados = buscar_dados_github_com_filtros(
            linguagens=filtros.linguagens,
            min_repos=filtros.minRepos,
            min_stars=filtros.minStars,
            min_followers=filtros.minFollowers,
            atividade_recente=filtros.atividadeRecente,
            localizacao=filtros.localizacao,
            keywords=keywords_str,
        )

        analise = gerar_analise_gpt(**dados)

        return {"analise": analise}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"❌ Erro na análise com filtros: {e}")
        return {"erro": f"Erro ao analisar com filtros: {str(e)}"}
