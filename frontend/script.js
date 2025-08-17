document.addEventListener("DOMContentLoaded", () => {
  // =============================
  // ELEMENTOS DO DOM
  // =============================
  const formulario = document.getElementById("formulario");
  const resultadoDiv = document.getElementById("resultado");
  const githubUsernameInput = document.getElementById("githubUsername"); // <-- Alterado de githubLink para githubUsername
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;

  // =============================
  // INICIALIZAÇÃO DO TEMA
  // =============================
  body.classList.add("modo-claro");
  if (themeToggle) {
    themeToggle.textContent = "☀️"; // Define o emoji do botão de tema
  }

  // =============================
  // VALIDAÇÃO DE ELEMENTOS
  // =============================
  if (!formulario || !resultadoDiv || !githubUsernameInput) {
    console.warn("⚠️ Elementos do DOM não encontrados.");
    return;
  }

  // =============================
  // EVENTO DE SUBMISSÃO DO FORMULÁRIO
  // =============================
  formulario.addEventListener("submit", async (e) => {
    e.preventDefault();

    const botao = formulario.querySelector("button[type=submit]");
    const username = githubUsernameInput.value.trim(); // <-- Pegando o valor do nome de usuário

    // =============================
    // VALIDAÇÃO DO NOME DE USUÁRIO
    // =============================
    if (!username) {
      resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❗ Por favor, insira o nome de usuário do GitHub.</p>`;
      resultadoDiv.focus();
      return;
    }

    // Desabilita o botão para evitar múltiplos envios
    botao.disabled = true;

    // =============================
    // 🔄 ANIMAÇÃO DE LOADING
    // =============================
    resultadoDiv.innerHTML = `
      <p class="carregando" tabindex="0">
        <span class="loading-container">
          <span class="loading-text">🔍 Carregando análise</span>
          <span class="loading-dots">
            <span class="loading-dot">.</span>
            <span class="loading-dot">.</span>
            <span class="loading-dot">.</span>
          </span>
        </span>
      </p>
    `;
    resultadoDiv.focus();

    try {
      // =============================
      // ENVIO DA REQUISIÇÃO PARA O BACKEND
      // =============================
      const resposta = await fetch("/analisar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: username }), // <-- Alterado para enviar 'username'
      });

      // =============================
      // TRATAMENTO DE ERRO HTTP
      // =============================
      if (!resposta.ok) {
        const dadosErro = await resposta.json().catch(() => ({}));
        resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ${resposta.status}: ${dadosErro.erro || resposta.statusText}</p>`;
        resultadoDiv.focus();
        return;
      }

      // =============================
      // PROCESSAMENTO DA RESPOSTA
      // =============================
      const dados = await resposta.json();
      console.log("Resposta recebida:", dados);

      const conteudo = dados.analise || dados.resposta;

      if (conteudo) {
        resultadoDiv.innerHTML = conteudo;
      } else {
        resultadoDiv.innerHTML = `<p class="erro" tabindex="0">⚠️ Erro: resposta inesperada do servidor.</p>`;
      }
      resultadoDiv.focus();

    } catch (error) {
      // =============================
      // TRATAMENTO DE ERROS DE CONEXÃO
      // =============================
      console.error("Erro na requisição:", error);
      resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ao conectar: ${error.message}</p>`;
      resultadoDiv.focus();
    } finally {
      // Reabilita o botão após a requisição
      botao.disabled = false;
    }
  });

  // =============================
  // TOGGLE DE TEMA (CLARO/ESCURO)
  // =============================
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const modoClaroAtivo = body.classList.toggle("modo-claro");
      themeToggle.textContent = modoClaroAtivo ? "☀️" : "🌙";
    });
  }
});
