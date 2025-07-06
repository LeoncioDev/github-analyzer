<<<<<<< HEAD
# GitHub Analisador – TCC 👨‍💻📊

Este projeto é parte do Trabalho de Conclusão de Curso (TCC) de Ciência da Computação, com o objetivo de auxiliar **recrutadores** e **avaliadores técnicos** a analisarem perfis públicos no GitHub de forma **automática, rápida e clara**.

Ao inserir o link de um perfil do GitHub, o sistema gera uma análise técnica com base nos dados públicos do usuário, incluindo sugestões de melhorias e um resumo em linguagem natural.
=======
# 🔍 GitHub Analisador com IA – Projeto de TCC

Este projeto é parte do Trabalho de Conclusão de Curso (TCC) em Ciência da Computação e tem como objetivo auxiliar **recrutadores**, **avaliadores técnicos** e interessados em obter uma visão automatizada de perfis públicos no GitHub.

A aplicação analisa informações públicas do perfil e gera uma **análise técnica em linguagem natural**, apontando linguagens predominantes, destaque de repositórios e sugestões personalizadas de melhoria.
>>>>>>> 8e132b6baeeb3c8569c0dabecf3253db05f33d2b

---

## ✅ Funcionalidades

<<<<<<< HEAD
- 📌 Análise de perfis públicos do GitHub com base em:
  - Linguagens mais utilizadas
  - Repositórios públicos
  - Quantidade de seguidores / seguindo
  - Descrição dos repositórios
- 🧠 Geração de análise textual automatizada
- 🛠️ Sugestões personalizadas de melhoria
- 💡 Interface web simples e acessível
=======
- 📊 Análise automatizada de perfis do GitHub
- 🔍 Extração de dados públicos: bio, seguidores, linguagens, repositórios
- 💬 Geração de relatório em HTML com insights técnicos
- 💡 Sugestões de evolução para o perfil GitHub
- 🧠 Uso de IA (Sentence Transformers) para expandir possibilidades
- 🌐 Interface web simples, responsiva e acessível
>>>>>>> 8e132b6baeeb3c8569c0dabecf3253db05f33d2b

---

## 🧱 Arquitetura do Projeto

<<<<<<< HEAD
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
=======
| Camada     | Tecnologia                   |
|------------|------------------------------|
| Backend    | Python + FastAPI             |
| Frontend   | HTML + CSS + JavaScript      |
| API externa| GitHub API                   |
| IA opcional| Sentence Transformers (NLU)  |
| Middleware | CORS, dotenv (variáveis)     |

---

## 🌐 Como Funciona

1. O usuário acessa o site e insere o link de um perfil GitHub.
2. O frontend envia a URL via `fetch` para a rota `/analisar`.
3. O backend consulta a GitHub API e extrai:
   - Repositórios públicos
   - Linguagens utilizadas
   - Bio, seguidores, estrelas e mais
4. O sistema gera uma análise em linguagem natural estruturada em HTML.
5. A resposta é exibida diretamente na página.
>>>>>>> 8e132b6baeeb3c8569c0dabecf3253db05f33d2b

---

## 🧪 Tecnologias Utilizadas

<<<<<<< HEAD
- **FastAPI** – API em Python rápida e moderna
- **PyGithub** – Cliente GitHub para Python
- **Sentence Transformers** – Análise semântica (opcional/expansível)
- **dotenv** – Gerenciamento de variáveis sensíveis
- **HTML/CSS/JS** – Interface direta, sem frameworks
- **CORS Middleware** – Comunicação frontend-backend
- **GitHub API** – Coleta de dados públicos
=======
- **FastAPI** – Framework web moderno para APIs Python
- **PyGithub** – Cliente GitHub para Python
- **Sentence Transformers** – Análise semântica de texto (expansível)
- **python-dotenv** – Variáveis de ambiente seguras
- **HTML, CSS, JS** – Frontend leve e acessível
- **GitHub API** – Consulta de dados públicos
- **CORS Middleware** – Integração segura entre backend e frontend
>>>>>>> 8e132b6baeeb3c8569c0dabecf3253db05f33d2b

---

## 📁 Estrutura do Projeto

<<<<<<< HEAD
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

=======
github-analisador/
├── backend/
│ ├── main.py # Lógica da API FastAPI
│ ├── .env # Token GitHub (não enviado ao GitHub)
│ └── requirements.txt # Dependências do backend
│
├── frontend/
│ ├── index.html # Interface principal
│ ├── style.css # Estilos da página
│ └── script.js # Lógica para envio e exibição
│
├── .gitignore # Arquivos ignorados (ex: .env, pycache)
└── README.md # Este arquivo


---

## 🔐 Segurança

- O token da GitHub API é opcional e configurado via `.env` (não incluído no repositório).
- O projeto usa `CORS` para controle de acesso entre frontend e backend.
- Pastas como `__pycache__` e arquivos sensíveis estão ignorados via `.gitignore`.

---

## 📌 Observações

- O projeto roda localmente, sem necessidade de deploy externo.
- Ideal para demonstração acadêmica, simulações de entrevistas ou uso pessoal por desenvolvedores.
- IA está pronta para expansão futura com modelos mais avançados ou integração com bancos vetoriais.

---

## 👨‍💻 Autor

Desenvolvido por **[João Paulo Leôncio]** como parte do TCC de Ciência da Computação.

>>>>>>> 8e132b6baeeb3c8569c0dabecf3253db05f33d2b
