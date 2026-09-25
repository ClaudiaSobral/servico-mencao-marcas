from datetime import datetime
import json
import logging
import pytest
from pathlib import Path
from pydantic import ValidationError

from src.modelo_json import RespostaBase, RespostaProcessada
from src.ingestao import ServicoIngestao


logger = logging.getLogger(__name__)


def test_criar_resposta_valida(caplog):

    with caplog.at_level(logging.INFO, logger="src.modelo_json"):
        resposta = RespostaBase(
            id="1",
            pergunta="Qual a melhor marca?",
            plataforma="ChatGPT",
            modelo="gpt-4",
            resposta_texto="Acme é uma opção",
            data_hora="2025-01-01T10:00:00"
        )

    assert resposta.id == "1"
    assert "criada com sucesso" in caplog.text

    
def test_criar_resposta_valida(caplog):

    with caplog.at_level(logging.INFO):
        resposta = RespostaBase(
            id="1",
            pergunta="Qual a melhor marca?",
            plataforma="ChatGPT",
            modelo="gpt-4",
            resposta_texto="Acme é uma opção",
            data_hora="2025-01-01T10:00:00"
        )
    print(caplog.text)
    assert resposta.id == "1"
    assert "criada com sucesso" in caplog.text

def test_converter_data_para_datetime(caplog):

    with caplog.at_level(logging.DEBUG, logger="src.modelo_json"):
        resposta = RespostaBase(
            id="1",
            pergunta="Pergunta",
            plataforma="ChatGPT",
            modelo="gpt-4",
            resposta_texto="Texto",
            data_hora="2025-01-01T10:00:00"
        )

    assert isinstance(resposta.data_hora, datetime)
    assert "convertido para datetime" in caplog.text


def test_sentimento_opcional(caplog):

    with caplog.at_level(logging.DEBUG, logger="src.modelo_json"):

        resposta = RespostaBase(
            id="1",
            pergunta="Pergunta",
            plataforma="ChatGPT",
            modelo="gpt-4",
            resposta_texto="Texto",
            data_hora="2025-01-01T10:00:00"
        )

        assert resposta.sentimento is None
        assert "sentimento não informado" in caplog.text


def test_deve_falhar_sem_campos_obrigatorios(caplog):

    with pytest.raises(ValidationError):
        RespostaBase(
            id="1"
        )

    logger.warning(
        "ValidationError capturada para campos obrigatórios ausentes"
    )

    assert "ValidationError capturada" in caplog.text


def test_valores_padrao_resposta_processada():

    resposta = RespostaProcessada(
        id="1",
        pergunta="Pergunta",
        plataforma="ChatGPT",
        modelo="gpt-4",
        resposta_texto="Texto",
        data_hora="2025-01-01T10:00:00"
    )

    assert resposta.marcas_mencionadas == []
    assert resposta.score_citacao == 0


def test_carregar_arquivo_real_valido():

    caminho = Path(__file__).parent / "data" / "respostas_validas.json"

    respostas = ServicoIngestao.carregar_arquivo(str(caminho))

    assert len(respostas) > 0
    assert all(isinstance(resposta, RespostaBase) for resposta in respostas)

def test_carregar_arquivo_real_sujo(caplog):

    caminho = Path(__file__).parent / "data" / "respostas_sujas.json"

    with caplog.at_level(logging.WARNING, logger="src.ingestao"):
        respostas = ServicoIngestao.carregar_arquivo(str(caminho))

    assert len(respostas) > 0
    assert "Registro inválido ignorado" in caplog.text