# GitHub Analisador – TCC 👨‍💻📊

Este projeto é parte do Trabalho de Conclusão de Curso (TCC) de Ciência da Computação, com o objetivo de auxiliar **recrutadores** e **avaliadores técnicos** a analisarem perfis públicos no GitHub de forma **automática, rápida e clara**.

Ao inserir o link de um perfil do GitHub, o sistema gera uma análise técnica com base nos dados públicos do usuário, incluindo sugestões de melhorias e um resumo em linguagem natural.

---

## ✅ Funcionalidades

- 📌 Análise de perfis públicos do GitHub com base em:
  - Linguagens mais utilizadas
  - Repositórios públicos
  - Quantidade de seguidores / seguindo
  - Descrição dos repositórios
- 🧠 Geração de análise textual automatizada
- 🛠️ Sugestões personalizadas de melhoria
- 💡 Interface web simples e acessível

---

## 🧱 Arquitetura do Projeto

| Camada     | Tecnologia        |
|------------|-------------------|
| Backend    | Python + FastAPI  |
| Frontend   | HTML, CSS, JS     |
| API externa| GitHub API        |
| IA Embedding| Sentence Transformers |
| Hospedagem | Executável local ou container |

---

## 🌐 Como funciona

1. O usuário acessa o site e insere o link de um perfil GitHub.
2. O frontend envia esse link via `fetch` para o endpoint `/analisar`.
3. O backend consome a GitHub API, coleta dados do perfil e repositórios.
4. A análise é montada em HTML, com:
   - Linguagens principais
   - Repositórios em destaque
   - Bio, seguidores, etc.
   - Sugestões de melhoria
5. O resultado é exibido na página de forma clara e organizada.

---

## 🧪 Tecnologias Utilizadas

- **FastAPI** – API em Python rápida e moderna
- **PyGithub** – Cliente GitHub para Python
- **Sentence Transformers** – Análise semântica (opcional/expansível)
- **dotenv** – Gerenciamento de variáveis sensíveis
- **HTML/CSS/JS** – Interface direta, sem frameworks
- **CORS Middleware** – Comunicação frontend-backend
- **GitHub API** – Coleta de dados públicos

---

## 📁 Estrutura do Projeto

GITHUB-ANALISADOR/
│
├── backend/
│ ├── main.py # API FastAPI com /analisar
│ ├── .env # Token do GitHub (opcional)
│ ├── requirements.txt # Dependências Python
│
├── frontend/
│ ├── index.html # Formulário de entrada
│ ├── style.css # Estilização visual
│ └── script.js # Envia dados e exibe resultados
│
└── README.md # Este arquivo

