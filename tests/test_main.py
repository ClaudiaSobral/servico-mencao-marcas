import pytest
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  

# Imports dos módulos
from src.main import app, get_db, calcular_score
from src.armazenamento import (
    Base,
    RespostaDB,
    SessionLocal,
)


@pytest.fixture
def session():
    """Cria uma sessão SQLite em memória compartilhada entre threads.

    StaticPool + check_same_thread=False são necessários porque o
    TestClient do FastAPI executa as rotas em threads diferentes da
    que criou a engine — sem isso, cada thread abriria uma conexão
    nova para o banco :memory:, resultando em "no such table" (banco
    vazio) ou em erro de thread do sqlite3.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    SessionTest = sessionmaker(bind=engine)
    session = SessionTest()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(session):
    """Cria um cliente de teste sobrescrevendo a dependência get_db.

    Sobrescrever via app.dependency_overrides (em vez de monkeypatch em
    SessionLocal) é o padrão do FastAPI para injeção de dependências e evita
    que o `db.close()` do get_db feche a sessão compartilhada do teste.
    """

    app.dependency_overrides[get_db] = lambda: session

    yield TestClient(app)

    app.dependency_overrides.clear()


def criar_resposta(**kwargs):
    """Cria dados válidos para os testes."""

    dados = {
        "id": "resp-001",
        "pergunta": "Qual marca você recomenda?",
        "plataforma": "ChatGPT",
        "modelo": "GPT",
        "resposta_texto": "Eu recomendo a Acme.",
        "data_hora": "2026-09-25T10:00:00",
        "sentimento": "positivo",
    }

    dados.update(kwargs)

    return dados


class TestAdicionarResposta:

    def test_adicionar_resposta(self, client, session):
        """Deve analisar e armazenar uma nova resposta.

        O valor esperado do score é calculado chamando calcular_score
        diretamente, não hardcoded — este teste valida a integração
        (endpoint → detecção → score → persistência), não a fórmula em si.
        """

        dados = criar_resposta()

        response = client.post(
            "/respostas",
            json=dados
        )

        assert response.status_code == 200
        assert response.json() == {
            "status": "sucesso"
        }

        registro = session.get(
            RespostaDB,
            "resp-001"
        )

        esperado = calcular_score(
            texto=dados["resposta_texto"],
            marca="Acme",
            marcas_citadas=["Acme"],
            sentimento=dados["sentimento"],
        )

        assert registro is not None
        assert registro.marcas_mencionadas == ["Acme"]
        assert registro.score_citacao == pytest.approx(esperado)

    def test_adicionar_resposta_sem_marca(
        self,
        client,
        session
    ):
        """Deve armazenar uma resposta sem marcas mencionadas, sem erro.

        Regressão do bug de ZeroDivisionError: quando nenhuma marca é
        detectada, calcular_score não deve ser chamado (marcas_citadas
        vazia causava divisão por zero no cálculo de exclusividade).
        """

        dados = criar_resposta(
            resposta_texto="Não tenho uma recomendação específica."
        )

        response = client.post(
            "/respostas",
            json=dados
        )

        assert response.status_code == 200

        registro = session.get(
            RespostaDB,
            "resp-001"
        )

        assert registro is not None
        assert registro.marcas_mencionadas == []
        assert registro.score_citacao == 0

    def test_adicionar_resposta_e_idempotente(
        self,
        client,
        session
    ):
        """Não deve criar registros duplicados para o mesmo ID."""

        dados = criar_resposta()

        primeira = client.post(
            "/respostas",
            json=dados
        )

        segunda = client.post(
            "/respostas",
            json=dados
        )

        assert primeira.status_code == 200
        assert segunda.status_code == 200

        resultados = session.query(RespostaDB).all()

        assert len(resultados) == 1

    def test_adicionar_resposta_usa_primeira_marca_para_score(
        self,
        client,
        session
    ):
        """Pina a limitação conhecida: com múltiplas marcas na mesma
        resposta, o score é calculado com base apenas na primeira marca
        detectada (marcas[0]), não uma por marca.

        Este teste existe para que qualquer mudança nesse comportamento
        seja intencional (o teste quebra e força atualizar o README).
        """

        dados = criar_resposta(
            resposta_texto="Recomendo a Zenith, mas a Acme também é boa opção."
        )

        response = client.post(
            "/respostas",
            json=dados
        )

        assert response.status_code == 200

        registro = session.get(RespostaDB, "resp-001")
        marca_usada_no_score = registro.marcas_mencionadas[0]

        esperado = calcular_score(
            texto=dados["resposta_texto"],
            marca=marca_usada_no_score,
            marcas_citadas=registro.marcas_mencionadas,
            sentimento=dados["sentimento"],
        )

        assert registro.score_citacao == pytest.approx(esperado)


class TestShareOfVoice:

    def inserir_respostas(self, session):
        """Insere respostas de teste para os testes de Share of Voice."""

        respostas = [
            RespostaDB(
                id="resp-001",
                pergunta="Pergunta 1",
                plataforma="ChatGPT",
                modelo="GPT",
                resposta_texto="Acme é uma opção.",
                data_hora=datetime(2026, 9, 25, 10, 0),
                sentimento="positivo",
                marcas_mencionadas=["Acme"],
                score_citacao=1,
            ),
            RespostaDB(
                id="resp-002",
                pergunta="Pergunta 2",
                plataforma="ChatGPT",
                modelo="GPT",
                resposta_texto="Acme é bastante conhecida.",
                data_hora=datetime(2026, 9, 25, 11, 0),
                sentimento="positivo",
                marcas_mencionadas=["Acme"],
                score_citacao=1,
            ),
            RespostaDB(
                id="resp-003",
                pergunta="Pergunta 3",
                plataforma="ChatGPT",
                modelo="GPT",
                resposta_texto="Zenith é uma opção.",
                data_hora=datetime(2026, 9, 25, 12, 0),
                sentimento="neutro",
                marcas_mencionadas=["Zenith"],
                score_citacao=1,
            ),
            RespostaDB(
                id="resp-004",
                pergunta="Pergunta 4",
                plataforma="ChatGPT",
                modelo="GPT",
                resposta_texto="Não tenho uma recomendação.",
                data_hora=datetime(2026, 9, 25, 13, 0),
                sentimento="neutro",
                marcas_mencionadas=[],
                score_citacao=0,
            ),
        ]

        session.add_all(respostas)
        session.commit()

    def test_share_of_voice(self, client, session):
        """Deve calcular corretamente o Share of Voice."""

        self.inserir_respostas(session)

        response = client.get(
            "/share-of-voice?marca=Acme"
        )

        assert response.status_code == 200

        resultado = response.json()

        assert resultado["marca"] == "Acme"
        assert resultado["total_respostas"] == 4
        assert resultado["mencoes"] == 2
        assert resultado["share_of_voice"] == 50.0

    def test_share_of_voice_ignora_maiusculas(
        self,
        client,
        session
    ):
        """A busca pela marca deve ignorar diferenças de maiúsculas."""

        self.inserir_respostas(session)

        response = client.get(
            "/share-of-voice?marca=acme"
        )

        assert response.status_code == 200
        assert response.json()["mencoes"] == 2
        assert response.json()["share_of_voice"] == 50.0

    def test_share_of_voice_marca_inexistente(
        self,
        client,
        session
    ):
        """Deve retornar zero para uma marca monitorada sem menções."""

        self.inserir_respostas(session)

        response = client.get(
            "/share-of-voice?marca=Nimbus"
        )

        assert response.status_code == 200

        resultado = response.json()

        assert resultado["mencoes"] == 0
        assert resultado["share_of_voice"] == 0.0

    def test_share_of_voice_marca_nao_monitorada(
        self,
        client,
        session
    ):
        """Documenta o comportamento atual: uma marca fora da lista fixa
        (ex.: erro de digitação do cliente da API) hoje retorna 0%
        silenciosamente, em vez de um erro explícito.

        Este teste serve para deixar essa decisão de escopo visível — se
        no futuro a rota passar a validar contra a lista fixa (e retornar
        400), este teste deve ser atualizado junto.
        """

        self.inserir_respostas(session)

        response = client.get(
            "/share-of-voice?marca=Coca-Cola"
        )

        assert response.status_code == 200
        assert response.json()["share_of_voice"] == 0.0

    def test_share_of_voice_sem_dados(self, client):
        """Deve retornar 404 quando não houver respostas."""

        response = client.get(
            "/share-of-voice?marca=Acme"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Sem dados"


class TestTopCitacoes:

    def inserir_respostas(self, session):
        """Insere respostas com diferentes scores.

        Os scores aqui são valores fixos inseridos direto no banco (não
        passam por calcular_score) — o objetivo destes testes é validar
        a ordenação/paginação da rota, não a fórmula de score.
        """

        respostas = [
            RespostaDB(
                id="resp-001",
                pergunta="Pergunta 1",
                plataforma="ChatGPT",
                modelo="GPT",
                resposta_texto="Acme.",
                data_hora=datetime(2026, 9, 25, 10, 0),
                sentimento="positivo",
                marcas_mencionadas=["Acme"],
                score_citacao=1,
            ),
            RespostaDB(
                id="resp-002",
                pergunta="Pergunta 2",
                plataforma="ChatGPT",
                modelo="GPT",
                resposta_texto="Acme e Zenith.",
                data_hora=datetime(2026, 9, 25, 11, 0),
                sentimento="positivo",
                marcas_mencionadas=["Acme", "Zenith"],
                score_citacao=5,
            ),
            RespostaDB(
                id="resp-003",
                pergunta="Pergunta 3",
                plataforma="ChatGPT",
                modelo="GPT",
                resposta_texto="Zenith.",
                data_hora=datetime(2026, 9, 25, 12, 0),
                sentimento="neutro",
                marcas_mencionadas=["Zenith"],
                score_citacao=3,
            ),
        ]

        session.add_all(respostas)
        session.commit()

    def test_top_citacoes_ordena_por_score(
        self,
        client,
        session
    ):
        """Deve retornar as respostas em ordem decrescente de score."""

        self.inserir_respostas(session)

        response = client.get("/top-citacoes")

        assert response.status_code == 200

        resultados = response.json()

        assert len(resultados) == 3
        assert resultados[0]["id"] == "resp-002"
        assert resultados[1]["id"] == "resp-003"
        assert resultados[2]["id"] == "resp-001"

    def test_top_citacoes_respeita_limite(
        self,
        client,
        session
    ):
        """Deve retornar no máximo n registros."""

        self.inserir_respostas(session)

        response = client.get(
            "/top-citacoes?n=2"
        )

        assert response.status_code == 200

        resultados = response.json()

        assert len(resultados) == 2
        assert resultados[0]["id"] == "resp-002"
        assert resultados[1]["id"] == "resp-003"

    def test_top_citacoes_com_n_zero(self, client):
        """Deve rejeitar n igual a zero."""

        response = client.get(
            "/top-citacoes?n=0"
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "n deve ser maior que zero"
        )

    def test_top_citacoes_com_n_negativo(self, client):
        """Deve rejeitar valores negativos para n."""

        response = client.get(
            "/top-citacoes?n=-1"
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "n deve ser maior que zero"
        )