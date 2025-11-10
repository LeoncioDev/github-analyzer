from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.github_service import buscar_dados_github, buscar_dados_github_com_filtros
from app.services.gpt_service import gerar_analise_gpt
import logging
from urllib.parse import urlparse

router = APIRouter()

class UsernameInput(BaseModel):
    username: str
    contexto: str = "recrutamento"

class FiltrosInput(BaseModel):
    linguagens: Optional[List[str]] = []
    habilidades: Optional[List[str]] = []
    metodologias: Optional[List[str]] = []
    minRepos: Optional[int] = 0
    minStars: Optional[int] = 0
    minFollowers: Optional[int] = 0
    atividadeRecente: Optional[bool] = False
    localizacao: Optional[str] = None

def extrair_username_de_url(input_str: str) -> str:
    """Extrai o nome de usuário de uma URL do GitHub ou retorna a string se não for URL"""
    input_str = input_str.strip().rstrip('/')

    #Verifica se é uma URL
    if input_str.startswith("http://") or input_str.startswith("https://"):
        try:
            parsed_url = urlparse(input_str)
            if "github.com" in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 1 and path_parts[0]:
                    return path_parts[0] #Retorna a primeira parte do path
            #Se não for uma URL do GitHub válida, retorna None para dar erro
            return None
        except Exception:
            return None #Erro no parse da URL
    
    #Se não for URL, assume que é um username
    #Remove o @ caso o usuário digite
    return input_str.lstrip('@')

@router.post("/analisar")
async def analisar(input: UsernameInput):
    try:
        username = extrair_username_de_url(input.username)
        if not username:
            raise HTTPException(status_code=400, detail="URL ou nome de usuário inválido.")

        logging.info(f"🔍 Analisando perfil do GitHub: {username} (Contexto: {input.contexto})")

        #buscar_dados_github agora retorna também o readme_text
        dados = buscar_dados_github(username)

        #Passar os dados e o contexto para o serviço GPT
        analise = gerar_analise_gpt(**dados, contexto=input.contexto)

        return {"analise": analise}

    except HTTPException as he:
        #Repassa exceções HTTP (como o 404 de usuário não encontrado)
        raise he
    except Exception as e:
        logging.error(f"❌ Erro na análise: {e}")
        #Usar HTTPException para enviar um erro JSON padronizado
        raise HTTPException(status_code=500, detail=f"Erro interno ao analisar perfil: {str(e)}")

@router.post("/analisar-com-filtros")
async def analisar_com_filtros(filtros: FiltrosInput):
    try:
        logging.info(f"🔍 Analisando perfil do GitHub com filtros: {filtros}")

        if not any([
            filtros.linguagens,
            filtros.habilidades,
            filtros.metodologias,
            filtros.minRepos > 0,
            filtros.minStars > 0,
            filtros.minFollowers > 0,
            filtros.atividadeRecente,
            filtros.localizacao
        ]):
            raise HTTPException(status_code=400, detail="Pelo menos um filtro deve ser fornecido.")
        
        palavras_chave = filtros.habilidades + filtros.metodologias
        keywords = " ".join(palavras_chave) if palavras_chave else None

        dados = buscar_dados_github_com_filtros(
            linguagens=filtros.linguagens,
            min_repos=filtros.minRepos,
            min_stars=filtros.minStars,
            min_followers=filtros.minFollowers,
            atividade_recente=filtros.atividadeRecente,
            localizacao=filtros.localizacao,
            keywords=keywords,
        )

        analise = gerar_analise_gpt(**dados, contexto="recrutamento")

        card_style = "border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px;"

        analise_com_filtro = f"""
        <div style="{card_style}">
            <p><strong>🔎 Perfil encontrado: <a href="{dados['html_url']}" target="_blank" style="color: 58a6ff; text-decoration: none; ">@{dados['login']}</a></strong></p>
            <p style="margin-top: 5px;">(Respeitando os filtros aplicados)</p>
        </div>
        {analise}
        """
        return {"analise": analise_com_filtro}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"❌ Erro na análise com filtros: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao analisar perfil com filtros: {str(e)}")

