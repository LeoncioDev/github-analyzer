from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from github import Github
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

load_dotenv()

app = FastAPI()

logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "../frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

class GithubInput(BaseModel):
    github_url: str

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# NOVA VERSÃO DA FUNÇÃO DE ANÁLISE — muito mais descritiva
def gerar_analise(nome, bio, seguidores, seguindo, public_repos, linguagens, repos_detalhes):
    linguagens_ordenadas = sorted(linguagens.items(), key=lambda x: x[1], reverse=True)
    linguagens_str = ", ".join([f"{lang} ({count} repo{'s' if count > 1 else ''})" for lang, count in linguagens_ordenadas])
    principais = [lang for lang, _ in linguagens_ordenadas[:3]]
    destaque = principais[0] if principais else "linguagens diversas"
    lista_repos = "".join([f"<li>{r}</li>" for r in repos_detalhes[:3]])

    analise_tecnica = f"""
    <p><strong>{nome}</strong> demonstra um perfil com foco em <strong>{destaque}</strong>. 
    Os projetos sugerem dedicação à criação de soluções práticas, muitas vezes voltadas à automação e desenvolvimento backend.</p>

    <p>A escolha por tecnologias como {', '.join(principais)} mostra um bom domínio técnico e uma preferência clara em relação à stack de desenvolvimento. 
    Mesmo com um número modesto de repositórios, percebe-se um cuidado com a estrutura, organização e objetivos de cada projeto.</p>

    <p>A ausência de seguidores ou estrelas não diminui a qualidade do conteúdo. Ainda assim, 
    para aumentar visibilidade e networking, é recomendável investir em compartilhamento de projetos em comunidades e redes sociais.</p>

    <p><strong>Recomendações para evolução:</strong></p>
    <ul>
        <li>Melhorar documentação e README dos repositórios com exemplos, imagens e instruções claras de uso;</li>
        <li>Incluir testes automatizados e badges (como cobertura, CI/CD, etc.);</li>
        <li>Publicar projetos em fóruns técnicos, LinkedIn e comunidades como Dev.to, Hashnode ou Twitter/X.</li>
    </ul>
    """

    html = f"""
    <p><strong>👤 Nome:</strong> {nome}</p>
    <p><strong>📄 Bio:</strong> {bio}</p>
    <p><strong>📊 Seguidores:</strong> {seguidores} | <strong>Seguindo:</strong> {seguindo}</p>
    <p><strong>📁 Repositórios públicos:</strong> {public_repos}</p>
    <p><strong>🛠️ Tecnologias utilizadas:</strong> {linguagens_str}</p>

    <p><strong>🚀 Repositórios em destaque:</strong></p>
    <ul>{lista_repos}</ul>

    <p><strong>🔍 Análise técnica detalhada:</strong></p>
    {analise_tecnica}

    <p><em>Essa análise foi gerada automaticamente com base nos dados públicos disponíveis no GitHub.</em></p>
    """
    return html

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        logging.error(f"Arquivo {index_path} não encontrado.")
        raise HTTPException(status_code=404, detail="Arquivo index.html não encontrado.")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))

@app.post("/analisar")
async def analisar(input: GithubInput):
    try:
        if "github.com" not in input.github_url:
            raise HTTPException(status_code=400, detail="URL inválida, use um link do GitHub.")

        username = input.github_url.rstrip("/").split("/")[-1]
        logging.info(f"Analisando perfil GitHub: {username}")

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
                langs = repo.get_languages()  # Lê todas as linguagens usadas no repositório
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
