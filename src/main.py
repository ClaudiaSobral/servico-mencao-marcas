from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.armazenamento import SessionLocal, criar_tabelas, RespostaDB
from src.deteccao_mencoes import DetectorMencoes
from src.modelo_json import RespostaBase

app = FastAPI(title='Servico de Analise de Mencoes')

criar_tabelas()

@app.post('/respostas')
def adicionar_resposta(resposta: RespostaBase):
    db: Session = SessionLocal()

    marcas, score = DetectorMencoes.detectar(resposta.resposta_texto)

    registro = RespostaDB(
        **resposta.model_dump(),
        marcas_mencionadas=','.join(marcas),
        score_citacao=score
    )

    db.add(registro)
    db.commit()

    return {'status': 'sucesso'}

@app.get('/share-of-voice')
def share_of_voice(marca: str):
    db: Session = SessionLocal()

    respostas = db.query(RespostaDB).all()

    total = len(respostas)

    if total == 0:
        raise HTTPException(status_code=404, detail='Sem dados')

    mencoes = [
        r for r in respostas
        if marca.lower() in (r.marcas_mencionadas or '').lower()
    ]

    return {
        'marca': marca,
        'total_respostas': total,
        'mencoes': len(mencoes),
        'share_of_voice': round(len(mencoes) / total * 100, 2)
    }

@app.get('/top-citacoes')
def top_citacoes(n: int = 5):
    db: Session = SessionLocal()

    resultados = (
        db.query(RespostaDB)
        .order_by(RespostaDB.score_citacao.desc())
        .limit(n)
        .all()
    )

    return resultados
