import json
import logging

from src.ingestao import ServicoIngestao

logger = logging.getLogger(__name__)

def test_carregar_arquivo_valido(tmp_path, caplog):

    dados = [
        {
            "id": "1",
            "pergunta": "Pergunta",
            "plataforma": "ChatGPT",
            "modelo": "gpt-4",
            "resposta_texto": "Acme",
            "data_hora": "2025-01-01T10:00:00"
        }
    ]

    arquivo = tmp_path / "respostas.json"

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f)

    respostas = ServicoIngestao.carregar_arquivo(str(arquivo))

    assert len(respostas) == 1


def test_ignorar_registro_invalido(tmp_path, caplog):

    dados = [
        {
            "id": "1",
            "pergunta": "Pergunta",
            "plataforma": "ChatGPT",
            "modelo": "gpt-4",
            "resposta_texto": "Acme",
            "data_hora": "2025-01-01T10:00:00"
        },
        {
            "id": "2"
        }
    ]

    arquivo = tmp_path / "respostas.json"

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f)

    with caplog.at_level(logging.WARNING):
        respostas = ServicoIngestao.carregar_arquivo(str(arquivo))

    assert len(respostas) == 1
    assert "Registro inválido ignorado" in caplog.text



def test_json_vazio(tmp_path, caplog):

    arquivo = tmp_path / "respostas.json"

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump([], f)

    respostas = ServicoIngestao.carregar_arquivo(str(arquivo))

    assert respostas == []

def test_carregar_apenas_registros_validos(tmp_path, caplog):

    dados = [
        {
            "id": "1",
            "pergunta": "Pergunta",
            "plataforma": "ChatGPT",
            "modelo": "gpt-4",
            "resposta_texto": "Acme",
            "data_hora": "2025-01-01T10:00:00"
        },
        {},
        {
            "id": "2"
        },
        {
            "id": "3",
            "pergunta": "Pergunta",
            "plataforma": "Gemini",
            "modelo": "gemini",
            "resposta_texto": "Zenith",
            "data_hora": "2025-01-02T10:00:00"
        }
    ]

    arquivo = tmp_path / "respostas.json"

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f)

    respostas = ServicoIngestao.carregar_arquivo(str(arquivo))

    assert len(respostas) == 2