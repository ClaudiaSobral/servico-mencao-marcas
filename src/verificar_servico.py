"""Script de verificação manual (smoke test) do serviço.

Diferente dos testes automatizados em tests/ (que rodam com banco em
memória, isolados via pytest), este script fala com o servidor de
verdade, rodando de pé, com o banco real (SQLite em arquivo). É a
prova de que "o serviço funciona" para quem está avaliando o
desafio: basta subir a API e rodar este arquivo.

Como usar:
    1. Em um terminal, suba a API:
         uvicorn src.main:app --reload
    2. Em outro terminal, rode este script:
         python scripts/verificar_servico.py

O script não usa pytest de propósito — é pensado para ser lido e
rodado por alguém avaliando o projeto, sem precisar conhecer a suíte
de testes.
"""

import sys

import httpx

BASE_URL = "http://127.0.0.1:8000"

RESPOSTAS_DE_EXEMPLO = [
    {
        "id": "smoke-forte-acme",
        "pergunta": "Qual ferramenta de dados vocês recomendam?",
        "plataforma": "ChatGPT",
        "modelo": "gpt-4",
        "resposta_texto": "A Acme é a melhor escolha do mercado, recomendo sem dúvida.",
        "data_hora": "2026-01-01T10:00:00",
        "sentimento": "positivo",
    },
    {
        "id": "smoke-fraca-zenith",
        "pergunta": "O que vocês usaram no projeto?",
        "plataforma": "Gemini",
        "modelo": "gemini-1.5",
        "resposta_texto": "Testamos várias ferramentas e, entre outras, usamos a Zenith uma vez.",
        "data_hora": "2026-01-01T11:00:00",
        # sentimento chega como string "null" de propósito, para provar
        # que a normalização de nulos do scraping está funcionando.
        "sentimento": "null",
    },
    {
        "id": "smoke-sem-marca",
        "pergunta": "Como está o tempo hoje?",
        "plataforma": "ChatGPT",
        "modelo": "gpt-4",
        "resposta_texto": "Não tenho acesso a informações de clima em tempo real.",
        "data_hora": "2026-01-01T12:00:00",
        "sentimento": None,
    },
]

falhas = []


def checar(descricao, condicao):
    if condicao:
        print(f"✅ {descricao}")
    else:
        print(f"❌ {descricao}")
        falhas.append(descricao)


def main():
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as cliente:
        try:
            cliente.get("/docs")
        except httpx.ConnectError:
            print(
                "Não consegui conectar em"
                f" {BASE_URL}. Suba a API primeiro com:\n"
                "    uvicorn src.main:app --reload"
            )
            sys.exit(1)

        # 1. Ingestão: cada resposta de exemplo precisa ser aceita
        for resposta in RESPOSTAS_DE_EXEMPLO:
            r = cliente.post("/respostas", json=resposta)
            checar(
                f"POST /respostas aceita '{resposta['id']}'",
                r.status_code == 200,
            )

        # 2. Idempotência: reenviar o mesmo id não deve gerar erro
        r = cliente.post("/respostas", json=RESPOSTAS_DE_EXEMPLO[0])
        checar("POST /respostas é idempotente para id repetido", r.status_code == 200)

        # 3. Share of Voice: Acme aparece em 1 das 3 respostas
        r = cliente.get("/share-of-voice", params={"marca": "Acme"})
        corpo = r.json() if r.status_code == 200 else {}
        checar("GET /share-of-voice responde 200", r.status_code == 200)
        checar(
            "GET /share-of-voice calcula o percentual esperado (~33.3%)",
            corpo.get("mencoes") == 1 and 33.0 <= corpo.get("share_of_voice", 0) <= 34.0,
        )
        checar(
            "GET /share-of-voice traz quebra por plataforma",
            "por_plataforma" in corpo and "ChatGPT" in corpo.get("por_plataforma", {}),
        )

        # 4. Top citações: a resposta com contexto de recomendação vem primeiro
        r = cliente.get("/top-citacoes", params={"n": 3})
        resultados = r.json() if r.status_code == 200 else []
        checar("GET /top-citacoes responde 200", r.status_code == 200)
        checar(
            "GET /top-citacoes ordena a citação mais forte primeiro",
            bool(resultados) and resultados[0]["id"] == "smoke-forte-acme",
        )

        # 5. Normalização de sentimento nulo do scraping
        mencao_zenith = next(
            (item for item in resultados if item["id"] == "smoke-fraca-zenith"), None
        )
        checar(
            "sentimento 'null' (string) foi normalizado para None",
            mencao_zenith is not None and mencao_zenith.get("sentimento") is None,
        )

        # 6. Validação de entrada continua ativa
        r = cliente.post("/respostas", json={"id": "smoke-invalido"})
        checar("POST /respostas rejeita payload incompleto (422)", r.status_code == 422)

    print()
    if falhas:
        print(f"{len(falhas)} verificação(ões) falharam:")
        for f in falhas:
            print(f"  - {f}")
        sys.exit(1)

    print("Todas as verificações passaram. Serviço funcionando de ponta a ponta.")


if __name__ == "__main__":
    main()