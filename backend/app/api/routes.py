import logging
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.github_service import buscar_dados_github, buscar_dados_github_com_filtros
from app.services.gpt_service import gerar_analise_gpt, gerar_ranking_completo
from app.models.schemas import (
    RankingInput, 
    CandidateDataForRanking, 
    UserInput, 
    FiltrosInput
)

router = APIRouter()
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# ENDPOINT DE RANKING DE MÚLTIPLOS CANDIDATOS
# ==============================================================================
@router.post("/ranking-vaga")
async def rankear_candidatos(input: RankingInput):
    logging.info(f"🚀 Iniciando ranking para {len(input.candidateUrls)} candidatos.")

    candidatos_analisados: List[CandidateDataForRanking] = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for url_or_username in input.candidateUrls:
            futures.append(executor.submit(
                processar_candidato_para_ranking, 
                url_or_username, 
                input.jobDescription
            ))
        
        for future in as_completed(futures):
            try:
                candidato_analisado = future.result() 
                if candidato_analisado:
                    candidatos_analisados.append(candidato_analisado)
            except HTTPException as he:
                logging.warning(f"Erro ao processar candidato: {he.detail}. Ignorando este candidato.")
            except Exception as e:
                logging.error(f"Erro inesperado ao processar candidato: {e}. Ignorando.")

    if not candidatos_analisados:
        raise HTTPException(status_code=404, detail="Nenhum candidato pôde ser analisado com sucesso.")
    
    try:
        logging.info(f"✨ Gerando ranking final da vaga com {len(candidatos_analisados)} análises.")
        ranking_html = gerar_ranking_completo(
            job_description=input.jobDescription,
            candidatos_analisados=candidatos_analisados
        )
        return {"analise": ranking_html}
    except Exception as e:
        logging.error(f"❌ Erro ao gerar ranking final: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking final: {str(e)}")

# Função auxiliar para processar um único candidato (executada em thread)
def processar_candidato_para_ranking(username_or_url: str, job_description: str) -> Optional[CandidateDataForRanking]:
    try:
        username = username_or_url
        if "github.com/" in username_or_url:
            username = username_or_url.split("github.com/")[-1].split("/")[0]

        dados_github = buscar_dados_github(username)
        
        analise_candidato_html = gerar_analise_gpt(
            nome=dados_github['nome'],
            login=dados_github['login'],
            html_url=dados_github['html_url'],
            bio=dados_github['bio'],
            seguidores=dados_github['seguidores'],
            seguindo=dados_github['seguindo'],
            public_repos=dados_github['public_repos'],
            linguagens=dados_github['linguagens'],
            repos_detalhes=dados_github['repos_detalhes'],
            readme_text=dados_github['readme_text'],
            contexto="recrutamento"
        )
        
        return CandidateDataForRanking(
            username=dados_github['login'],
            nome=dados_github['nome'],
            html_url=dados_github['html_url'],
            analise_html=analise_candidato_html
        )
    except HTTPException as he:
        logging.warning(f"Erro HTTP ao buscar/analisar {username_or_url}: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Erro ao processar {username_or_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao processar {username_or_url}: {str(e)}")


# ==============================================================================
# ENDPOINT DE ANÁLISE DE PERFIL INDIVIDUAL
# ==============================================================================
@router.post("/analisar-perfil")
async def analisar_perfil(user_input: UserInput):
    try:
        username = user_input.usernameOrUrl
        if "github.com/" in username:
            username = username.split("github.com/")[-1].split("/")[0]

        dados_github = buscar_dados_github(username)
        
        analise_html = gerar_analise_gpt(
            nome=dados_github['nome'],
            login=dados_github['login'],
            html_url=dados_github['html_url'],
            bio=dados_github['bio'],
            seguidores=dados_github['seguidores'],
            seguindo=dados_github['seguindo'],
            public_repos=dados_github['public_repos'],
            linguagens=dados_github['linguagens'],
            repos_detalhes=dados_github['repos_detalhes'],
            readme_text=dados_github['readme_text'],
            contexto=user_input.contexto
        )
        return {"analise": analise_html}
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"❌ Erro ao analisar perfil: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao acessar GitHub: {str(e)}")


# ==============================================================================
# ENDPOINT DE ANÁLISE COM FILTROS AVANÇADOS
# ==============================================================================
@router.post("/analisar-com-filtros")
async def analisar_com_filtros(filtros: FiltrosInput):
    try:
        logging.info(f"🔍 Buscando candidatos com filtros: {filtros}")

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
            raise HTTPException(status_code=400, detail="É necessário informar ao menos um filtro válido para busca.")

        palavras_chave = filtros.habilidades + filtros.metodologias
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

        analise = gerar_analise_gpt(**dados, contexto="recrutamento")

        card_style = "border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px;"

        analise_com_filtro = f"""
        <div style="{card_style}">
            <p><strong>🔎 Perfil encontrado: <a href="{dados['html_url']}" target="_blank" style="color: #58a6ff; text-decoration: none;">@{dados['login']}</a></strong></p>
            <p style="margin-top: 5px;">(Respeitando os filtros selecionados)</p>
        </div>
        {analise}
        """

        return {"analise": analise_com_filtro}

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"❌ Erro na análise com filtros: {e}")
        return {"erro": f"Erro ao analisar com filtros: {str(e)}"}
