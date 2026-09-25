from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

class RespostaBase(BaseModel):
    id: str
    pergunta: str
    plataforma: str
    modelo: str
    resposta_texto: str
    data_hora: datetime
    sentimento: Optional[str] = None

class RespostaProcessada(RespostaBase):
    marcas_mencionadas: List[str] = Field(default_factory=list)
    score_citacao: int = 0
