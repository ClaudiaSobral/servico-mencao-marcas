import json
from typing import List

from modelo_json import RespostaBase

class ServicoIngestao:

    @staticmethod
    def carregar_arquivo(caminho: str) -> List[RespostaBase]:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        respostas = []

        for registro in dados:
            try:
                respostas.append(RespostaBase(**registro))
            except Exception:
                continue

        return respostas
