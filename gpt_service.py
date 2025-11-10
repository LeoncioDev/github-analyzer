import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_analise_gpt(nome, bio, seguidores, seguindo, public_repos, linguagens, repos_detalhes, readme_text="", contexto: str = "recrutamento", login: str="", html_url: str=""):
    try:
        if isinstance(linguagens, dict):
            principais_lista = sorted(linguagens, key=linguagens.get, reverse=True)[:3]
            principais = ", ".join(principais_lista) if principais_lista else "N/A"
        elif isinstance(linguagens, list):
            principais = ", ".join(linguagens[:3]) if linguagens else "N/A"
        else:
            principais = "N/A"

        # Pegar os 5 repositórios mais relevantes para a IA analisar
        destacados_lista = repos_detalhes[:5]
        destacados_str = "\n".join([f"<li>{repo}</li>" for repo in destacados_lista])
        if not destacados_str:
            destacados_str = "<li>Nenhum repositório de projeto encontrado.</li>"

        readme_limitado = readme_text[:2000] if readme_text else "Nenhum README de perfil fornecido."

        prompt = ""
        
        # --- ESTILIZAÇÃO CSS INLINE PARA OS CARDS ---
        card_style = "border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px;"

        # --- REGRAS GERAIS DE HTML (PARA AMBOS OS PROMPTS) ---
        regras_html = f"""
REGRAS DE GERAÇÃO:
1.  **Gere APENAS HTML.** Nenhum Markdown (como `###` ou `**...**`) deve ser usado.
2.  **NÃO** inclua `<html>`, `<body>`, `<head>`, `<style>` ou `<script>`. Gere apenas as tags de conteúdo.
3.  Use `<h2>` para títulos de seção, `<h3>` para nomes de repositórios.
4.  Use `<strong>` para ênfase, `<p>` para parágrafos, `<ul>` e `<li>` para listas.
5.  **ESTRUTURA VISUAL:** Envolva CADA seção principal em um `<div>` com este estilo inline exato:
    `<div style="{card_style}">...</div>`
6.  Coloque o título da seção (ex: `<h2>...</h2>`) DENTRO de cada `<div>`.
"""

        # --- LÓGICA DE CONTEXTO ---
        if contexto == "autoanalise":
            # PROMPT 1: MENTOR
            prompt = f"""
{regras_html}

PERSONA: Você é um Mentor de Carreira e Desenvolvedor Sênior (Tech Lead). Seu tom é construtivo, encorajador e prático.

OBJETIVO: Analisar o perfil de {nome} e fornecer um plano de ação detalhado para melhoria, focando nos projetos.

DADOS DO PERFIL:
- Nome: {nome} (@{login})
- Bio: {bio}
- README do Perfil: "{readme_limitado}"
- Principais Tecnologias: {principais}
- Repositórios para análise:
<ul>
{destacados_str}
</ul>

TAREFA: Gere o relatório HTML.
1.  Crie o card de "Seus Pontos Fortes Atuais".
2.  Crie o card de "Análise Detalhada dos Seus Projetos".
3.  **Dentro desse segundo card:** Para CADA repositório da lista, você DEVE gerar um `<h3>` com o nome do projeto.
4.  **Abaixo de cada `<h3>`:** Você DEVE gerar uma `<ul>` com 3 `<li>`s:
    - `<li><strong>O que foi bem feito:</strong> ... (sua análise)</li>`
    - `<li><strong>Ponto de Melhoria (Ação):</strong> ... (sua análise, usando ✅/❌)</li>`
    - `<li><strong>Próximo Nível (Sugestão):</strong> ... (sua análise)</li>`
5.  Crie o card final de "Plano de Ação (Resumo)".

ESTRUTURA HTML DE SAÍDA (use-a como guia):

<div style="{card_style}">
    <h2>🚀 Seus Pontos Fortes Atuais</h2>
    <p>Seja encorajador. Destaque os pontos positivos que {nome} já possui (baseado na bio, no README do perfil e nas tecnologias).</p>
</div>

<div style="{card_style}">
    <h2>💡 Análise Detalhada dos Seus Projetos</h2>
    
    </div>

<div style="{card_style}">
    <h2>🎯 Plano de Ação (Resumo)</h2>
    <p>Com base na análise dos projetos, resuma as 3 principais ações que {nome} deve tomar para elevar o nível do seu portfólio.</p>
</div>
"""
        else:
            # PROMPT 2: ANALISTA TÉCNICO
            prompt = f"""
{regras_html}

PERSONA: Você é um Analista Técnico Sênior (Tech Recruiter). Seu tom é profissional, objetivo e analítico.

OBJETIVO: Avaliar o perfil de {nome} para uma vaga de desenvolvedor, focando na análise técnica de seus repositórios.

DADOS DO PERFIL:
- Nome: {nome} (@{login})
- Bio: {bio}
- README do Perfil: "{readme_limitado}"
- Principais Tecnologias: {principais}
- Repositórios para análise:
<ul>
{destacados_str}
</ul>

TAREFA: Gere o relatório HTML.
1.  Primeiro, crie um card de "Resumo do Perfil e Veredito".
2.  Segundo, crie um card de "Análise Técnica Detalhada".
3.  **Dentro desse segundo card:** Para CADA repositório da lista, você DEVE gerar um `<h3>` com o nome do projeto.
4.  **Abaixo de cada `<h3>`:** Você DEVE gerar uma `<ul>` com 4 `<li>`s:
    - `<li><strong>Objetivo Inferido:</strong> ... (sua análise)</li>`
    - `<li><strong>Análise Técnica:</strong> ... (sua análise)</li>`
    - `<li><strong>Qualidade e Documentação:</strong> ... (sua análise, usando ✅/❌)</li>`
    - `<li><strong>Sinal de Senioridade:</strong> ... (sua análise)</li>`

ESTRUTURA HTML DE SAÍDA (use-a como guia):

<div style="{card_style}">
    <h2>📊 Resumo do Perfil e Veredito</h2>
    <p>Resumo objetivo sobre {nome} (bio, tecnologias principais). Avalie a coerência do perfil.</p>
    <p>Finalize com um veredito curto. Use spans coloridos para o status:</p>
    <ul>
        <li><span style="color:green;">Veredito: Candidato promissor.</span></li>
    </ul>
</div>

<div style="{card_style}">
    <h2>🔍 Análise Técnica Detalhada dos Repositórios</h2>

    </div>
"""
        # --- FIM DA LÓGICA DE CONTEXTO ---
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000, 
            temperature=0.4,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Erro ao gerar análise GPT: {e}")
        # Retornar o erro em um 'card' de erro
        card_style_erro = "border: 1px solid #ff6b6b; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #ff6b6b20;"
        return f'<div style="{card_style_erro}"><h2>❌ Erro ao Gerar Análise</h2><p class="erro">Detalhe: {e}</p></div>'