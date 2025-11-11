document.addEventListener("DOMContentLoaded", () => {
  // ===============================
  // ELEMENTOS DA PÁGINA
  // ===============================
  const simpleAnalysisSection = document.getElementById("simpleAnalysisSection");
  const simpleAnalysisButtons = document.getElementById("simpleAnalysisButtons");
  const rankingAnalysisSection = document.getElementById("rankingAnalysisSection");
  const rankingToggleField = document.getElementById("rankingToggleField");
  const toggleRankingCheckbox = document.getElementById("toggleRanking");
  const contextRadios = document.querySelectorAll('input[name="contexto"]');
  
  // Elementos dos formulários
  const formulario = document.getElementById("formulario");
  const githubUsernameInput = document.getElementById("githubUsername");
  const formRanking = document.getElementById("formRanking");
  const cancelRankingBtn = document.getElementById("cancelRankingBtn");
  
  // Elementos de feedback
  const resultadoDiv = document.getElementById("resultado");
  const loaderContainer = document.getElementById("loader");
  
  // ===============================
  // TEMA
  // ===============================
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;
  
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
  // FUNÇÕES DE FEEDBACK
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
      resultadoDiv.classList.add("ativo"); // MOSTRAR a caixa de insights com o erro
      resultadoDiv.focus();
    }
    if (loaderContainer) loaderContainer.style.display = "none";
  }

  function mostrarLoading(mensagem) {
    if (resultadoDiv) {
      resultadoDiv.innerHTML = `<p class="carregando" tabindex="0">${mensagem} <span class="dots">.</span></p>`;
      resultadoDiv.classList.add("ativo"); // MOSTRAR a caixa de insights com o loading
      resultadoDiv.focus();
      startDotsAnimation();
    }
    if (loaderContainer) loaderContainer.style.display = "flex";
  }

  function mostrarAnalise(conteudo) {
    stopDotsAnimation();
    if (resultadoDiv) {
      if (conteudo) {
        resultadoDiv.innerHTML = conteudo;
        resultadoDiv.classList.add("ativo"); // MOSTRAR a caixa de insights
        resultadoDiv.focus();
      } else {
        // Se o conteúdo for vazio, ESCONDER a caixa
        resultadoDiv.innerHTML = "";
        resultadoDiv.classList.remove("ativo");
      }
    }
    if (loaderContainer) loaderContainer.style.display = "none";
  }
  
  // ===============================
  // LÓGICA DE TROCA DE FORMULÁRIO
  // ===============================

  function updateFormVisibility() {
    const selectedContext = document.querySelector('input[name="contexto"]:checked').value;
    const isRankingActive = toggleRankingCheckbox.checked;

    if (selectedContext === 'autoanalise') {
      // MODO: ANALISAR MEU PERFIL
      rankingToggleField.classList.add('hidden');
      simpleAnalysisSection.classList.remove('hidden');
      simpleAnalysisButtons.classList.remove('hidden');
      rankingAnalysisSection.classList.add('hidden');
    
    } else if (selectedContext === 'recrutamento') {
      // MODO: AVALIAR CANDIDATO
      rankingToggleField.classList.remove('hidden');
      
      if (isRankingActive) {
        // MODO: AVALIAR (RANKING)
        simpleAnalysisSection.classList.add('hidden');
        simpleAnalysisButtons.classList.add('hidden');
        rankingAnalysisSection.classList.remove('hidden');
      } else {
        // MODO: AVALIAR (SIMPLES)
        simpleAnalysisSection.classList.remove('hidden');
        simpleAnalysisButtons.classList.remove('hidden');
        rankingAnalysisSection.classList.add('hidden');
      }
    }
    // Limpar resultados e erros ao trocar de modo
    mostrarAnalise(""); // ESCONDER a caixa de insights
  }

  contextRadios.forEach(radio => radio.addEventListener('change', updateFormVisibility));
  toggleRankingCheckbox.addEventListener('change', updateFormVisibility);
  
  if (cancelRankingBtn) {
    cancelRankingBtn.addEventListener("click", () => {
      toggleRankingCheckbox.checked = false;
      updateFormVisibility();
    });
  }
  
  updateFormVisibility(); // Estado inicial

  // ===============================
  // LÓGICA DO FORMULÁRIO DE RANKING
  // ===============================
  const addCandidateBtn = document.getElementById("addCandidateBtn");
  const newCandidateInput = document.getElementById("newCandidateUrl");
  const candidateListDiv = document.getElementById("candidateList");
  let candidateURLs = [];

  if (addCandidateBtn) {
    addCandidateBtn.addEventListener("click", () => {
      const url = newCandidateInput.value.trim();
      if (url) {
        if (candidateURLs.includes(url)) {
            mostrarErro("❗ Candidato já adicionado.");
            return;
        }
        candidateURLs.push(url);
        
        const item = document.createElement("div");
        item.className = "candidate-item";
        item.innerHTML = `<span>${url}</span><button type="button" data-url="${url}">&times;</button>`;
        candidateListDiv.appendChild(item);
        
        newCandidateInput.value = "";
        mostrarAnalise(""); // Limpa qualquer erro
      }
    });

    candidateListDiv.addEventListener("click", (e) => {
      if (e.target.tagName === "BUTTON") {
        const urlToRemove = e.target.getAttribute("data-url");
        candidateURLs = candidateURLs.filter(url => url !== urlToRemove);
        e.target.parentElement.remove();
      }
    });
  }

  if (formRanking) {
    const submitButton = formRanking.querySelector("button[type='submit']");

    formRanking.addEventListener("submit", async (e) => {
      e.preventDefault();
      const jobDescription = document.getElementById("jobDescription").value.trim();

      if (!jobDescription) {
        mostrarErro("❗ Por favor, preencha a Descrição da Vaga.");
        return;
      }
      if (candidateURLs.length === 0) {
        mostrarErro("❗ Adicione pelo menos um candidato para análise.");
        return;
      }
      
      if (submitButton) submitButton.disabled = true;
      
      mostrarLoading("🔍 Analisando e rankeando candidatos..."); 
      
      try {
        const resposta = await fetch("/ranking-vaga", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ jobDescription: jobDescription, candidateUrls: candidateURLs }),
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
          mostrarErro("⚠️ Erro: resposta inesperada do servidor para o ranking.");
        }
      } catch (error) {
        console.error("Erro na requisição de ranking:", error);
        mostrarErro(`❌ Erro ao conectar ao servidor para ranking: ${error.message}`);
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    });
  }

  // ===============================
  // LÓGICA DO FORMULÁRIO DE ANÁLISE SIMPLES
  // ===============================
  if (formulario && resultadoDiv && githubUsernameInput) {
    const botao = formulario.querySelector('button[type=submit]');

    formulario.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = githubUsernameInput.value.trim();

      if (!username) {
        githubUsernameInput.classList.add("input-erro");
        mostrarErro("❗ Por favor, insira o nome de usuário ou URL do GitHub.");
        return;
      } else {
        githubUsernameInput.classList.remove("input-erro");
      }
      
      const contextoSelecionado = document.querySelector('input[name="contexto"]:checked');
      const contexto = contextoSelecionado ? contextoSelecionado.value : "recrutamento";

      if (botao) botao.disabled = true;
      mostrarLoading("🔍 Carregando análise");

      try {
        const resposta = await fetch("/analisar-perfil", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ usernameOrUrl: username, contexto: contexto }),
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
      }
    });
  }

  // ===============================
  // FILTROS AVANÇADOS
  // ===============================
  const toggleFiltersBtn = document.getElementById("toggleFilters");
  const filtrosSection = document.getElementById("filtrosAvancados");
  
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
      
      const minRepos = formFiltros.querySelector("#minRepos") ? parseInt(formFiltros.querySelector("#minRepos").value) || 0 : 0;
      const minStars = formFiltros.querySelector("#minStars") ? parseInt(formFiltros.querySelector("#minStars").value) || 0 : 0;
      const minFollowers = formFiltros.querySelector("#minFollowers") ? parseInt(formFiltros.querySelector("#minFollowers").value) || 0 : 0;
      const atividadeRecente = formFiltros.querySelector("#atividadeRecente") ? formFiltros.querySelector("#atividadeRecente").checked : false;
      const localizacao = formFiltros.querySelector("#localizacao") ? formFiltros.querySelector("#localizacao").value.trim() : null;


      if (botaoFiltros) botaoFiltros.disabled = true;
      mostrarLoading("🔍 Buscando com filtros...");

      const dadosFiltros = {
        linguagens: linguagensSelecionadas,
        habilidades: habilidadesSelecionadas,
        metodologias: metodologiasSelecionadas,
        minRepos,
        minStars,
        minFollowers,
        atividadeRecente,
        localizacao
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
      }
    });
  }

  // ===============================
  // BOTÃO DE CONTATO
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
