import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_analise_gpt(nome, bio, seguidores, seguindo, public_repos, linguagens, repos_detalhes, readme_text=""):
    try:
        # Garantir que linguagens seja um dict para ordenação, caso contrário usar lista simples
        if isinstance(linguagens, dict):
            principais = ", ".join(sorted(linguagens, key=linguagens.get, reverse=True)[:3])
        elif isinstance(linguagens, list):
            principais = ", ".join(linguagens[:3])
        else:
            principais = "N/A"

        destacados = ", ".join(repos_detalhes[:3]) if repos_detalhes else "Nenhum repositório destacado."

        # Limitar tamanho do README para evitar erros de tamanho de prompt
        readme_limitado = readme_text[:2000] if readme_text else ""

        prompt = f"""
Você é um analista técnico sênior especializado em avaliação detalhada de perfis GitHub para recrutadores e avaliadores técnicos exigentes.

O conteúdo do README do perfil do desenvolvedor <strong>{nome}</strong> é o seguinte:
\"\"\"
{readme_limitado}
\"\"\"

Com base nisso e nos dados do perfil, gere um relatório técnico profissional em HTML limpo, sem usar blocos de código (```), nem marcação Markdown. Use somente tags HTML como <h2>, <h3>, <p>, <ul>, <li>, <strong>, <span style="color:green;">, <span style="color:red;"> e <span style="color:blue;">.

Use:
- <h2> para seções principais
- <h3> para subtítulos quando necessário
- <p> para parágrafos explicativos
- <ul> e <li> para listas
- <strong> para destacar nomes, pontos-chave e insights importantes
- <span style="color:green;"> para destacar pontos fortes e realizações positivas
- <span style="color:red;"> para alertas, problemas ou áreas a melhorar
- <span style="color:blue;"> para sugestões específicas de melhoria, caso necessário

Regras:
- Analise minuciosamente o perfil do desenvolvedor <strong>{nome}</strong> e os repositórios destacados: {destacados}.
- Avalie o conteúdo do README do perfil e dos READMEs dos repositórios (quando fornecidos).
- Extraia e destaque quaisquer dados públicos de contato que encontrar no README do perfil ou em READMEs, como e-mail, telefone ou LinkedIn.
- Não assuma automaticamente a ausência de testes ou documentação apenas pela falta de arquivos explícitos. Considere que muitos projetos são voltados para avaliadores técnicos, que podem entender o código sem documentação extensa.
- Não inclua recomendações genéricas. Só sugira melhorias específicas e claras se identificar pontos que realmente precisam de atenção.
- Para cada repositório destacado, detalhe: objetivo, aplicabilidade, qualidade e organização do código, documentação (clareza, completude, atualizações), presença e qualidade de testes automatizados, CI/CD ou outras práticas profissionais.
- Informe a coerência do portfólio e diversidade tecnológica.
- Forneça um resumo final objetivo, destacando os pontos fortes e qualquer aspecto que mereça atenção, sem repetir recomendações vazias.

Estrutura do relatório:

<h2>Resumo do Perfil</h2>
<p>Resumo detalhado e objetivo sobre o desenvolvedor <strong>{nome}</strong>, sua bio, principais tecnologias usadas e uma visão geral do perfil.</p>

<h2>Análise Técnica dos Repositórios Destacados</h2>
<p>Para cada repositório listado, comente:</p>
<ul>
  <li>Objetivo e aplicabilidade do projeto</li>
  <li>Qualidade e organização do código</li>
  <li>Documentação: clareza, completude e atualizações</li>
  <li>Presença e qualidade de testes automatizados, CI/CD ou outras práticas profissionais</li>
</ul>

<h2>Contato e Redes</h2>
<p>Liste qualquer informação de contato pública disponível, extraída do README do perfil e dos repositórios, como e-mail, telefone ou LinkedIn.</p>

<h2>Resumo Final</h2>
<p>Breve avaliação geral com destaque para pontos fortes e possíveis áreas que merecem atenção, caso existam.</p>

Dados do Perfil:
Nome: {nome}
Bio: {bio}
Seguidores: {seguidores}
Seguindo: {seguindo}
Repositórios públicos: {public_repos}
Tecnologias principais: {principais}
Repositórios destacados: {destacados}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1400,
            temperature=0.6,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        # Log de erro pode ser adaptado conforme seu sistema de logs
        print(f"Erro ao gerar análise GPT: {e}")
        return f"<p class='erro'>Erro ao gerar análise: {e}</p>"
