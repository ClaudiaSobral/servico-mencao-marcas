![git_hub_project_mencao](/assets/img/git_hub_project_mencao.png)

# Serviço de menções de marcas em respostas IA

Este repositório documenta a criação de um serviço de ingestão de dados por arquivo JSON através de API para monitorar menções a marcas monitoradas ("Acme", "Zenith" e "Nimbus")

❗OBSERVAÇÃO❗ Nesse README constam decisões arquiteturais e explicações a fundo do processo. Para o README resumido apenas com os entregáveis, prossiga para [README_resumido.md](https://github.com/ClaudiaSobral/servico-mencao-marcas/blob/main/README_resumido.md)


## 1. Resumo

Aplicação em Python que utiliza o **framework FastAPI + armazenamento em SQLite usando SQLAlchemy** para armazenar respostas de webscraping, detectando menções a marcas.

![git_hub_project_framework](/assets/img/git_hub_mencao_framework.png)

### Framework escolhido
> Fast API + SQLAlchemy & SQLite

### Bibliotecas principais
```fastapi``` ```sqlalchemy``` ```pytest``` ```uvicorn.```

### Estrutura de pastas

A seguinte estrutura de pastas foi utilizada por ser um modelo modularizável e fácil de trabalhar em um framework de Git. Também é o padrão que tenho usado e que observo meus pares utilizando.
Vale ressaltar que em todo momento são utilizados arquivos .json sintéticos para teste. Caso fossem dados reais do cliente, não estariam versionados.


    servico-mencao-marcas/
    ├── assets/             # Recursos extras de documentação
    │   ├── imgs            # Pasta para imagens
    │   └── docs            # Documentos extras
    ├── src/                # Scripts da aplicação
    │   ├── __init__.py
    │   ├── armazenamento.py
    │   ├── deteccao_mencoes.py
    │   ├── ingestao.py        
    │   ├── main.py            
    │   └── modelo_json.py
    ├── tests/              # Scripts de teste 
    │   ├── data/           # Arquivos sintéticos para validação
    │   │  ├── respostas_validas.json
    │   │  └── respostas_sujas.json
    │   ├── __init__.py
    │   ├── test_armazenamento.py
    │   ├── test_deteccao_mencoes.py
    │   ├── test_ingestao.py
    │   ├── test_integracao.py
    │   ├── main.py
    │   └── test_modelo_json.py
    ├── README.md           # Arquivo principal de documentação
    ├── .gitignore
    └── requirements.txt



## 2.  Passo a passo

        respostas.json
            │
            ▼
        POST /respostas
            │
            ├── Pydantic
            │
            ▼
        DetectorMencoes
            │
            ├── marcas
            └── score_citacao
            │
            ▼
        SQLAlchemy
            │
            ▼
        SQLite
            │
            ├──────────────┐
            ▼              ▼
        /share-of-voice   /top-citacoes

### Planejamento do projeto
- **Passo inicial**: análise do contexto fornecido e delimitar os principais entregáveis e funcionalidades do projeto.
- **Funcionalidades**: ingestão de dados via API, detecção de menções, armazenamento dos dados coletados
- **Entregas**: repositório GitHub com README curto explicando as decisões, projeto modular no framework que eu escolher, testes considerados necessários e ideias de aprimoramento no futuro. Precisa constar as dependências em requirements.txt ou pyproject.toml
    
### Escolha de modelo de fluxo de trabalho
- Eu iria optar por um modelo padrão de aplicações em ambiente de produção, constando uma branch "main", "development", "feat/nome-do-feature", "test/nome-do-teste", mas através do uso de IA generativa + pesquisa em buscadores, me foi apresentado o modelo [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow), que utiliza apenas uma branch "main" e uma branch "develop/nome-do-feature", ideal para testes práticos e enxutos como esse.

    ![gitflow](/assets/img/gitflow.png)

- Optei por não deletar as branches /develop/. para ficar mais fácil de avaliar as alterações como um todo.

- Criei a branch "main", o README.md para registrar o processo de criação do serviço, um arquivo requirements.txt para dependências (pyproject.toml seria mais moderno, mas a prática que tenho é com o requirements.txt), o .gitignore para limitar o que é posto no repositório (a princípio, coloquei lá o que é mais recorrente nos meus projetos). Criei um arquivo de checklists como log de acompanhamento pessoal. Também criei a estrutura de pastas inicial

### Java considerado inicialmente
- A princípio, o framework seria escolhido pensando no produto da PiniOn que mais se adequa ao serviço descrito: o v-tracker. A princípio, o produto foi mencionado brevemente na entrevista e lembro vagamente de ter sido dito que o v-tracker era baseado em Java.

### Python foi um caminho melhor para seguir
- No entanto, utilizei IAs para verificar quais seriam as possibilidades de criar essa integração com Java. Elas apontaram para o risco de utilizar uma linguagem que não tenho tanta facilidade, apontando também para o uso padrão de Python (que tenho mais familidade) para webscrapping.  Além disso, a recomendação do arquivo de dependências em requirements.txt ou pyproject.toml apontaram para a adoção de Python no framework.
- Por ser um microsserviço desacoplado com dados em JSON, faz sentido que possam haver múltiplas ferramentas em uma mesma aplicação e posteriormente possa ser feita a integração.

### Django, Flask ou FastAPI?
- Fiquei entre o Django, Flask e FastAPI, serviços populares de desenvolvimento com APIs. Dentro dos prós e contras dos três, escolhi seguir com o **FastAPI**, que é rápido, seguro e aplicável a projetos simples, pois o Flask me pareceu ser menos robusto em questão de segurança e rapidez e o Django parecia ser seguro mas não ter suporte a projetos tão simples nem ser tão rápido.

### Validação do código:
- Seguindo a sugestão de tempo do desafio, eu decidi utilizar a seguinte estratégia: explicando o contexto do desafio para a IA generativa, criei o código através de prompt para voltar revisando validando cada camada em uma branch separada.

As branchs são:
1. develop/ingestao-de-mencoes (testa modelo_json.py e ingestao.py)
2. develop/deteccao-de-mencoes (testa deteccao-de-mencoes.py)
3. develop/armazenamento (testa armazenamento.py)
4. develop/main-script (testa o script de orquestração main.py)
5. develop/integracao (testa se o fluxo da aplicação funciona)
6. develop/fix (faz alguns fixes gerais)

-  Nessa etapa de validação, adicionei docstrings em cada classe definida e suprimi código sobressalente/que seria depreciado. Fui fazendo também os testes unitários com a biblioteca pytest.

## 3. Testes realizados

- O projeto foi testado de duas formas:
    ### pytest
    - De forma extensiva com o uso da biblioteca ````pytest````, validando cada script antes de adicioná-lo ao projeto principal. Ele faz testes unitários para verificar principalmente idempotência, contraints do modelo, segurança contra injeções SQL, etc. Pode ser rodado no terminal executando o seguinte comando:
    
    ```python
    pytest tests/<script-teste>.py -v
    ```
    ### Smoke test
    - Um **smoke test** para avaliação rápida do projeto através de ```src/verificar_servico.py``` :
            Para executá-lo:

            Terminal 1:

            uvicorn src.main:app --reload

            Terminal 2:

            python scripts/verificar_servico.py

    - O smoke test verifica o fluxo completo de ingestão, persistência e consulta, incluindo:

        1. ingestão de respostas pela API;
        2. detecção de marcas;
        3. idempotência;
        4. cálculo de Share of Voice;
        5. ordenação das citações;
        6. normalização de "null" para None;
        7. rejeição de payloads inválidos.


    - Resultado do smoke test funcionando:

                ✅ POST /respostas aceita 'smoke-forte-acme'
                ✅ POST /respostas aceita 'smoke-fraca-zenith'
                ✅ POST /respostas aceita 'smoke-sem-marca'
                ✅ POST /respostas é idempotente para id repetido
                ✅ GET /share-of-voice responde 200
                ✅ GET /share-of-voice calcula o percentual esperado
                ✅ GET /top-citacoes responde 200
                ...
                Todas as verificações passaram.


## 4. Persistência

- O armazenamento das respostas foi feito em um banco SQLite gerado por SQLAlchemy, escolhido por ser facilmente integrado com PostgreSQL, que lembro de ser banco utilizado pela PiniOn. A integração pode ser feita com lgumas pequenas mudanças e uso do Alembic (um toolkit de migração de bases SQLAlchemy).

- Apesar de os constraints de nulidade já estarem feitos na fase de leitura e ingestão do JSON, ainda coloquei um constraint de quais campos aceitam nulos ou não. Não limitei quantidade de caracteres por ainda desconhecer qual vai ser a necessidade do projeto, em média.

- O campo "id" como chave primária já evita duplicidades de identificação

- O banco transforma tudo em texto e garante sua resistência contra injeções de SQL 

- Coloquei a coluna de "marcas mencionadas" como JSON pra dar suporte a listas de tamanho flexível.

## 5. A "força" da menção

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


## 6. Desafios e aprendizados
> O maior desafio foi sem dúvidas a validação e a implementação de "força" da menção
- Esqueci a boa prática do "git pull" depois de criar sincronizar o repositório remoto. Tive que usar o **"git push --force-with-lease"**, com cautela, no primeiro commit.
- Ao fazer a validação, revisei e documentei o código, **pesquisando o que não entendi e suprimindo o que não era funcional**. Por exemplo, a IA sugeriu usar o módulo typing para importar List e Optional, mas vi que esses módulos serão depreciados. (A linha "Optional[str] = None" virou "sentimento: str | None = None"). Fui corrigindo o arquivo "requirement.txt" enquanto suprimia código.
- Não sou proficiente em fazer testes de validação de API. A validação que costumo fazer é dentro dos bancos de dados. Tive dificuldade em pedir a implementação de testes com logs na IA, então eu...
>usei a mesma lógica de testes que faria "manualmente" na com pandas ou SQL para verificar se uma base está limpa (ou seja, verifiquei se repostas íntegras passavam, se havia duplicatas, se os contraints de tipos estavam funcionando etc).
- Demorei *bastante* tempo tentando fazer melhorias incrementais com IA generativa a partir do troubleshooting do teste. Foquei em **o quê** testar e não exatamente como os testes funcionam.
- Para amenizar isso, criei arquivos gerados por IA que simulam uma quatidade maior de dicionários json, chamados "respostas_sujas.json" e "respostas_validas.json", para além dos testes dentro do próprio arquivo. Isso me deu um parâmetro de que o código conseguiria ingerir um formato maior de erros no momento de ingestão, que é crucial para o framework.
- Inicialmente, eu considerei "força" da menção como uma contagem simples de palavras, mas percebi ao longo do desafio que uma contagem não fornece o contexto necessário. Tentei aplicar uma média ponderada que fosse mais justa com o contexto. Foi um grande desafio e eu gostaria de estudar melhor como fazer isso, talvez com NLP, mas avaliaria rotas fora de um ML antes.

## 7. O que eu faria diferente se tivesse mais tempo

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

## 6. Instalação e uso
## Instalação

### Pré-requisitos

* Python 3.11+
* Git
* `pip`

### 1. Clonar o repositório

```bash
git clone https://github.com/ClaudiaSobral/servico-mencao-marcas.git
cd servico-mencao-marcas
```

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

### 4. Iniciar a API

```bash
uvicorn src.main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

A documentação interativa do FastAPI pode ser acessada em:

```text
http://127.0.0.1:8000/docs
```
### 5. Executar os testes

Com as dependências instaladas e o ambiente virtual ativado:

```bash
pytest
```

Os testes automatizados utilizam um banco SQLite em memória, portanto não alteram o banco `mencoes.db` utilizado pela aplicação.

### 6. Executar o smoke test

O projeto também possui um script para verificar o serviço de ponta a ponta.

Primeiro, mantenha a API em execução:

```bash
uvicorn src.main:app --reload
```

Em outro terminal, com o ambiente virtual ativado:

```bash
python scr/verificar_servico.py
```