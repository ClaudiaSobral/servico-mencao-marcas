import re
from typing import List

MARCAS_MONITORADAS = {
    'Acme': [r'acme'],
    'Zenith': [r'zenith'],
    'Nimbus': [r'nimbus']
}

class DetectorMencoes:

    @staticmethod
    def detectar(texto: str) -> tuple[list[str], int]:
        texto = texto.lower()

        marcas = []
        score = 0

        for marca, padroes in MARCAS_MONITORADAS.items():
            for padrao in padroes:
                ocorrencias = len(re.findall(padrao, texto, re.IGNORECASE))

                if ocorrencias > 0:
                    marcas.append(marca)
                    score += ocorrencias
                    break

        return marcas, score
