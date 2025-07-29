import os
import logging
from github import Github
from fastapi import HTTPException

def buscar_dados_github(username: str):
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
