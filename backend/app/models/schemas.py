# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

# --- MODELOS PARA ANÁLISE SIMPLES ---
class UserInput(BaseModel):
    usernameOrUrl: str
    contexto: str

# --- MODELOS PARA FILTROS ---
class FiltrosInput(BaseModel):
    linguagens: List[str] = []
    habilidades: List[str] = []
    metodologias: List[str] = []
    minRepos: int = 0
    minStars: int = 0
    minFollowers: int = 0
    atividadeRecente: bool = False
    localizacao: Optional[str] = None

# --- MODELOS PARA RANKING DE VAGA ---
class RankingInput(BaseModel):
    jobDescription: str = Field(..., min_length=50, max_length=5000)
    candidateUrls: List[str] = Field(..., min_items=1, max_items=5)

class CandidateDataForRanking(BaseModel):
    username: str
    nome: str
    html_url: str
    analise_html: str # Análise detalhada gerada pela IA para este candidato
