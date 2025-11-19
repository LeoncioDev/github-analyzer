document.addEventListener("DOMContentLoaded", () => {
  // --- SELETORES PRINCIPAIS ---
  const contextRadios = document.querySelectorAll('input[name="contexto"]');
  const analysisArea = document.getElementById("analysisArea");
  const advancedFiltersArea = document.getElementById("advancedFiltersArea");

  // Sub-seções de Recrutador
  const rankingToggleWrapper = document.getElementById("rankingToggleWrapper");
  const toggleRanking = document.getElementById("toggleRanking");
  const simpleFormContainer = document.getElementById("simpleFormContainer");
  const rankingFormContainer = document.getElementById("rankingFormContainer");

  // Inputs e Formulários
  const formSimple = document.getElementById("formulario");
  const githubUsername = document.getElementById("githubUsername");
  const formRanking = document.getElementById("formRanking");
  const formFiltros = document.getElementById("formFiltros");
  
  const cancelRankingBtn = document.getElementById("cancelRankingBtn");

  // Resultados e Feedback
  const resultadoDiv = document.getElementById("resultado");
  const loader = document.getElementById("loader");
  const errorMessage = document.getElementById("errorMessage");
  
  // Tema
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;

  // --- GERENCIAMENTO DE TEMA  ---
  // Carregar tema salvo
  if (localStorage.getItem("tema") === "claro") {
    body.classList.add("modo-claro");
    themeToggle.textContent = "☀️";
  }

  themeToggle.addEventListener("click", () => {
    const isLight = body.classList.toggle("modo-claro");
    themeToggle.textContent = isLight ? "☀️" : "🌙";
    localStorage.setItem("tema", isLight ? "claro" : "escuro");
  });

  // --- GERENCIAMENTO DE VISIBILIDADE ---
  function updateView() {
    const selected = document.querySelector('input[name="contexto"]:checked').value;
    
    // Reset inicial
    resultadoDiv.classList.remove("ativo");
    errorMessage.classList.add("hidden");
    analysisArea.classList.add("hidden");
    advancedFiltersArea.classList.add("hidden");
    rankingToggleWrapper.classList.add("hidden");

    if (selected === "recrutamento") {
      analysisArea.classList.remove("hidden");
      rankingToggleWrapper.classList.remove("hidden");
      updateRecruiterMode();
      githubUsername.placeholder = "Cole o link do GitHub ou digite o usuário do candidato...";
    } 
    else if (selected === "autoanalise") {
      analysisArea.classList.remove("hidden");
      simpleFormContainer.classList.remove("hidden");
      rankingFormContainer.classList.add("hidden");
      githubUsername.placeholder = "Digite seu nome de usuário do GitHub...";
      toggleRanking.checked = false;
    } 
    else if (selected === "filtros") {
      advancedFiltersArea.classList.remove("hidden");
    }
  }

  function updateRecruiterMode() {
    if (toggleRanking.checked) {
      simpleFormContainer.classList.add("hidden");
      rankingFormContainer.classList.remove("hidden");
    } else {
      simpleFormContainer.classList.remove("hidden");
      rankingFormContainer.classList.add("hidden");
    }
  }

  contextRadios.forEach(r => r.addEventListener("change", updateView));
  if (toggleRanking) toggleRanking.addEventListener("change", updateRecruiterMode);

  if (cancelRankingBtn) {
    cancelRankingBtn.addEventListener("click", () => {
      toggleRankingCheckbox.checked = false;
      updateRecruiterMode();
    });
  }

  // Inicialização
  updateView();


  // --- LÓGICA DE RANKING (Lista de Candidatos) ---
  const addCandidateBtn = document.getElementById("addCandidateBtn");
  const newCandidateInput = document.getElementById("newCandidateUrl");
  const candidateListDiv = document.getElementById("candidateList");
  let candidateURLs = [];

  if (addCandidateBtn) {
    addCandidateBtn.addEventListener("click", () => {
      const url = newCandidateInput.value.trim();
      if (!url) return;
      
      if (candidateURLs.includes(url)) {
        showError("Candidato já adicionado.");
        return;
      }
      // --- MÁXIMO 3 ---
      if (candidateURLs.length >= 3) {
        showError("Máximo de 3 candidatos permitidos.");
        return;
      }

      candidateURLs.push(url);
      renderCandidates();
      newCandidateInput.value = "";
      errorMessage.classList.add("hidden");
    });
  }

  function renderCandidates() {
    candidateListDiv.innerHTML = "";
    candidateURLs.forEach(url => {
      const div = document.createElement("div");
      div.className = "candidate-item";
      div.innerHTML = `<span>${url}</span> <button type="button" onclick="removeCandidate('${url}')"><i class="fas fa-times"></i></button>`;
      candidateListDiv.appendChild(div);
    });
  }

  window.removeCandidate = (url) => {
    candidateURLs = candidateURLs.filter(c => c !== url);
    renderCandidates();
  };


  // --- ENVIOS (SUBMITS) ---
  
  // 1. Form Simples
  formSimple.addEventListener("submit", async (e) => {
    e.preventDefault();
    const user = githubUsername.value.trim();
    const context = document.querySelector('input[name="contexto"]:checked').value;
    if (!user) return showError("Digite um usuário.");
    
    await processRequest("/analisar-perfil", { usernameOrUrl: user, contexto: context });
  });

  // 2. Form Ranking
  formRanking.addEventListener("submit", async (e) => {
    e.preventDefault();
    const jd = document.getElementById("jobDescription").value.trim();
    if (!jd) return showError("Preencha a descrição da vaga.");
    if (candidateURLs.length < 1) return showError("Adicione candidatos.");
    
    await processRequest("/ranking-vaga", { jobDescription: jd, candidateUrls: candidateURLs });
  });

  // 3. Filtros
  formFiltros.addEventListener("submit", async (e) => {
    e.preventDefault();
    const getChecked = (name) => Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(cb => cb.value);
    const linguagens = getChecked("linguagens");
    const habilidades = getChecked("habilidades");
    const metodologias = getChecked("metodologias");
    
    if (linguagens.length === 0 && habilidades.length === 0 && metodologias.length === 0) return showError("Selecione filtros.");

    await processRequest("/analisar-com-filtros", {
      linguagens, habilidades, metodologias, minRepos: 5, atividadeRecente: true
    });
  });


  // --- HELPERS ---
  async function processRequest(endpoint, data) {
    loader.classList.remove("hidden");
    resultadoDiv.classList.remove("ativo");
    errorMessage.classList.add("hidden");

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      
      if (!response.ok) throw new Error(result.detail || "Erro na requisição.");

      resultadoDiv.innerHTML = result.analise || result.resposta;
      resultadoDiv.classList.add("ativo");
      
      setTimeout(() => resultadoDiv.scrollIntoView({ behavior: "smooth" }), 100);

    } catch (error) {
      showError(error.message);
    } finally {
      loader.classList.add("hidden");
    }
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.classList.remove("hidden");
    loader.classList.add("hidden");
  }
});
