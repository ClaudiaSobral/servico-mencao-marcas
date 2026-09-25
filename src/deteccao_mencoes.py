import re

'''Lista de padrões para detecção. Os limites \b garantem que a marca seja identificada
como uma palavra isolada, evitando correspondências dentro de outras palavras.
'''

MARCAS_MONITORADAS = {
    'Acme': [r'\bacme\b', r'\bac[mn]e\b', r'\bakme\b'],
    'Zenith': [r'\bzenith\b', r'\bzenit[h]?\b', r'\bzenite\b'],
    'Nimbus': [r'\bnimbus\b', r'\bnimbos\b', r'\bnimbu[cs]\b'],
}


class DetectorMencoes:
    """Responsável por identificar marcas monitoradas em um texto."""

    @staticmethod
    def detectar(texto: str) -> tuple[list[str], int]:
        """
        Args:
            texto: Conteúdo textual que será analisado.

        Returns:
            tuple[list[str], int]:
                - Lista de marcas identificadas no texto.
                - Score bruto correspondente ao total de ocorrências.
        """

        texto = texto.lower()

        marcas = []
        score = 0

        for marca, padroes in MARCAS_MONITORADAS.items():
            padrao_combinado = "|".join(padroes)
            ocorrencias = len(re.findall(padrao_combinado, texto))

            if ocorrencias > 0:
                marcas.append(marca)
                score += ocorrencias

        return marcas, score