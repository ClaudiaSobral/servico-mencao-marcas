import logging
from datetime import datetime               # Faz o constraint da data em texto para o tipo datetime
from pydantic import BaseModel, Field, field_validator, model_validator       # BaseModel faz o constraint de tipos e Field delimita o valor padrão

logger = logging.getLogger(__name__)

VALORES_NULOS = {"null", "none", "n/a", "na", "nan", ""}



class RespostaBase(BaseModel): 
    """Faz o constraint de uma resposta da IA para tipos
    específicos seguindo o padrão do .json. Ajuda a validar
    as respostas antes de fazer a detecção das menções.
        Attributes:
            id: identificador único da resposta. (str)
            pergunta: Pergunta feita ao modelo de IA. (str)
            plataforma: Ferramenta de IA generativa que gerou a resposta
                (ex: "ChatGPT", "Gemini", "Perplexity"). (str)
            modelo: Nome/versão do modelo usado (ex: "gpt-4", "gemini-1.5"). (str)
            resposta_texto: Texto completo da resposta, onde é feita a busca
                por menções às marcas monitoradas. (str)
            data_hora: Data e hora em que a resposta foi coletada. (datetime)
            sentimento: Sentimento associado à resposta, se disponível.
                Pode ser None quando não informado pela fonte de dados. (str ou None)
        """
    id: str
    pergunta: str
    plataforma: str
    modelo: str
    resposta_texto: str
    data_hora: datetime
    sentimento: str | None = None

    @field_validator("data_hora", mode="before")
    @classmethod
    def _logar_conversao_data(cls, v):
        logger.debug("Campo data_hora convertido para datetime: %r -> processando", v)
        return v

    @field_validator("sentimento", mode="before")
    @classmethod
    def _normalizar_sentimento_nulo(cls, v):
        """Converte representações textuais de nulo para None."""

        if isinstance(v, str) and v.strip().lower() in VALORES_NULOS:
            return None

        return v


    @model_validator(mode="after")
    def _logar_criacao(self):
        logger.info("RespostaBase criada com sucesso (id=%s)", self.id)
        if self.sentimento is None:
            logger.debug("Campo sentimento não informado para id=%s", self.id)
        return self

class RespostaProcessada(RespostaBase):
    """Processa a resposta após a etapa de detecção de menções.

    Estende RespostaBase adicionando os resultados produzidos pelo módulo
    de detecção: quais marcas monitoradas foram encontradas no texto e
    um score que mede a "força" dessa citação (usado em /top-citacoes).

    Attributes:
        marcas_mencionadas: Lista das marcas monitoradas (ex: "Acme",
            "Zenith", "Nimbus") identificadas em resposta_texto. (lista de strings)
        score_citacao: Valor numérico que representa a força da citação
            nessa resposta. Critério definido no módulo de detecção
            (ex: nº de marcas citadas, posição no texto, repetições). (int)
    """
    marcas_mencionadas: list[str] = Field(default_factory=list)
    score_citacao: int = 0