from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = 'sqlite:///mencoes.db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class RespostaDB(Base):
    __tablename__ = 'respostas'

    id = Column(String, primary_key=True)
    pergunta = Column(Text)
    plataforma = Column(String)
    modelo = Column(String)
    resposta_texto = Column(Text)
    data_hora = Column(DateTime)
    sentimento = Column(String, nullable=True)
    marcas_mencionadas = Column(Text)
    score_citacao = Column(Integer)

def criar_tabelas():
    Base.metadata.create_all(bind=engine)
