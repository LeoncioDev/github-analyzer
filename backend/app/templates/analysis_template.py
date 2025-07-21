# app/templates/analysis_template.py

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
