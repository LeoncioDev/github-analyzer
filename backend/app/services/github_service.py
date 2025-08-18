import os
import logging
from github import Github
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Optional, List

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


def buscar_dados_github_com_filtros(
    linguagens: Optional[List[str]] = None,
    min_repos: int = 0,
    min_stars: int = 0,
    min_followers: int = 0,
    atividade_recente: bool = False,
    localizacao: Optional[str] = None,
    keywords: Optional[str] = None,
    max_usuarios: int = 5
):
    """
    Busca usuários no GitHub aplicando filtros e retorna o mais adequado.
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

        data_limite = datetime.utcnow() - timedelta(days=90) if atividade_recente else None

        for usuario in usuarios[:max_usuarios]:
            user = g.get_user(usuario.login)

            # Atividade recente
            if atividade_recente:
                try:
                    eventos = user.get_events()
                    ativo = any(evento.created_at > data_limite for evento in eventos)
                    if not ativo:
                        continue
                except Exception as e:
                    logging.warning(f"Erro ao verificar eventos de {user.login}: {e}")
                    continue

            # Soma de estrelas
            total_stars = 0
            linguagens_usuario = {}
            repos_detalhes = []

            try:
                for repo in user.get_repos():
                    total_stars += repo.stargazers_count

                    langs = repo.get_languages()
                    for lang in langs:
                        linguagens_usuario[lang] = linguagens_usuario.get(lang, 0) + 1

                    desc = repo.description or "Sem descrição"
                    lang_str = ", ".join(langs.keys()) or "sem linguagem"
                    detalhes = f"{repo.name} - {desc} ({lang_str}) - ⭐ {repo.stargazers_count}"
                    repos_detalhes.append(detalhes)

                    if min_stars > 0 and total_stars >= min_stars:
                        break

            except Exception as e:
                logging.warning(f"Erro ao buscar repositórios de {user.login}: {e}")
                continue

            if min_stars > 0 and total_stars < min_stars:
                continue

            dados_usuario = {
                "nome": user.name or user.login,
                "bio": user.bio or "Sem biografia.",
                "seguidores": user.followers,
                "seguindo": user.following,
                "public_repos": user.public_repos,
                "linguagens": linguagens_usuario,
                "repos_detalhes": repos_detalhes,
            }

            usuarios_filtrados.append(dados_usuario)

        if not usuarios_filtrados:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado com os filtros especificados.")

        return usuarios_filtrados[0]

    except Exception as e:
        logging.error(f"Erro ao buscar dados do GitHub com filtros: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao acessar GitHub: {str(e)}")
