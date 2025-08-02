document.addEventListener("DOMContentLoaded", () => {
  // =============================
  // ELEMENTOS DO DOM
  // =============================
  const formulario = document.getElementById("formulario");
  const resultadoDiv = document.getElementById("resultado");
  const githubLinkInput = document.getElementById("githubLink");
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;

  // =============================
  // INICIALIZAÇÃO DO TEMA
  // =============================
  // Forçar modo claro como padrão ao carregar a página
  body.classList.add("modo-claro");
  if (themeToggle) {
    themeToggle.textContent = "☀️"; // emoji do sol no botão
  }

  // =============================
  // VALIDAÇÃO DE ELEMENTOS
  // =============================
  if (!formulario || !resultadoDiv || !githubLinkInput) {
    console.warn("⚠️ Elementos do DOM não encontrados.");
    return;
  }

  // =============================
  // EVENTO DE SUBMISSÃO DO FORMULÁRIO
  // =============================
  formulario.addEventListener("submit", async (e) => {
    e.preventDefault();

    const botao = formulario.querySelector("button[type=submit]");
    const githubLink = githubLinkInput.value.trim();

    // Validação do campo de URL
    if (!githubLink) {
      resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❗ Por favor, insira uma URL do GitHub.</p>`;
      resultadoDiv.focus();
      return;
    }

    // Desabilitar botão e mostrar animação de loading
    botao.disabled = true;

    // =============================
    // 🔄 ANIMAÇÃO DE LOADING - TEXTO E PONTINHOS PULANDO INDIVIDUALMENTE
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
      // Requisição para backend
      const resposta = await fetch("/analisar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_url: githubLink }),
      });

      // Tratamento de erro HTTP
      if (!resposta.ok) {
        const dadosErro = await resposta.json().catch(() => ({}));
        resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ${resposta.status}: ${dadosErro.erro || resposta.statusText}</p>`;
        resultadoDiv.focus();
        return;
      }

      // Processar resposta JSON
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
      // Tratamento de erro de conexão
      console.error("Erro na requisição:", error);
      resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ao conectar: ${error.message}</p>`;
      resultadoDiv.focus();
    } finally {
      // Reabilitar botão após resposta ou erro
      botao.disabled = false;
    }
  });

  // =============================
  // ALTERNÂNCIA DE TEMA (CLARO/ESCURO)
  // =============================
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const modoClaroAtivo = body.classList.toggle("modo-claro");

      // Alterna o emoji 🌙 <-> ☀️ no botão
      themeToggle.textContent = modoClaroAtivo ? "☀️" : "🌙";
    });
  }
});
