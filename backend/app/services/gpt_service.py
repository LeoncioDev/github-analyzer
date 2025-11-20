import os
import json
from openai import OpenAI
from typing import List
from app.models.schemas import CandidateDataForRanking

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- FUNÇÃO "LIMPADORA" ---
def clean_ai_response(raw_html: str) -> str:
    """
    Limpa a resposta da IA, removendo cercas de markdown (```html e ```)
    que ela possa adicionar por engano.
    """
    raw_html = raw_html.strip()
    
    # Remove a tag inicial (pode ser ```html ou ```)
    if raw_html.startswith("```html"):
        raw_html = raw_html[7:]
    elif raw_html.startswith("```"):
        raw_html = raw_html[3:]
        
    # Remove a tag final
    if raw_html.endswith("```"):
        raw_html = raw_html[:-3]
        
    return raw_html.strip()
# --- FIM ---


def selecionar_repositorios_com_ia(repos_lista: list) -> list:
    """
    Usa a IA para selecionar os 5 repositórios mais complexos e relevantes de uma lista.
    """
    if not repos_lista:
        return []

    repos_str = "\n".join(repos_lista)

    prompt = f"""
Você é um Arquiteto de Software Sênior e sua tarefa é identificar os projetos mais relevantes em um portfólio.
Abaixo está uma lista de repositórios de um usuário:
---
{repos_str}
---
Analise a lista e selecione os 5 (cinco) repositórios que parecem ser os mais complexos, completos e profissionalmente relevantes.
Ignore projetos simples, forks, ou "hello-world".

Responda APENAS com uma lista JSON contendo os nomes exatos dos repositórios que você selecionou.
Exemplo de resposta:
["nome-do-repo-1", "nome-do-repo-5", "nome-do-repo-10", "nome-do-repo-12", "nome-do-repo-15"]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2,
        )
        
        content = response.choices[0].message.content.strip()
        
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = content[json_start:json_end]
            nomes_selecionados = json.loads(json_str)
            return nomes_selecionados
        else:
            return [repo.split(' ')[0] for repo in repos_lista[:5]]

    except Exception as e:
        print(f"Erro ao selecionar repositórios com IA: {e}")
        return [repo.split(' ')[0] for repo in repos_lista[:5]]


def gerar_analise_gpt(nome, bio, seguidores, seguindo, public_repos, linguagens, repos_detalhes, readme_text="", contexto: str = "recrutamento", login: str = "", html_url: str = ""):
    try:
        if isinstance(linguagens, dict):
            principais_lista = sorted(linguagens, key=linguagens.get, reverse=True)[:3]
            principais = ", ".join(principais_lista) if principais_lista else "N/A"
        elif isinstance(linguagens, list):
            principais = ", ".join(linguagens[:3]) if linguagens else "N/A"
        else:
            principais = "N/A"

        destacados_lista = repos_detalhes 
        destacados_str = "\n".join([f"<li>{repo}</li>" for repo in destacados_lista])
        if not destacados_str:
            destacados_str = "<li>Nenhum repositório de projeto encontrado.</li>"

        readme_limitado = readme_text[:2000] if readme_text else "Nenhum README de perfil fornecido."

        prompt = ""
        
        card_style = "border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px;"
        repo_card_style = "border-top: 1px solid #30363d; padding-top: 12px; margin-top: 12px;"

        regras_html = f"""
REGRAS DE GERAÇÃO:
1.  **Gere APENAS HTML.** Nenhum Markdown (como `###` ou `**...**`) deve ser usado.
2.  **NÃO** inclua `<html>`, `<body>`, `<head>`, `<style>` ou `<script>`. Gere apenas as tags de conteúdo.
3.  Use `<h2>` para títulos de seção, `<h3>` para nomes de repositórios.
4.  Use `<strong>` para ênfase, `<p>` para parágrafos, `<ul>` e `<li>` para listas.
5.  **ESTRUTURA VISUAL:** Envolva CADA seção principal em um `<div>` com este estilo inline exato:
    `<div style="{card_style}">...</div>`
6.  Coloque o título da seção (ex: `<h2>...</h2>`) DENTRO de cada `<div>`.
7.  **IDENTIFICAÇÃO:** Refira-se ao candidato APENAS pelo Nome e (@username). NUNCA use o nome de um repositório como se fosse o apelido ou "conhecido como" do candidato. Repositórios são projetos.
"""

        if contexto == "autoanalise":
            prompt = f"""
{regras_html}
PERSONA: Você é um Mentor de Carreira e Desenvolvedor Sênior (Tech Lead).
OBJETIVO: Analisar o perfil de {nome} e fornecer um plano de ação detalhado para melhoria, focando nos projetos.
DADOS DO PERFIL:
- Nome: {nome} (@{login})
- Bio: {bio}
- README do Perfil: "{readme_limitado}"
- Principais Tecnologias: {principais}
- Repositórios Selecionados pela IA (os mais complexos):
<ul>
{destacados_str}
</ul>

TAREFA: Gere o relatório HTML.
1.  Crie o card de "Seus Pontos Fortes Atuais".
2.  Crie o card de "Análise Detalhada dos Seus Projetos".
3.  **Dentro desse segundo card:** Para CADA repositório da lista, você DEVE envolvê-lo em um `<div>` com o estilo: `<div style="{repo_card_style}">` (comece o primeiro *sem* esse div).
4.  **Dentro de cada `div` de projeto:** Gere um `<h3>` com o nome do projeto.
5.  **Abaixo de cada `<h3>`:** Gere uma `<ul>` com 3 `<li>`s:
    - `<li><strong>O que foi bem feito:</strong> ... (sua análise)</li>`
    - `<li><strong>Ponto de Melhoria (Ação):</strong> ... (sua análise, usando ✅/❌)</li>`
    - `<li><strong>Próximo Nível (Sugestão):</strong> ... (sua análise)</li>`
6.  Crie o card final de "Plano de Ação (Resumo)".

ESTRUTURA HTML DE SAÍDA (use-a como guia):
<div style="{card_style}">
    <h2>🚀 Seus Pontos Fortes Atuais</h2>
    <p>...</p>
</div>
<div style="{card_style}">
    <h2>💡 Análise Detalhada dos Seus Projetos (Selecionados por IA)</h2>
    <div>
        <h3>Nome-do-Projeto-1</h3>
        <ul>...</ul>
    </div>
    <div style="{repo_card_style}">
        <h3>Nome-do-Projeto-2</h3>
        <ul>...</ul>
    </div>
</div>
<div style="{card_style}">
    <h2>🎯 Plano de Ação (Resumo)</h2>
    <p>...</p>
</div>
"""
        else:
            prompt = f"""
{regras_html}
PERSONA: Você é um Analista Técnico Sênior (Tech Recruiter).
OBJETIVO: Avaliar o perfil de {nome} para uma vaga de desenvolvedor, focando na análise técnica de seus repositórios.
DADOS DO PERFIL:
- Nome: {nome} (@{login})
- Bio: {bio}
- README do Perfil: "{readme_limitado}"
- Principais Tecnologias: {principais}
- Repositórios Selecionados pela IA (os mais complexos):
<ul>
{destacados_str}
</ul>

TAREFA: Gere o relatório HTML.
1.  Primeiro, crie um card de "Resumo do Perfil e Veredito".
    - Comece com um parágrafo resumindo o perfil: "João Paulo (@leonciodev) é um desenvolvedor com foco em...".
    - JAMAIS confunda o nome de um repositório com o nome do candidato.
2.  Segundo, crie um card de "Análise Técnica Detalhada".
3.  **Dentro desse segundo card:** Para CADA repositório da lista, você DEVE envolvê-lo em um `<div>` com o estilo: `<div style="{repo_card_style}">` (comece o primeiro *sem* esse div).
4.  **Dentro de cada `div` de projeto:** Gere um `<h3>` com o nome do projeto.
5.  **Abaixo de cada `<h3>`:** Gere uma `<ul>` com 4 `<li>`s:
    - `<li><strong>Objetivo Inferido:</strong> ... (sua análise)</li>`
    - `<li><strong>Análise Técnica:</strong> ... (sua análise)</li>`
    - `<li><strong>Qualidade e Documentação:</strong> ... (sua análise, usando ✅/❌)</li>`
    - `<li><strong>Sinal de Senioridade:</strong> ... (sua análise)</li>`

ESTRUTURA HTML DE SAÍDA (use-a como guia):
<div style="{card_style}">
    <h2>📊 Resumo do Perfil e Veredito</h2>
    <p>...</p>
    <ul>
        <li><span style="color:green;">Veredito: ...</span></li>
    </ul>
</div>
<div style="{card_style}">
    <h2>🔍 Análise Técnica Detalhada dos Repositórios (Selecionados por IA)</h2>
    <div>
        <h3>Nome-do-Projeto-1</h3>
        <ul>...</ul>
    </div>
    <div style="{repo_card_style}">
        <h3>Nome-do-Projeto-2</h3>
        <ul>...</ul>
    </div>
</div>
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000, 
            temperature=0.4,
        )
        
        raw_html = response.choices[0].message.content
        return clean_ai_response(raw_html)

    except Exception as e:
        print(f"Erro ao gerar análise GPT: {e}")
        card_style_erro = "border: 1px solid #ff6b6b; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #ff6b6b20;"
        return f'<div style="{card_style_erro}"><h2>❌ Erro ao Gerar Análise</h2><p class="erro">Detalhe: {e}</p></div>'

# --- FUNÇÃO DE RANKING ---
def gerar_ranking_completo(job_description: str, candidatos_analisados: List[CandidateDataForRanking]) -> str:
    """
    Usa a IA para comparar e ranquear múltiplos candidatos com base em uma descrição de vaga.
    """
    if not candidatos_analisados:
        return "<h3>Nenhum candidato analisado para ranking.</h3>"

    analises_formatadas = []
    for i, cand in enumerate(candidatos_analisados):
        analises_formatadas.append(f"""
--- CANDIDATO {i+1}: {cand.nome} (@{cand.username}) ---
Link do Perfil: {cand.html_url}
<Detalhes da Análise Gerada Pela IA>
{cand.analise_html}
</Detalhes da Análise Gerada Pela IA>
""")

    analises_concatenadas = "\n".join(analises_formatadas)

    card_style = "border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px;"

    prompt = f"""
Você é um Recrutador Técnico Sênior com vasta experiência em análise de perfis GitHub e descrição de vagas.
Sua tarefa é ranquear candidatos para uma vaga específica e fornecer um relatório claro e objetivo.

REGRAS DE GERAÇÃO:
1.  **Gere APENAS HTML.** Nenhum Markdown (como `###` ou `**...**`) deve ser usado.
2.  **NÃO** inclua `<html>`, `<body>`, `<head>`, `<style>` ou `<script>`. Gere apenas as tags de conteúdo.
3.  Use `<h2>` para títulos de seção, `<h3>` para nomes de candidatos, `<h4>` para subtítulos de análise.
4.  Use `<strong>` para ênfase, `<p>` para parágrafos, `<ul>` e `<li>` para listas.
5.  **ESTRUTURA VISUAL:** Envolva CADA seção principal em um `<div>` com este estilo inline exato:
    `<div style="{card_style}">...</div>`
6.  Coloque o título da seção (ex: `<h2>...</h2>`) DENTRO de cada `<div>`.
7.  Use divs para separar a análise de cada candidato dentro da seção.
8. Seja objetivo e direto em suas análises e justificativas.
9. Considere a descrição da vaga cuidadosamente ao ranquear os candidatos.
10. Comece mencionando o nome completo do desenvolvedor, seguido pelo seu username entre parênteses (ex: João (@joao)).
11. **IMPORTANTE:** NUNCA use o nome de um repositório como se fosse o apelido do desenvolvedor (ex: não diga "conhecido como ProjectX").

DESCRIÇÃO DA VAGA:
---
{job_description}
---

ANÁLISES DETALHADAS DOS CANDIDATOS:
(Cada candidato teve seu perfil e projetos mais complexos analisados individualmente pela IA. Use estas análises como base para seu ranking.)
{analises_concatenadas}

TAREFA:
Gere um relatório HTML com as seguintes seções:

1.  **"📊 Ranking de Candidatos para a Vaga"**:
    * Um `<h3>` para cada candidato, com seu nome e @username (ex: "1º - João Silva (@joaosilva)").
    * Abaixo de cada `<h3>`, uma lista `<ul>` com 2 `<li>`s:
        * `<li><strong>Pontos Fortes para a Vaga:</strong> Descreva 2-3 pontos fortes diretamente relacionados à JD.</li>`
        * `<li><strong>Pontos a Observar:</strong> Descreva 1-2 pontos que podem ser desenvolvidos ou que não se alinham perfeitamente à JD.</li>`

2.  **"⭐ Justificativa Final do Ranking"**:
    * Um parágrafo (`<p>`) explicando a lógica geral por trás do ranking (por que o 1º é o 1º, etc.).
    * Um `<ul>` com 3 `<li>`s para as principais recomendações/próximos passos (ex: "Recomendar entrevista técnica para X", "Solicitar portfólio de Y").

ESTRUTURA HTML DE SAÍDA (use-a como guia):

<div style="{card_style}">
    <h2>📋 Descrição da Vaga</h2>
    <p>{job_description}</p>
</div>

<div style="{card_style}">
    <h2>📊 Ranking de Candidatos para a Vaga</h2>
    <div>
        <h3>1º - Nome do Candidato 1 (@username1)</h3>
        <ul>
            <li><strong>Pontos Fortes para a Vaga:</strong> ...</li>
            <li><strong>Pontos a Observar:</strong> ...</li>
        </ul>
    </div>
    <div style="border-top: 1px solid #30363d; padding-top: 12px; margin-top: 12px;">
        <h3>2º - Nome do Candidato 2 (@username2)</h3>
        <ul>
            <li>...</li>
        </ul>
    </div>
    
</div>

<div style="{card_style}">
    <h2>⭐ Justificativa Final do Ranking</h2>
    <p>Com base na análise...</p>
    <ul>
        <li><strong>Próximo Passo 1:</strong> ...</li>
        <li><strong>Próximo Passo 2:</strong> ...</li>
    </ul>
</div>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0.7,
        )
        
        raw_html = response.choices[0].message.content
        return clean_ai_response(raw_html)
        
    except Exception as e:
        print(f"Erro ao gerar ranking final: {e}")
        card_style_erro = "border: 1px solid #ff6b6b; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #ff6b6b20;"
        return f'<div style="{card_style_erro}"><h2>❌ Erro ao Gerar Ranking</h2><p class="erro">Detalhe: {e}</p></div>'
