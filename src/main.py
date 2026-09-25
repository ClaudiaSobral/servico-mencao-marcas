import math                                             # Importa o método de logaritmo
import re                                               # Importa expressões regex

from fastapi import FastAPI, HTTPException, Depends     # Importa FastAPI, tratamento de erros e módulo de reaproveitamento de código
from sqlalchemy.orm import Session                      # Permite abri o banco de dados no Python

# Imports dos módulos
from src.armazenamento import (                         
    SessionLocal,
    criar_tabelas,
    RespostaDB,
    salvar_resposta,
)
from src.deteccao_mencoes import DetectorMencoes
from src.modelo_json import RespostaBase


app = FastAPI(                                          # Inicialização do FastAPI
    title="Servico de Analise de Mencoes"
)


criar_tabelas()

# Lista de expressões que podem aumentar a "força" das menções
PALAVRAS_RECOMENDACAO = [
    "recomendo", "recomendada", "recomendável", "melhor", "líder",
    "referência", "principal escolha", "top", "excelente opção",
]

PESO_SENTIMENTO = {"positivo": 1.2, "neutro": 1.0, "negativo": 0.6}


def get_db():
    """Cria e fecha uma sessão de banco por requisição (dependency do FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calcular_score(
    texto: str,
    marca: str,
    marcas_citadas: list[str],
    sentimento: str | None,
) -> float:
    """Calcula a "força" de uma citação combinando frequência, contexto,
    posição, exclusividade e sentimento — não apenas contagem de menções.

    Args:
        texto: Texto completo da resposta analisada.
        marca: Marca cuja força de citação está sendo calculada.
        marcas_citadas: Lista de todas as marcas monitoradas citadas na resposta.
        sentimento: Sentimento da resposta ("positivo", "neutro", "negativo" ou None).

    Returns:
        Score numérico de força da citação (quanto maior, mais forte).
    """
    texto_lower = texto.lower()
    marca_lower = marca.lower()

    # Frequência com retorno decrescente (log evita que repetição mecânica domine)
    ocorrencias = texto_lower.count(marca_lower)
    score_frequencia = math.log1p(ocorrencias)

    # Contexto: a marca aparece na mesma sentença que uma palavra de recomendação?
    sentencas = re.split(r'(?<=[.!?])\s+', texto)
    score_contexto = 0.0
    for sentenca in sentencas:
        s_lower = sentenca.lower()
        if marca_lower in s_lower and any(p in s_lower for p in PALAVRAS_RECOMENDACAO):
            score_contexto = 1.0
            break

    # Posição: menção no primeiro terço do texto pesa mais (resposta "abre" com ela)
    posicao_primeira = texto_lower.find(marca_lower)
    score_posicao = 1.0 if 0 <= posicao_primeira < len(texto) / 3 else 0.3

    # Exclusividade: quanto menos marcas concorrentes citadas, mais "decidida" é a resposta
    score_exclusividade = 1.0 if len(marcas_citadas) == 1 else (1.0 / len(marcas_citadas))

    # Sentimento da resposta como multiplicador
    peso_sentimento = PESO_SENTIMENTO.get((sentimento or "neutro").lower(), 1.0)

    score_base = (
        0.3 * score_frequencia
        + 0.3 * score_contexto
        + 0.2 * score_posicao
        + 0.2 * score_exclusividade
    )

    return round(score_base * peso_sentimento, 3)


@app.post("/respostas")
def adicionar_resposta(resposta: RespostaBase, db: Session = Depends(get_db)):
    """Detecta marcas no texto recebido, calcula o score de citação e persiste a resposta."""
    marcas, _ = DetectorMencoes.detectar(resposta.resposta_texto)

    score = 0.0
    if marcas:
        score = calcular_score(
            texto=resposta.resposta_texto,
            marca=marcas[0],
            marcas_citadas=marcas,
            sentimento=resposta.sentimento,
        )

    dados = {
        **resposta.model_dump(),
        "marcas_mencionadas": marcas,
        "score_citacao": score,
    }

    salvar_resposta(db, dados)

    return {"status": "sucesso"}


@app.get("/share-of-voice")
def share_of_voice(marca: str, db: Session = Depends(get_db)):
    """Calcula o percentual de respostas que citam a marca informada,
    no total e discriminado por plataforma."""
    respostas = db.query(RespostaDB).all()
    total = len(respostas)

    if total == 0:
        raise HTTPException(status_code=404, detail="Sem dados")

    marca_normalizada = marca.lower()

    def cita_marca(resposta):
        return marca_normalizada in [m.lower() for m in (resposta.marcas_mencionadas or [])]

    quantidade_mencoes = sum(1 for r in respostas if cita_marca(r))

    contagem_por_plataforma: dict[str, dict[str, int]] = {}
    for resposta in respostas:
        stats = contagem_por_plataforma.setdefault(
            resposta.plataforma, {"total_respostas": 0, "mencoes": 0}
        )
        stats["total_respostas"] += 1
        if cita_marca(resposta):
            stats["mencoes"] += 1

    por_plataforma = {
        plataforma: {
            "total_respostas": stats["total_respostas"],
            "mencoes": stats["mencoes"],
            "share_of_voice": round(stats["mencoes"] / stats["total_respostas"] * 100, 2),
        }
        for plataforma, stats in contagem_por_plataforma.items()
    }

    return {
        "marca": marca,
        "total_respostas": total,
        "mencoes": quantidade_mencoes,
        "share_of_voice": round(quantidade_mencoes / total * 100, 2),
        "por_plataforma": por_plataforma,
    }

@app.get("/top-citacoes")
def top_citacoes(n: int = 5, db: Session = Depends(get_db)):
    """Retorna as N respostas com maior score de força de citação."""
    if n < 1:
        raise HTTPException(status_code=400, detail="n deve ser maior que zero")

    resultados = (
        db.query(RespostaDB)
        .order_by(RespostaDB.score_citacao.desc())
        .limit(n)
        .all()
    )

    return resultados