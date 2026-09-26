![git_hub_project_mencao](/assets/img/git_hub_project_mencao.png)

# Serviço de menções de marcas em respostas IA

Este repositório documenta a criação de um serviço de ingestão de dados por arquivo JSON através de API para monitorar menções a marcas monitoradas ("Acme", "Zenith" e "Nimbus")

## 1. Resumo

Aplicação em Python que utiliza o **framework FastAPI + armazenamento em SQLite usando SQLAlchemy** para armazenar respostas de webscraping, detectando menções a marcas.

### Framework escolhido

> Fast API + SQLAlchemy & SQLite

### Bibliotecas principais
```fastapi``` ```sqlalchemy``` ```pytest``` ```uvicorn.```

## 2. Estrutura de pastas

A seguinte estrutura de pastas foi utilizada por ser um modelo modularizável e fácil de trabalhar em um framework de Git. Também é o padrão que tenho usado e que observo meus pares utilizando.
Vale ressaltar que em todo momento são utilizados arquivos .json sintéticos para teste. Caso fossem dados reais do cliente, não estariam versionados.

    servico-mencao-marcas/
    ├── assets/                     # Recursos extras de documentação
    │   ├── imgs                    # Pasta para imagens
    │   └── docs                    # Documentos extras
    ├── src/                        # Scripts da aplicação
    │   ├── __init__.py
    │   ├── armazenamento.py
    │   ├── deteccao_mencoes.py
    │   ├── ingestao.py        
    │   ├── main.py            
    │   ├── modelo_json.py            
    │   └── verificar_servico.py
    ├── tests/                          # Scripts de teste 
    │   ├── data/                       # Arquivos sintéticos para validação
    │   │  ├── respostas_validas.json
    │   │  └── respostas_sujas.json
    │   ├── __init__.py
    │   ├── test_armazenamento.py
    │   ├── test_deteccao_mencoes.py
    │   ├── test_ingestao.py
    │   ├── test_integracao.py
    │   ├── test_main.py
    │   └── test_modelo_json.py
    ├── README.md                   # Arquivo principal de documentação
    ├── ENTREGA.md                  # README resumido apenas com os entregáveis
    ├── .gitignore
    └── requirements.txt

## 3. A "força" da menção

                        Força da menção
                            │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        Frequência      Contexto       Posição
                │              │              │
                └──────────────┼──────────────┘
                            ▼
                        Exclusividade
                            │
                            ▼
                        + Sentimento
                            │
                            ▼
                        Score final

A `score_citacao` é uma métrica que busca representar a força de uma menção de marca na resposta. O cálculo combina a **frequência de ocorrência da marca**, a presença de **termos associados a recomendações**, a **posição da primeira menção**, a **quantidade de marcas concorrentes citadas** e o **sentimento** da resposta. A frequência utiliza uma espécie de média ponderada para aumentar o score para menções positivas e reduzindo-o para menções negativas. Atualmente, o score é calculado para a **primeira marca detectada na resposta** através da seleção do index 0 em ```marca=marcas[0]``` no arquivo ```deteccao_mencoes.py```, o que é uma limitação da atual implementação.


## 4. Desafios e aprendizados
> O maior desafio foi sem dúvidas a validação e a implementação de "força" da menção

- Esqueci a boa prática do "git pull" depois de criar sincronizar o repositório remoto. Tive que usar o **"git push --force-with-lease"**, com cautela, no primeiro commit.
- Ao fazer a validação, revisei e documentei o código, **pesquisando o que não entendi e suprimindo o que não era funcional**. Por exemplo, a IA sugeriu usar o módulo typing para importar List e Optional, mas vi que esses módulos serão depreciados. (A linha "Optional[str] = None" virou "sentimento: str | None = None"). Fui corrigindo o arquivo "requirement.txt" enquanto suprimia código.
- Não sou proficiente em fazer testes de validação de API. A validação que costumo fazer é dentro dos bancos de dados. Tive dificuldade em pedir a implementação de testes com logs na IA, então eu...
>usei a mesma lógica de testes que faria "manualmente" na com pandas ou SQL para verificar se uma base está limpa (ou seja, verifiquei se repostas íntegras passavam, se havia duplicatas, se os contraints de tipos estavam funcionando etc).
- Demorei *bastante* tempo tentando fazer melhorias incrementais com IA generativa a partir do troubleshooting do teste. Foquei em **o quê** testar e não exatamente como os testes funcionam.
- Para amenizar isso, criei arquivos gerados por IA que simulam uma quatidade maior de dicionários json, chamados "respostas_sujas.json" e "respostas_validas.json", para além dos testes dentro do próprio arquivo. Isso me deu um parâmetro de que o código conseguiria ingerir um formato maior de erros no momento de ingestão, que é crucial para o framework.
- Inicialmente, eu considerei "força" da menção como uma contagem simples de palavras, mas percebi ao longo do desafio que uma contagem não fornece o contexto necessário. Tentei aplicar uma média ponderada que fosse mais justa com o contexto. Foi um grande desafio e eu gostaria de estudar melhor como fazer isso, talvez com NLP, mas avaliaria rotas fora de um ML antes.

## 5. O que eu faria diferente se tivesse mais tempo

### Testes mais criteriosos 
- Estudaria mais a biblioteca pytest e logging para verificar **como lançar erros e exceções** de forma mais criteriosa e consciente.
    - Não documentei tão bem os testes por conta disso: não achei que valia o custo-benefício de tempo para a entrega e foquei em colocar isso como ponto de observação para melhorar para a próxima entrega

### Segurança e LGPD
- Consegui validar a segurança contra injeções SQL ao tipar todo o conteúdo que vai pras bases como string. No entanto, o serviço não conta com validação de tokens por API key. Acredito que isso pudesse trazer um nível extra de segurança.
- Além disso, em contexto de desenvolvimento, seria **imprescindível** criar **mecanismos de segurança para não vazar dados PII que violassem a LGPD** no processo de ingestão das respostas (o que não está implementado).

### Refino dos algoritmos e do System Design
- Utilizaria fuzzy matching para automatizar a detecção de empresas com erros de digitação de forma automatizada, mas estou optando por reduzir a quantidade de dependências e principalmente por evitar incluir uma lógica de código que **eu não consiga saber quais implicações** isso tem no resto do código nem via teste.
- Também consideraria um modelo de machine learning NLP para avaliar os sentimentos.
- Como o input do teste foi vago especificações de negócio, utilizei as informações disponíveis para um System Design versátil dentro do que já me foi apresentado pela empresa, mas não pude considerar as ferramentas exatas, o que resultaria em decisões mais criteriosas em termos de latência, ferramentas de autenticação, custo computacional e e o framework num geral.

### Testes extras, escalabilidade, integração e comentários
- Faria testes extras de carga de requisições, de limite de payload e vazamento de memória. Provavelmente integraria o serviço de menção a uma fila que armazenasse requisições em momentos de pico, até poder distribuit essa task.
- Indo para um contexto de equipe, eu criaria uma imagem Docker do projeto (a depender de com que ferramentas a equipe trabalha)
- O projeto foi pensado como IaC (Infraestrutura como Código), mas caso o direcionamento fosse implementá-lo para leitura de agentes IA, seria necessário documentar melhor o código para que menos tokens fossem gastos pela melhoria da compreensão do código pela IA.
