import pytest
from src.deteccao_mencoes import DetectorMencoes


class TestDeteccaoBasica:
    """Cobre o caminho principal: marca presente, ausente, e repetida."""

    def test_detecta_marca_unica(self):
        marcas, score = DetectorMencoes.detectar("A Acme lançou um produto novo.")
        assert marcas == ["Acme"]
        assert score == 1

    def test_case_insensitive(self):
        # Mesma marca em três grafias de caixa diferentes no mesmo texto
        marcas, score = DetectorMencoes.detectar("acme, ACME e AcMe são a mesma empresa")
        assert marcas == ["Acme"]
        assert score == 3  # conta cada ocorrência, mas marca aparece 1x na lista

    def test_texto_sem_marca_retorna_vazio(self):
        marcas, score = DetectorMencoes.detectar("Hoje o tempo está bom.")
        assert marcas == []
        assert score == 0

    def test_texto_vazio(self):
        marcas, score = DetectorMencoes.detectar("")
        assert marcas == []
        assert score == 0


class TestVariacoesETypos:
    """Cobre os padrões alternativos definidos em MARCAS_MONITORADAS.

    Cada teste aqui documenta explicitamente qual variação está coberta —
    útil para o README, como registro de que erro de digitação foi previsto.
    """

    @pytest.mark.parametrize("texto,marca_esperada", [
        ("A Acne é referência no setor", "Acme"),      # troca m -> n
        ("Muita gente escreve Zenit sem o h", "Zenith"),  # sem o h final
        ("O produto da Nimbos é bom", "Nimbus"),        # variação de vogal
    ])
    def test_variacao_conhecida_e_detectada(self, texto, marca_esperada):
        marcas, score = DetectorMencoes.detectar(texto)
        assert marca_esperada in marcas
        assert score == 1

    def test_typo_fora_do_padrao_nao_e_detectado(self):
        # Documenta o limite conhecido da abordagem por regex fixo:
        # typos não previstos não são cobertos (trade-off vs. fuzzy matching)
        marcas, score = DetectorMencoes.detectar("A empresa Acm3 lançou algo")
        assert marcas == []
        assert score == 0


class TestMultiplasMarcas:
    """Cobre respostas que citam mais de uma marca monitorada."""

    def test_duas_marcas_no_mesmo_texto(self):
        texto = "Comparando Acme e Zenith, prefiro a Acme."
        marcas, score = DetectorMencoes.detectar(texto)
        assert set(marcas) == {"Acme", "Zenith"}
        assert score == 3  # Acme aparece 2x + Zenith 1x

    def test_todas_as_marcas_monitoradas_no_mesmo_texto(self):
        texto = "Acme, Zenith e Nimbus são concorrentes diretos."
        marcas, score = DetectorMencoes.detectar(texto)
        assert set(marcas) == {"Acme", "Zenith", "Nimbus"}
        assert score == 3

    def test_score_soma_ocorrencias_de_multiplas_marcas(self):
        # O score representa o total de ocorrências das marcas detectadas.
        # aparecem no dicionário MARCAS_MONITORADAS
        texto = "Nimbus é ótima, Nimbus é ótima, Acme também."
        marcas, score = DetectorMencoes.detectar(texto)
        assert set(marcas) == {"Nimbus", "Acme"}
        assert score == 3

    def test_mesma_marca_em_variacoes_diferentes(self):
        texto = "Acme, Acne e AKME são empresas conhecidas."

        marcas, score = DetectorMencoes.detectar(texto)

        assert marcas == ["Acme"]
        assert score == 3

    def test_nao_detecta_marca_dentro_de_palavra(self):
        marcas, score = DetectorMencoes.detectar(
            "O termo acmecorp não representa uma menção à marca."
        )

        assert marcas == []
        assert score == 0