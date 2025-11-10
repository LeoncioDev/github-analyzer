document.addEventListener("DOMContentLoaded", () => {
  // ===============================
  // ELEMENTOS OPCIONAIS
  // ===============================
  const formulario = document.getElementById("formulario");
  const resultadoDiv = document.getElementById("resultado");
  const githubUsernameInput = document.getElementById("githubUsername");
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;
  const loaderContainer = document.getElementById("loader");

  // ===============================
  // TEMA PERSISTENTE
  // ===============================
  const temaSalvo = localStorage.getItem("tema");
  if (temaSalvo === "claro") {
    body.classList.add("modo-claro");
    if (themeToggle) themeToggle.textContent = "☀️";
  } else {
    body.classList.remove("modo-claro");
    if (themeToggle) themeToggle.textContent = "🌙";
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const modoClaroAtivo = body.classList.toggle("modo-claro");
      themeToggle.textContent = modoClaroAtivo ? "☀️" : "🌙";
      localStorage.setItem("tema", modoClaroAtivo ? "claro" : "escuro");
    });
  }

  // ===============================
  // FUNÇÕES DE LOADER
  // ===============================
  function mostrarLoader() {
    if (loaderContainer) loaderContainer.style.display = "flex";
  }

  function esconderLoader() {
    if (loaderContainer) loaderContainer.style.display = "none";
  }

  // ===============================
  // FUNÇÕES DE FEEDBACK NO RESULTADO
  // ===============================
  let dotsInterval;

  function startDotsAnimation() {
    let dots = 0;
    if (!resultadoDiv) return;
    dotsInterval = setInterval(() => {
      const dotsSpan = resultadoDiv.querySelector(".dots");
      if (dotsSpan) {
        dotsSpan.textContent = ".".repeat(dots + 1);
        dots = (dots + 1) % 3;
      }
    }, 500);
  }

  function stopDotsAnimation() {
    clearInterval(dotsInterval);
  }

  function mostrarErro(mensagem) {
    stopDotsAnimation();
    if (resultadoDiv) {
      resultadoDiv.innerHTML = `<p class="erro" tabindex="0">${mensagem}</p>`;
      resultadoDiv.focus();
    }
    esconderLoader();
  }

  function mostrarLoading(mensagem) {
    if (resultadoDiv) {
      resultadoDiv.innerHTML = `<p class="carregando" tabindex="0">${mensagem} <span class="dots">.</span></p>`;
      resultadoDiv.focus();
      startDotsAnimation();
      mostrarLoader();
    }
  }

  function mostrarAnalise(conteudo) {
    stopDotsAnimation();
    if (resultadoDiv) {
      resultadoDiv.innerHTML = conteudo;
      resultadoDiv.focus();
    }
    esconderLoader();
  }

  // ===============================
  // FORMULÁRIO DE ANÁLISE (opcional)
  // ===============================
  if (formulario && resultadoDiv && githubUsernameInput) {
    const botao = formulario.querySelector('button[type=submit]');

    formulario.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = githubUsernameInput.value.trim();

      // Pegar o contexto
      const contextoSelecionado = document.querySelector('Input[name="contexto"]:checked');
      const contexto = contextoSelecionado ? contextoSelecionado.value : "recrutamento";
      //--------------------------

      if (!username) {
        githubUsernameInput.classList.add("input-erro");
        mostrarErro("❗ Por favor, insira o nome de usuário ou URL do GitHub.");
        return;
      } else {
        githubUsernameInput.classList.remove("input-erro");
      }

      if (botao) botao.disabled = true;
      mostrarLoading("🔍 Carregando análise");

      try {
        const resposta = await fetch("/analisar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, contexto }),
        });

        if (!resposta.ok) {
          const dadosErro = await resposta.json().catch(() => ({}));
          const detalheErro = dadosErro.detail || dadosErro.erro || resposta.statusText;
          mostrarErro(`❌ Erro ${resposta.status}: ${detalheErro}`);
          return;
        }

        const dados = await resposta.json();
        const conteudo = dados.analise || dados.resposta;

        if (conteudo) {
          mostrarAnalise(conteudo);
        } else {
          mostrarErro("⚠️ Erro: resposta inesperada do servidor.");
        }
      } catch (error) {
        console.error("Erro na requisição:", error);
        mostrarErro(`❌ Erro ao conectar: ${error.message}`);
      } finally {
        if (botao) botao.disabled = false;
        esconderLoader();
      }
    });
  }
  
  // ===============================
  // FILTROS AVANÇADOS (opcional)
  // ===============================
  const toggleFiltersBtn = document.getElementById("toggleFilters");
  const filtrosSection = document.getElementById("filtrosAvancados");
  const formFiltros = document.getElementById("formFiltros");

  if (toggleFiltersBtn && filtrosSection) {
    toggleFiltersBtn.addEventListener("click", () => {
      filtrosSection.classList.toggle("ativo");
      toggleFiltersBtn.textContent = filtrosSection.classList.contains("ativo")
        ? "Esconder Filtros ❌"
        : "Filtros Avançados 🔍";
    });
  }

  if (formFiltros) {
    const botaoFiltros = formFiltros.querySelector("button[type=submit]");

    formFiltros.addEventListener("submit", async (e) => {
      e.preventDefault();

      function coletarCheckboxes(nome) {
        return Array.from(formFiltros.querySelectorAll(`input[name='${nome}']:checked`)).map(cb => cb.value);
      }

      const linguagensSelecionadas = coletarCheckboxes("linguagens");
      const habilidadesSelecionadas = coletarCheckboxes("habilidades");
      const metodologiasSelecionadas = coletarCheckboxes("metodologias");

      if (!linguagensSelecionadas.length && !habilidadesSelecionadas.length && !metodologiasSelecionadas.length) {
        mostrarErro("❗ Selecione pelo menos uma opção em algum filtro.");
        if (botaoFiltros) botaoFiltros.disabled = false;
        return;
      }

      if (botaoFiltros) botaoFiltros.disabled = true;
      mostrarLoading("🔍 Buscando com filtros...");

      const dadosFiltros = {
        linguagens: linguagensSelecionadas,
        habilidades: habilidadesSelecionadas,
        metodologias: metodologiasSelecionadas
      };

      try {
        const resposta = await fetch("/analisar-com-filtros", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dadosFiltros),
        });

        if (!resposta.ok) {
          const dadosErro = await resposta.json().catch(() => ({}));
          const detalheErro = dadosErro.detail || dadosErro.erro || resposta.statusText;
          mostrarErro(`❌ Erro ${resposta.status}: ${detalheErro}`);
          return;
        }

        const dados = await resposta.json();
        const conteudo = dados.analise || dados.resposta;

        if (conteudo) {
          mostrarAnalise(conteudo);
        } else {
          mostrarErro("⚠️ Erro: resposta inesperada do servidor.");
        }
      } catch (error) {
        console.error("Erro na requisição:", error);
        mostrarErro(`❌ Erro ao conectar: ${error.message}`);
      } finally {
        if (botaoFiltros) botaoFiltros.disabled = false;
        esconderLoader();
      }
    });
  }

  // ===============================
  // BOTÃO DE CONTATO COM COPIAR EMAIL (sempre)
  // ===============================
  const contatoBtn = document.getElementById("contatoBtn");
  const emailContato = document.getElementById("emailContato");

  if (contatoBtn && emailContato) {
    contatoBtn.addEventListener("click", async (event) => {
      event.preventDefault();
      const email = emailContato.textContent.trim();
      try {
        await navigator.clipboard.writeText(email);
        contatoBtn.textContent = "📋 E-mail copiado!";
        setTimeout(() => { contatoBtn.textContent = "Contato"; }, 2000);
      } catch (err) {
        console.error("Erro ao copiar e-mail:", err);
        contatoBtn.textContent = "❌ Erro ao copiar";
        setTimeout(() => { contatoBtn.textContent = "Contato"; }, 2000);
      }
    });
  }

});
