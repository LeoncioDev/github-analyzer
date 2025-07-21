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
        resultadoDiv.innerHTML = `<p class="erro">Por favor, insira uma URL do GitHub.</p>`;
        resultadoDiv.focus();
        return;
      }

      botao.disabled = true;
      resultadoDiv.innerHTML = "<p>Carregando análise...</p>";

      try {
        const resposta = await fetch("/analisar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ github_url: githubLink }),
        });

        if (!resposta.ok) {
          resultadoDiv.innerHTML = `<p class="erro">Erro HTTP: ${resposta.status} - ${resposta.statusText}</p>`;
          resultadoDiv.focus();
          return;
        }

        const dados = await resposta.json();

        if (dados.analise) {
          resultadoDiv.innerHTML = dados.analise;
        } else {
          resultadoDiv.innerHTML = `<p class="erro">Erro: ${dados.erro || "Resposta inesperada."}</p>`;
        }

        resultadoDiv.focus();
      } catch (error) {
        console.error(error);
        resultadoDiv.innerHTML = `<p class="erro">Erro na requisição: ${error.message}</p>`;
        resultadoDiv.focus();
      } finally {
        botao.disabled = false;
      }
    });
  } else {
    console.warn("Elementos necessários para funcionamento do formulário não encontrados.");
  }
});
