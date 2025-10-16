import os
import logging
import random
from github import Github
from fastapi import HTTPException
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

def buscar_dados_github(username: str):
    """
    Busca dados básicos e informações dos repositórios de um usuário GitHub.
    """
    try:
        token = os.getenv("GITHUB_TOKEN")
        g = Github(token) if token else Github()

        user = g.get_user(username)

        nome = user.name or username
        bio = user.bio or "Sem biografia."
        seguidores = user.followers
        seguindo = user.following
        public_repos = user.public_repos

        repos = user.get_repos()
        linguagens = {}
        repos_detalhes = []

        for repo in repos:
            try:
                langs = repo.get_languages()
                for lang in langs:
                    linguagens[lang] = linguagens.get(lang, 0) + 1

                desc = repo.description or "Sem descrição"
                stars = repo.stargazers_count
                lang_str = ", ".join(langs.keys()) or "sem linguagem"
                detalhes = f"{repo.name} - {desc} ({lang_str}) - ⭐ {stars}"
                repos_detalhes.append(detalhes)

            except Exception as e:
                logging.warning(f"Erro ao processar repo {repo.name}: {e}")

        if not linguagens:
            raise HTTPException(status_code=404, detail="Não foi possível extrair linguagens do perfil.")

        return {
            "nome": nome,
            "bio": bio,
            "seguidores": seguidores,
            "seguindo": seguindo,
            "public_repos": public_repos,
            "linguagens": linguagens,
            "repos_detalhes": repos_detalhes,
        }

    except Exception as e:
        logging.error(f"Erro ao buscar dados do GitHub: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao acessar GitHub: {str(e)}")

def processar_usuario_com_filtros(user, min_stars: int, linguagens_filtro: Optional[List[str]] = None):
    """
    Processa dados do usuário com filtros, limitando repositórios e somando stars.
    Verifica se o usuário possui repositórios nas linguagens solicitadas.
    Retorna dict com dados ou None se não passar filtro.
    """
    try:
        total_stars = 0
        linguagens_usuario = {}
        repos_detalhes = []

        repos = user.get_repos()
        count = 0

        # Se não houver filtro de linguagens, aceita por padrão
        tem_linguagem_requerida = not linguagens_filtro

        for repo in repos:
            langs = repo.get_languages()

            # Verifica se o repo tem alguma das linguagens requisitadas
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

        # Se usuário não possui repositórios nas linguagens exigidas, rejeita
        if not tem_linguagem_requerida:
            return None

        if min_stars > 0 and total_stars < min_stars:
            return None

        dados_usuario = {
            "nome": user.name or user.login,
            "bio": user.bio or "Sem biografia.",
            "seguidores": user.followers,
            "seguindo": user.following,
            "public_repos": user.public_repos,
            "linguagens": linguagens_usuario,
            "repos_detalhes": repos_detalhes,
        }

        return dados_usuario

    except Exception as e:
        logging.warning(f"Erro ao buscar repositórios de {user.login}: {e}")
        return None

def buscar_dados_github_com_filtros(
    linguagens: Optional[List[str]] = None,
    min_repos: int = 0,
    min_stars: int = 0,
    min_followers: int = 0,
    atividade_recente: bool = False,  # Ignorado para otimizar
    localizacao: Optional[str] = None,
    keywords: Optional[str] = None,
    max_usuarios: int = 20
):
    """
    Busca usuários no GitHub aplicando filtros e retorna um usuário aleatório entre os que passam.
    """
    try:
        token = os.getenv("GITHUB_TOKEN")
        g = Github(token) if token else Github()

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
            futures = []
            for usuario in usuarios[:max_usuarios]:
                user = g.get_user(usuario.login)
                futures.append(executor.submit(processar_usuario_com_filtros, user, min_stars, linguagens))

            for future in as_completed(futures):
                resultado = future.result()
                if resultado:
                    usuarios_filtrados.append(resultado)

        if not usuarios_filtrados:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado com os filtros especificados.")

        usuario_escolhido = random.choice(usuarios_filtrados)
        return usuario_escolhido

    except Exception as e:
        logging.error(f"Erro ao buscar dados do GitHub com filtros: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao acessar GitHub: {str(e)}")
