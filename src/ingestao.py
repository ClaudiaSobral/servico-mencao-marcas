import json                                    # Permite carregamento das respostas em json
import logging

# Imports dos módulos
from src.modelo_json import RespostaBase           # Import do padrão de resposta definido pelo módulo modelo_json

logger = logging.getLogger(__name__)


class ServicoIngestao:
    """Responsável por carregar e validar respostas a partir de um arquivo JSON.

    Trata o fato de que o arquivo de origem vem de scraping automático e pode conter registros malformados.
    """
    @staticmethod
    def carregar_arquivo(caminho: str) -> list[RespostaBase]:
        """Carrega e valida respostas de um arquivo JSON.

        Lê o arquivo indicado, faz o parse do JSON e tenta converter cada
        registro em uma instância de RespostaBase. Registros que não
        atendem ao formato esperado (campo ausente, tipo inválido, data em
        formato inconsistente etc.) são descartados para wue um único registro
        sujo não interrompa a ingestão de todo o arquivo.

        Args:
            caminho: Caminho para o arquivo respostas.json a ser carregado.

        Returns:
            Lista de RespostaBase contendo apenas os registros que
            passaram na validação.

        Raises:
            FileNotFoundError: Se o arquivo indicado em `caminho` não existir.
            json.JSONDecodeError: Se o conteúdo do arquivo não for um JSON
                válido.
        """

        with open(caminho, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        respostas = []

        for registro in dados:
            try:
                respostas.append(RespostaBase(**registro))
            except Exception:
                logger.warning("Registro inválido ignorado")
                continue

        return respostas
