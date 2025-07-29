import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_analise_gpt(nome, bio, seguidores, seguindo, public_repos, linguagens, repos_detalhes):
    # Ordena linguagens por uso e seleciona as 3 principais
    principais = ", ".join(sorted(linguagens, key=linguagens.get, reverse=True)[:3])
    destacados = ", ".join(repos_detalhes[:3]) if repos_detalhes else "Nenhum repositório destacado."

    prompt = f"""
Você é um analista técnico sênior especializado em avaliação de perfis GitHub para recrutadores e avaliadores técnicos exigentes.

Com base nas informações abaixo, elabore um relatório profissional em HTML limpo (sem blocos de código), usando:
- <h2> para seções principais
- <h3> para subtítulos (quando necessário)
- <p> para parágrafos explicativos
- <ul> e <li> para listas
- <strong> para ênfases pontuais

O relatório deve ser:
- Claro, objetivo e técnico
- Avaliativo e opinativo, com fundamentação real nos dados fornecidos
- Personalizado ao perfil e aos repositórios destacados
- Evitar recomendações genéricas ou repetidas, principalmente se evidências no perfil já indicarem o contrário (ex.: não peça README se já houver documentação clara)

A estrutura do relatório deve conter:
<h2>Resumo do Perfil</h2>
<p>Resumo conciso sobre o desenvolvedor, sua bio, tecnologias e perfil geral.</p>

<h2>Análise Técnica</h2>
<p>Comentários diretos e claros sobre os repositórios destacados, focando em:</p>
<ul>
  <li>Propósito e aplicabilidade</li>
  <li>Qualidade técnica e boas práticas</li>
  <li>Diversidade e coerência tecnológica</li>
</ul>

<h2>Recomendações Profissionais</h2>
<p>Sugestões específicas e práticas para evolução técnica, visibilidade e networking, baseadas nos dados fornecidos.</p>

Dados do Perfil:
Nome: {nome}
Bio: {bio}
Seguidores: {seguidores}
Seguindo: {seguindo}
Repositórios públicos: {public_repos}
Tecnologias mais usadas: {principais}
Repositórios em destaque: {destacados}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()
