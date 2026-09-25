import pytest                               # Biblioteca de testagem
from datetime import datetime               #Faz o contraint de tipo data

from sqlalchemy import create_engine        # Inicializa a Engeine
from sqlalchemy.exc import IntegrityError   # Lança erro em caso de violação de integridade
from sqlalchemy.orm import sessionmaker     # Define as regras globais da conexão

from src.armazenamento import (             
    Base,
    RespostaDB,
    salvar_resposta,
)


@pytest.fixture
def session():
    """Cria um banco SQLite temporário para cada teste."""

    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    SessionTest = sessionmaker(bind=engine)
    session = SessionTest()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def criar_resposta(**kwargs):
    """Cria dados válidos para os testes."""

    dados = {
        "id": "resp-001",
        "pergunta": "Qual marca você recomenda?",
        "plataforma": "ChatGPT",
        "modelo": "GPT",
        "resposta_texto": "Eu recomendo a Acme.",
        "data_hora": datetime.now(),
        "sentimento": "positivo",
        "marcas_mencionadas": ["Acme"],
        "score_citacao": 1,
    }

    dados.update(kwargs)

    return dados


class TestArmazenamento:

    def test_insere_e_recupera_resposta(self, session):
        dados = criar_resposta()

        resposta = RespostaDB(**dados)

        session.add(resposta)
        session.commit()

        resultado = session.get(
            RespostaDB,
            "resp-001"
        )

        assert resultado is not None
        assert resultado.pergunta == "Qual marca você recomenda?"
        assert resultado.plataforma == "ChatGPT"
        assert resultado.marcas_mencionadas == ["Acme"]
        assert resultado.score_citacao == 1

    def test_score_padrao_zero(self, session):
        dados = criar_resposta(
            marcas_mencionadas=[]
        )

        dados.pop("score_citacao")

        resposta = RespostaDB(**dados)

        session.add(resposta)
        session.commit()

        resultado = session.get(
            RespostaDB,
            "resp-001"
        )

        assert resultado.score_citacao == 0

    def test_insercao_e_idempotente(self, session):
        dados = criar_resposta()

        salvar_resposta(session, dados)
        salvar_resposta(session, dados)

        resultados = session.query(RespostaDB).all()

        assert len(resultados) == 1
        assert resultados[0].id == "resp-001"

    def test_id_deve_ser_unico(self, session):
        primeira = criar_resposta(id="resp-001")
        segunda = criar_resposta(id="resp-001")

        session.add(RespostaDB(**primeira))
        session.commit()

        session.add(RespostaDB(**segunda))

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_armazena_texto_especial_com_seguranca(self, session):
        texto = "Resposta: 'Acme'; DROP TABLE respostas; --"

        dados = criar_resposta(
            resposta_texto=texto
        )

        session.add(RespostaDB(**dados))
        session.commit()

        resultado = session.get(
            RespostaDB,
            "resp-001"
        )

        assert resultado.resposta_texto == texto
        assert resultado.id == "resp-001"

    def test_erro_de_integridade_nao_compromete_sessao(
        self,
        session
    ):
        primeira = criar_resposta(id="resp-001")

        session.add(RespostaDB(**primeira))
        session.commit()

        segunda = criar_resposta(id="resp-001")

        session.add(RespostaDB(**segunda))

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

        resultado = session.get(
            RespostaDB,
            "resp-001"
        )

        assert resultado is not None