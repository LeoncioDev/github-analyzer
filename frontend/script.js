document.addEventListener("DOMContentLoaded", () => {
  // =============================
  // ELEMENTOS DO DOM
  // =============================
  const formulario = document.getElementById("formulario");
  const resultadoDiv = document.getElementById("resultado");
  const githubUsernameInput = document.getElementById("githubUsername");
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;

  // =============================
  // INICIALIZAÇÃO DO TEMA (CLARO POR PADRÃO)
  // =============================
  body.classList.add("modo-claro");
  if (themeToggle) {
    themeToggle.textContent = "☀️"; // Emoji para tema claro
  }

  // =============================
  // VALIDAÇÃO DE ELEMENTOS ESSENCIAIS
  // =============================
  if (!formulario || !resultadoDiv || !githubUsernameInput) {
    console.warn("⚠️ Elementos essenciais do DOM não encontrados.");
    return;
  }

  // =============================
  // ENVIO FORMULÁRIO BUSCA POR USERNAME
  // =============================
  formulario.addEventListener("submit", async (e) => {
    e.preventDefault();

    const botao = formulario.querySelector("button[type=submit]");
    const username = githubUsernameInput.value.trim();

    if (!username) {
      resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❗ Por favor, insira o nome de usuário do GitHub.</p>`;
      resultadoDiv.focus();
      return;
    }

    botao.disabled = true;

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
      const resposta = await fetch("/analisar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });

      if (!resposta.ok) {
        const dadosErro = await resposta.json().catch(() => ({}));
        resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ${resposta.status}: ${dadosErro.erro || resposta.statusText}</p>`;
        resultadoDiv.focus();
        return;
      }

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
      console.error("Erro na requisição:", error);
      resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ao conectar: ${error.message}</p>`;
      resultadoDiv.focus();
    } finally {
      botao.disabled = false;
    }
  });

  // =============================
  // TOGGLE DOS FILTROS AVANÇADOS
  // =============================
  const toggleFiltersBtn = document.getElementById("toggleFilters");
  const filtrosSection = document.getElementById("filtrosAvancados");

  if (toggleFiltersBtn && filtrosSection) {
    toggleFiltersBtn.addEventListener("click", () => {
      const estaVisivel = filtrosSection.style.display === "block";
      filtrosSection.style.display = estaVisivel ? "none" : "block";
      toggleFiltersBtn.textContent = estaVisivel ? "Filtros Avançados 🔍" : "Esconder Filtros ❌";
    });
  }

  // =============================
  // ENVIO FORMULÁRIO FILTROS AVANÇADOS
  // =============================
  const formFiltros = document.getElementById("formFiltros");
  if (formFiltros) {
    formFiltros.addEventListener("submit", async (e) => {
      e.preventDefault();

      const botaoFiltros = formFiltros.querySelector("button[type=submit]");
      botaoFiltros.disabled = true;

      // Função para coletar valores de checkboxes pelo nome
      function coletarCheckboxes(nome) {
        const selecionados = formFiltros.querySelectorAll(`input[name='${nome}']:checked`);
        return Array.from(selecionados).map(cb => cb.value);
      }

      // Captura as seleções de cada grupo
      const linguagensSelecionadas = coletarCheckboxes("linguagens");
      const habilidadesSelecionadas = coletarCheckboxes("habilidades");
      const competenciasSelecionadas = coletarCheckboxes("competencias");
      const metodologiasSelecionadas = coletarCheckboxes("metodologias");

      // Validação: ao menos um checkbox selecionado em qualquer grupo
      const temSelecao = linguagensSelecionadas.length > 0 ||
                         habilidadesSelecionadas.length > 0 ||
                         competenciasSelecionadas.length > 0 ||
                         metodologiasSelecionadas.length > 0;

      if (!temSelecao) {
        resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❗ Por favor, selecione ao menos uma opção em algum dos filtros avançados.</p>`;
        resultadoDiv.focus();
        botaoFiltros.disabled = false;
        return;
      }

      resultadoDiv.innerHTML = `
        <p class="carregando" tabindex="0">
          <span class="loading-container">
            <span class="loading-text">🔍 Buscando com filtros...</span>
            <span class="loading-dots">
              <span class="loading-dot">.</span>
              <span class="loading-dot">.</span>
              <span class="loading-dot">.</span>
            </span>
          </span>
        </p>
      `;
      resultadoDiv.focus();

      const dadosFiltros = {
        linguagens: linguagensSelecionadas,
        habilidades: habilidadesSelecionadas,
        competencias: competenciasSelecionadas,
        metodologias: metodologiasSelecionadas,
      };

      try {
        const resposta = await fetch("/analisar-com-filtros", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dadosFiltros),
        });

        if (!resposta.ok) {
          const dadosErro = await resposta.json().catch(() => ({}));
          resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ${resposta.status}: ${dadosErro.erro || resposta.statusText}</p>`;
          resultadoDiv.focus();
          return;
        }

        const dados = await resposta.json();
        const conteudo = dados.analise || dados.resposta;

        if (conteudo) {
          resultadoDiv.innerHTML = conteudo;
        } else {
          resultadoDiv.innerHTML = `<p class="erro" tabindex="0">⚠️ Erro: resposta inesperada do servidor.</p>`;
        }
        resultadoDiv.focus();

      } catch (error) {
        console.error("Erro na requisição:", error);
        resultadoDiv.innerHTML = `<p class="erro" tabindex="0">❌ Erro ao conectar: ${error.message}</p>`;
        resultadoDiv.focus();
      } finally {
        botaoFiltros.disabled = false;
      }
    });
  }

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
