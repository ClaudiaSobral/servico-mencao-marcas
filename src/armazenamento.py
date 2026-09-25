from sqlalchemy import (                                  # Importa as estruturas de tipos da base
    Column,
    DateTime,
    Float,
    JSON,
    String,
    Text,
    create_engine)                          
from sqlalchemy.orm import declarative_base, sessionmaker # Mapeia classes Python e importa parâmetros do módulo de armazenamento
import os                                                 # Permite fazer a portabilidade do banco de dados  

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///mencoes.db"
)

engine = create_engine(DATABASE_URL)                      # Cria conexão usando o DATABASE_URL
SessionLocal = sessionmaker(bind=engine)                  # Permite interagir com o banco

Base = declarative_base()                                 # Permite manipular o banco como uma classe Python    

class RespostaDB(Base):                                   # Inicializa estrutura da tabela
    """Representa uma resposta analisada e seus resultados no banco."""

    __tablename__ = 'respostas'

    id = Column(String, primary_key=True)                       # Chave primária
    pergunta = Column(Text, nullable=False)
    plataforma = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    resposta_texto = Column(Text, nullable=False)
    data_hora = Column(DateTime(timezone=True), nullable=False) # Aramazena dara e hora com suporte a fuso
    sentimento = Column(String, nullable=True)                  # Sentimento pode ser nulo
    marcas_mencionadas = Column(JSON, nullable=False)           # Utiliza JSON para manter uma estrutura com suporte a listas
    score_citacao = Column(Float, nullable=False, default=0)  # Usa 0 quando o score não for informado

def criar_tabelas():
    """Cria as tabelas do banco definidas pelos modelos ORM."""                                        
    Base.metadata.create_all(bind=engine)

def salvar_resposta(session, dados):
    """Salva uma resposta no banco de forma idempotente.

    Se já existir uma resposta com o mesmo ID, o registro existente
    é retornado e nenhuma nova linha é inserida.

    Args:
        session: Sessão ativa do SQLAlchemy.
        dados: Dicionário contendo os dados da resposta.

    Returns:
        Objeto RespostaDB correspondente ao registro salvo ou
        previamente existente.
    """
    existente = session.get(RespostaDB, dados["id"])

    if existente:
        return existente

    resposta = RespostaDB(**dados)

    session.add(resposta)
    session.commit()

    return resposta