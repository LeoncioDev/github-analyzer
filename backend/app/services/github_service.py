# app/services/github_service.py
from fastapi import HTTPException
from github import Github
from app.templates.analysis_template import gerar_analise
import os
import logging

async def analisar_github(github_url: str):
    try:
        if "github.com" not in github_url:
            raise HTTPException(status_code=400, detail="URL inválida. Forneça uma URL do GitHub.")

        username = github_url.rstrip("/").split("/")[-1]
        logging.info(f"Analisando GitHub: {username}")

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
                logging.warning(f"Erro ao processar {repo.name}: {e}")

        if not linguagens:
            raise HTTPException(status_code=404, detail="Não foi possível extrair linguagens do perfil.")

        analise_html = gerar_analise(
            nome=nome,
            bio=bio,
            seguidores=seguidores,
            seguindo=seguindo,
            public_repos=public_repos,
            linguagens=linguagens,
            repos_detalhes=repos_detalhes
        )

        return {"analise": analise_html}

    except Exception as e:
        logging.error(f"Erro na análise: {e}")
        return {"erro": f"Erro ao analisar perfil: {str(e)}"}
