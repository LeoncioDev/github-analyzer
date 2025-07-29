document.addEventListener("DOMContentLoaded", () => {
  const formulario = document.getElementById("formulario");
  const resultadoDiv = document.getElementById("resultado");
  const githubLinkInput = document.getElementById("githubLink");

  if (formulario && resultadoDiv && githubLinkInput) {
    formulario.addEventListener("submit", async (e) => {
      e.preventDefault();

      const botao = formulario.querySelector("button[type=submit]");
      const githubLink = githubLinkInput.value.trim();

      if (!githubLink) {
        resultadoDiv.innerHTML = `<p class="erro">❗ Por favor, insira uma URL do GitHub.</p>`;
        resultadoDiv.focus();
        return;
      }

      botao.disabled = true;
      resultadoDiv.innerHTML = "<p>🔍 Carregando análise...</p>";

      try {
        const resposta = await fetch("/analisar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ github_url: githubLink }),
        });

        const dados = await resposta.json();
        console.log("Resposta recebida:", dados);

        if (!resposta.ok) {
          resultadoDiv.innerHTML = `<p class="erro">❌ Erro ${resposta.status}: ${dados.erro || resposta.statusText}</p>`;
          resultadoDiv.focus();
          return;
        }

        const conteudo = dados.analise || dados.resposta;

        if (conteudo) {
          // Mostra HTML diretamente (sem usar marked, pois já está formatado)
          resultadoDiv.innerHTML = conteudo;
        } else {
          resultadoDiv.innerHTML = `<p class="erro">⚠️ Erro: resposta inesperada do servidor.</p>`;
        }

        setTimeout(() => resultadoDiv.focus(), 100);
      } catch (error) {
        console.error("Erro na requisição:", error);
        resultadoDiv.innerHTML = `<p class="erro">❌ Erro ao conectar: ${error.message}</p>`;
        setTimeout(() => resultadoDiv.focus(), 100);
      } finally {
        botao.disabled = false;
      }
    });
  } else {
    console.warn("⚠️ Elementos do DOM não encontrados.");
  }
});
