# Serviço de menções de marcas em respostas IA

Este repositório documenta a criação de um serviço de ingestão de dados por arquivo JSON através de API para monitorar menções a marcas monitoradas ("Acme", "Zenith" e "Nimbus")

## Resumo

Aplicação em Python que utiliza o **framework FastAPI + armazenamento em SQLAlchemy** para armazenar respostas de webscraping, detectando menções a marcas.

## Passo a passo

            respostas.json
                ↓
            ingestão
                ↓
            detecção de marcas
                ↓
            análise
                ↓
            armazenamento
                ↓
            script de orquestração main.py

##### Planejamento do projeto
- **Passo inicial**: análise do contexto fornecido e delimitar os principais entregáveis e funcionalidades do projeto.
- **Funcionalidades**: ingestão de dados via API, detecção de menções, armazenamento dos dados coletados
- **Entregas**: repositório GitHub com README curto explicando as decisões, projeto modular no framework que eu escolher, testes considerados necessários e ideias de aprimoramento no futuro. Precisa constar as dependências em requirements.txt ou pyproject.toml
    
##### Escolha de modelo de fluxo de trabalho
- Eu iria optar por um modelo padrão de aplicações em ambiente de produção, constando uma branch "main", "development", "feat/nome-do-feature", "test/nome-do-teste", mas através do uso de IA generativa + pesquisa em buscadores, me foi apresentado o modelo [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow), que utiliza apenas uma branch "main" e uma branch "develop/nome-do-feature", ideal para testes práticos e enxutos como esse.

    ![gitflow](/assets/img/gitflow.png)

- Optei por não deletar as branches /develop/. para ficar mais fácil de avaliar as alterações como um todo.

- Criei a branch "main", o README.md para registrar o processo de criação do serviço, um arquivo requirements.txt para dependências (pyproject.toml seria mais moderno, mas a prática que tenho é com o requirements.txt), o .gitignore para limitar o que é posto no repositório (a princípio, coloquei lá o que é mais recorrente nos meus projetos). Criei um arquivo de checklists como log de acompanhamento pessoal. Também criei a estrutura de pastas inicial

### Escolha de framework:
> Fast API + SQLAlchemy

##### Java considerado inicialmente
- A princípio, o framework seria escolhido pensando no produto da PiniOn que mais se adequa ao serviço descrito: o v-tracker. A princípio, o produto foi mencionado brevemente na entrevista e lembro vagamente de ter sido dito que o v-tracker era baseado em Java.

##### Python foi um caminho melhor para seguir
- No entanto, utilizei IAs para verificar quais seriam as possibilidades de criar essa integração com Java. Elas apontaram para o risco de utilizar uma linguagem que não tenho tanta facilidade, apontando também para o uso padrão de Python (que tenho mais familidade) para webscrapping.  Além disso, a recomendação do arquivo de dependências em requirements.txt ou pyproject.toml apontaram para a adoção de Python no framework.
- Por ser um microsserviço desacoplado com dados em JSON, faz sentido que possam haver múltiplas ferramentas em uma mesma aplicação e posteriormente possa ser feita a integração.

##### Django, Flask ou FastAPI?
- Fiquei entre o Django, Flask e FastAPI, serviços populares de desenvolvimento com APIs. Dentro dos prós e contras dos três, escolhi seguir com o **FastAPI**, que é rápido, seguro e aplicável a projetos simples, pois o Flask me pareceu ser menos robusto em questão de segurança e rapidez e o Django parecia ser seguro mas não ter suporte a projetos tão simples nem ser tão rápido.

##### Validação do código:
- Seguindo a sugestão de tempo do desafio, eu decidi utilizar a seguinte estratégia: explicando o contexto do desafio para a IA generativa, criei o código através de prompt para voltar revisando validando cada camada em uma branch separada.

As branchs são:
1. develop/ingestao-de-mencoes (testa modelo_json.py e ingestao.py)
2. develop/deteccao-de-mencoes (testa deteccao-de-mencoes.py)
3. develop/armazenamento (testa armazenamento.py)
4. develop/main-script (testa o script de orquestração main.py)
5. develop/integracao (testa se o fluxo da aplicação funciona)

-  Nessa etapa, adicionei docstrings em cada classe definida e suprimi código sobressalente/que seria depreciado. Fui fazendo também os testes unitários com a biblioteca pytest.

##### Persistência

- O armazenamento das respostas foi feito em um banco SQLAlchemy, escolhido por ser facilmente integrado com PostgreSQL, que lembro de ser banco utilizado pela PiniOn. A integração pode ser feita com lgumas pequenas mudanças e uso do Alembic (um toolkit de migração de bases SQLAlchemy).

- Apesar de os constraints de nulidade já estarem feitos na fase de leitura e ingestão do JSON, ainda coloquei um constraint de quais campos aceitam nulos ou não. Não limitei quantidade de caracteres por ainda desconhecer qual vai ser a necessidade do projeto, em média.

- O campo "id" como chave primária já evita duplicidades de identificação

- O banco transforma tudo em texto e garante sua resistência contra injeções de SQL 

- Coloquei a coluna de "marcas mencionadas" como JSON pra dar suporte a listas de tamanho flexível.


### Estrutura de pastas

    servico-mencao-marcas/
    ├── assets/             # Recursos extras de documentação
    │   ├── imgs            # Pasta para imagens
    │   └── docs            # Documentos extras
    ├── src/                # Scripts da aplicação
    │   ├── __init__.py
    │   ├── deteccao_mencoes.py
    │   ├── ingestao.py        
    │   ├── main.py            
    │   └── modelo_json.py
    ├── tests/              # Scripts de teste 
    │   ├── data/           # Arquivos sintéticos para validação
    │   │  ├── respostas_validas.json
    │   │  └── respostas_sujas.json
    │   ├── __init__.py
    │   ├── test_modelo_json.py
    │   └── test_ingestao.py
    ├── README.md           # Arquivo principal de documentação
    ├── .gitignore
    └── requirements.txt


## Desafios e aprendizados

- Esqueci a boa prática do "git pull" depois de criar sincronizar o repositório remoto. Tive que usar o "git push --force-with-lease", com cautela, no primeiro commit.
- Ao fazer a validação, revisei e documentei o código, pesquisando o que não entendi e suprimindo o que não era funcional. Por exemplo, a IA sugeriu usar o módulo typing para importar List e Optional, mas vi que esses módulos serão depreciados. (A linha "Optional[str] = None" virou "sentimento: str | None = None"). Fui corrigindo o arquivo "requirement.txt" enquanto suprimia código.
- O processo de ingestão só aceita dados estritamente dentro dos parâmetros, ignorando erros. Preciso considerar como tratar esses erros.
- Não sou proficiente em fazer testes de APU com a biblioteca pytest. Tive dificuldade em pedir a implementação de testes com logs na IA, então eu...
>usei a mesma lógica de testes que faria "manualmente" na biblioteca pandas para verificar se dataframes estão limpos (ou seja, verifiquei se repostas íntegras passavam, se havia duplicatas, se os contraints de tipos estavam funcionando etc).
- Demorei *bastante* tempo tentando fazer melhorias incrementais a partir do troubleshooting do teste. Estou focando em **o quê** testar e não exatamente como os testes funcionam.
- Para amenizar isso, criei arquivos gerados por IA que simulam uma quatidade maior de dicionários json, chamados "respostas_sujas.json" e "respostas_validas.json", para além dos testes dentro do próprio arquivo. Isso me deu um parâmetro de que o código conseguiria ingerir um formato maior de erros.

## O que eu faria diferente se tivesse mais tempo
- Estudaria mais a biblioteca pytest e logging para verificar como lançar erros e exceções de forma mais criteriosa e consciente.
    - Não documentei tão bem os testes por conta disso: não achei que valia o custo-benefício de tempo para a entrega e foquei em colocar isso como ponto de observação para melhorar para a próxima
- O serviço não conta com validação de tokens. Acredito que isso pudesse trazer um nível extra de segurança.
- Utilizaria fuzzy matching para automatizar a detecção de empresas com erros de digitação de forma automatizada, mas estou optando por reduzir a quantidade de dependências e principalmente por evitar incluir uma lógica de código que eu não consiga explicar bem e saber quais implicações isso tem no resto do código, até porque não saberia o que testar.
