# github_service.py
import os
import logging
import random
from github import Github, UnknownObjectException
from fastapi import HTTPException
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Carrega o .env
load_dotenv()

# Pega o token do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logging.error("❌ GITHUB_TOKEN não encontrado. Verifique seu arquivo .env")
    raise ValueError("GITHUB_TOKEN não definido no ambiente")

# Inicializa o cliente do GitHub
g = Github(GITHUB_TOKEN)

def buscar_dados_github(username: str):
    """ Busca dados básicos, README do perfil e informações dos repositórios."""
    try:
        user = g.get_user(username)

        nome = user.name or username
        bio = user.bio or "Sem biografia."
        seguidores = user.followers
        seguindo = user.following
        public_repos = user.public_repos

        # --- Buscar README do Perfil ---
        readme_text = ""
        try:
            readme_repo = user.get_repo(username)
            readme_content = readme_repo.get_readme().decoded_content.decode('utf-8')
            readme_text = readme_content
            logging.info(f"✅ README do perfil de {username} encontrado.")
        except UnknownObjectException:
            logging.warning(f"README de perfil de {username} não encontrado.")
            readme_text = "Nenhum README de perfil público encontrado."
        except Exception as e:
            logging.warning(f"Erro ao tentar buscar README do perfil de {username}: {e}")
            readme_text = "Erro ao processar README do perfil."
        # ----------

        repos = user.get_repos()
        linguagens = {}
        repos_detalhes = []

        for repo in repos:
            try:
                if repo.name == username:
                    continue
                    
                langs = repo.get_languages()
                for lang in langs:
                    linguagens[lang] = linguagens.get(lang, 0) + 1

                desc = repo.description or "Sem descrição"
                stars = repo.stargazers_count
                lang_str = ", ".join(langs.keys()) or "sem linguagem"

                # --- Verificação de README do repositório ---
                readme_info = ""
                try:
                    repo.get_readme()
                    readme_info = "✅ README"
                except UnknownObjectException:
                    readme_info = "❌ Sem README"
                # --- FIM DA VERIFICAÇÃO ---
                
                detalhes = f"{repo.name} ({lang_str}) - {readme_info} - ⭐ {stars} - {desc}"
                repos_detalhes.append(detalhes)

            except Exception as e:
                logging.warning(f"Erro ao processar repo {repo.name}: {e}")

        if not linguagens and not repos_detalhes:
             logging.warning(f"Nenhuma linguagem ou repositório (além do README) encontrado para {username}.")
             
        return {
            "nome": nome,
            "bio": bio,
            "seguidores": seguidores,
            "seguindo": seguindo,
            "public_repos": public_repos,
            "linguagens": linguagens,
            "repos_detalhes": repos_detalhes,
            "readme_text": readme_text,
        }

    except UnknownObjectException:
        logging.error(f"Usuário GitHub '{username}' não encontrado.")
        raise HTTPException(status_code=404, detail=f"Usuário GitHub '{username}' não encontrado.")
    except Exception as e:
        logging.error(f"Erro ao buscar dados do GitHub: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao acessar GitHub: {str(e)}")

def processar_usuario_com_filtros(user, min_stars: int, linguagens_filtro: Optional[List[str]] = None):
    """Processa dados do usuário com filtros, limitando repositórios e somando stars."""
    try:
        total_stars = 0
        linguagens_usuario = {}
        repos_detalhes = []

        repos = user.get_repos()
        count = 0
        tem_linguagem_requerida = not linguagens_filtro

        for repo in repos:
            langs = repo.get_languages()

            if linguagens_filtro:
                if any(lang.lower() in (l.lower() for l in langs.keys()) for lang in linguagens_filtro):
                    tem_linguagem_requerida = True

            total_stars += repo.stargazers_count

            for lang in langs:
                linguagens_usuario[lang] = linguagens_usuario.get(lang, 0) + 1

            desc = repo.description or "Sem descrição"
            lang_str = ", ".join(langs.keys()) or "sem linguagem"
            detalhes = f"{repo.name} - {desc} ({lang_str}) - ⭐ {repo.stargazers_count}"
            repos_detalhes.append(detalhes)

            count += 1
            if count >= 10 or (min_stars > 0 and total_stars >= min_stars):
                break

        if not tem_linguagem_requerida or (min_stars > 0 and total_stars < min_stars):
            return None

        return {
            "nome": user.name or user.login,
            "login": user.login,
            "html_url": user.html_url,
            "bio": user.bio or "Sem biografia.",
            "seguidores": user.followers,
            "seguindo": user.following,
            "public_repos": user.public_repos,
            "linguagens": linguagens_usuario,
            "repos_detalhes": repos_detalhes,
            # Adicionado para manter a compatibilidade com o gpt_service
            "readme_text": f"README do perfil de {user.login} não buscado (análise de filtro)."
        }

    except Exception as e:
        logging.warning(f"Erro ao buscar repositórios de {user.login}: {e}")
        return None

def buscar_dados_github_com_filtros(
    linguagens: Optional[List[str]] = None,
    min_repos: int = 0,
    min_stars: int = 0,
    min_followers: int = 0,
    atividade_recente: bool = False,
    localizacao: Optional[str] = None,
    keywords: Optional[str] = None,
    max_usuarios: int = 20
):
    """Busca usuários aplicando filtros e retorna um usuário aleatório entre os que passam."""
    try:
        query_parts = []

        if linguagens:
            query_parts.append(" ".join(f"language:{ling}" for ling in linguagens))
        if min_repos > 0:
            query_parts.append(f"repos:>={min_repos}")
        if min_followers > 0:
            query_parts.append(f"followers:>={min_followers}")
        if localizacao:
            query_parts.append(f"location:{localizacao}")
        if keywords:
            query_parts.append(keywords)

        query = " ".join(query_parts).strip()

        if not query:
            raise HTTPException(status_code=400, detail="Filtros insuficientes para busca.")

        logging.info(f"📡 Buscando usuários com query: {query}")

        usuarios = g.search_users(query)
        usuarios_filtrados = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(processar_usuario_com_filtros, g.get_user(u.login), min_stars, linguagens)
                       for u in usuarios[:max_usuarios]]

            for future in as_completed(futures):
                resultado = future.result()
                if resultado:
                    usuarios_filtrados.append(resultado)

        if not usuarios_filtrados:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado com os filtros especificados.")

        return random.choice(usuarios_filtrados)

    except Exception as e:
        logging.error(f"Erro ao buscar dados do GitHub com filtros: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao acessar GitHub: {str(e)}")
