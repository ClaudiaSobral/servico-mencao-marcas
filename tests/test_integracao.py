"""Testes de integração do serviço de análise de menções.

Diferente dos testes de unidade (que já cobrem o detector e a ingestão
isoladamente), aqui o objetivo é validar que as camadas se conectam
corretamente: requisição HTTP -> validação Pydantic -> detecção de
menções -> persistência -> consulta. Cada teste cobre um caminho de
dados diferente pela aplicação, evitando sobreposição entre eles.

Banco de dados: usamos SQLite em memória (isolado do mencoes.db real)
com StaticPool para manter a mesma conexão entre as sessões abertas
durante um teste. As tabelas são recriadas a cada teste via fixture,
então não há estado compartilhado entre eles.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.armazenamento import Base
from src.main import app, get_db

# --- Banco de teste: SQLite em memória, isolado do banco real ---------

engine_teste = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTeste = sessionmaker(bind=engine_teste)


def _sobrescrever_get_db():
    """Substitui a dependência get_db do app pelo banco de teste."""
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    """Sobe um TestClient com um banco em memória limpo por teste."""
    Base.metadata.create_all(bind=engine_teste)
    app.dependency_overrides[get_db] = _sobrescrever_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_teste)


# --- Helper para montar payloads válidos de /respostas -----------------

def _payload(id, texto, plataforma="ChatGPT", sentimento=None,
             pergunta="Qual a melhor opção?", modelo="gpt-4",
             data_hora="2026-01-01T10:00:00"):
    return {
        "id": id,
        "pergunta": pergunta,
        "plataforma": plataforma,
        "modelo": modelo,
        "resposta_texto": texto,
        "data_hora": data_hora,
        "sentimento": sentimento,
    }


# --- 1. Inserção -> consulta --------------------------------------------

def test_insercao_persiste_e_aparece_na_consulta(client):
    """A resposta enviada via POST precisa percorrer toda a aplicação
    (validação -> detecção -> persistência) e ficar disponível para
    consulta via GET. Sem esse caminho funcionando, nenhum outro teste
    de integração tem sentido.
    """
    resposta = client.post(
        "/respostas",
        json=_payload("r1", "A Acme é usada aqui.", sentimento="neutro"),
    )
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "sucesso"}

    consulta = client.get("/share-of-voice", params={"marca": "Acme"})
    assert consulta.status_code == 200
    corpo = consulta.json()
    assert corpo["total_respostas"] == 1
    assert corpo["mencoes"] == 1
    assert corpo["share_of_voice"] == 100.0


# --- 2. Múltiplas respostas -> Share of Voice ---------------------------

def test_share_of_voice_combina_deteccao_persistencia_e_calculo(client):
    """Insere respostas com e sem a marca monitorada, em duas
    plataformas diferentes, e valida o cálculo agregado e por
    plataforma. Cobre detecção (marca precisa ser reconhecida no
    texto), persistência (todas precisam estar salvas) e o cálculo do
    percentual em si — inclusive o caso de marca ausente, que não pode
    ser contabilizado indevidamente.
    """
    client.post("/respostas", json=_payload("r1", "A Acme lidera o mercado.", plataforma="ChatGPT"))
    client.post("/respostas", json=_payload("r2", "Prefiro a Zenith para isso.", plataforma="ChatGPT"))
    client.post("/respostas", json=_payload("r3", "A Acme é uma boa opção.", plataforma="Gemini"))
    client.post("/respostas", json=_payload("r4", "Não conheço nenhuma marca boa.", plataforma="Gemini"))

    resposta = client.get("/share-of-voice", params={"marca": "Acme"})
    assert resposta.status_code == 200
    corpo = resposta.json()

    assert corpo["total_respostas"] == 4
    assert corpo["mencoes"] == 2
    assert corpo["share_of_voice"] == 50.0

    assert corpo["por_plataforma"]["ChatGPT"] == {
        "total_respostas": 2, "mencoes": 1, "share_of_voice": 50.0,
    }
    assert corpo["por_plataforma"]["Gemini"] == {
        "total_respostas": 2, "mencoes": 1, "share_of_voice": 50.0,
    }


# --- 3. Inserção -> /top-citacoes ---------------------------------------

def test_score_do_detector_chega_integro_ao_top_citacoes(client):
    """O score calculado em calcular_score (frequência, contexto,
    posição, exclusividade e sentimento) precisa chegar sem distorção
    do POST até a ordenação do GET /top-citacoes. Uma citação "forte"
    (marca única, cedo no texto, junto de palavra de recomendação,
    sentimento positivo) deve vir antes de uma citação "fraca"
    (menção incidental, sem contexto de recomendação, sentimento
    neutro).
    """
    forte = _payload(
        "forte-1",
        "Acme é a melhor escolha do mercado, recomendo sem dúvida.",
        sentimento="positivo",
    )
    fraca = _payload(
        "fraca-1",
        "Testamos várias ferramentas ao longo do projeto e, entre "
        "outras, usamos a Zenith uma vez.",
        sentimento="neutro",
    )

    client.post("/respostas", json=forte)
    client.post("/respostas", json=fraca)

    resposta = client.get("/top-citacoes", params={"n": 2})
    assert resposta.status_code == 200
    resultados = resposta.json()

    assert len(resultados) == 2
    assert resultados[0]["id"] == "forte-1"
    assert resultados[1]["id"] == "fraca-1"
    assert resultados[0]["score_citacao"] > resultados[1]["score_citacao"] > 0


# --- 4. Entrada inválida -------------------------------------------------

def test_entrada_invalida_e_rejeitada_pela_api(client):
    """Como o serviço recebe dados de scraping (potencialmente sujos),
    a validação de contrato na borda da API precisa estar de fato
    conectada ao endpoint: campos obrigatórios ausentes ou com tipo
    errado devem ser barrados antes de qualquer detecção ou persistência.
    """
    payload_incompleto = {"id": "invalido-1"}
    resposta = client.post("/respostas", json=payload_incompleto)
    assert resposta.status_code == 422

    payload_data_invalida = _payload("invalido-2", "Texto qualquer.")
    payload_data_invalida["data_hora"] = "não é uma data"
    resposta2 = client.post("/respostas", json=payload_data_invalida)
    assert resposta2.status_code == 422

    # nada deve ter sido persistido a partir dos payloads inválidos
    consulta = client.get("/share-of-voice", params={"marca": "Acme"})
    assert consulta.status_code == 404