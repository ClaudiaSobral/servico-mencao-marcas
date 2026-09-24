# Serviço de menções de marcas em respostas IA

Este repositório documenta a criação de um serviço de ingestão de dados por arquivo JSON através de API para monitorar menções a marcas monitoradas ("Acme", "Zenith" e "Nimbus")

## Passo a passo

- **Planejamento do projeto**: o passo inicial foi analisar o contexto fornecido e delimitar os principais entregáveis e funcionalidades do projeto.
    - **Funcionalidades**: ingestão de dados via API, detecção de menções, armazenamento dos dados coletados
    - **Entregas**: repositório GitHub com README curto explicando as decisões, projeto modular no framework que eu escolher, testes considerados necessários e ideias de aprimoramento no futuro. Precisa constar as dependências em requirements.txt ou pyproject.toml
    
- **Escolha de modelo de fluxo de trabalho**: Eu iria optar por um modelo padrão de aplicações em ambiente de produção, constando uma branch "main", "development", "feat/nome-do-feature", "test/nome-do-teste", mas através do uso de IA generativa + pesquisa em buscadores, me foi apresentado o modelo [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow), que utiliza apenas uma branch "main" e uma branch "develop/nome-do-feature", ideal para testes práticos e enxutos como esse.


    ![gitflow](/assets/img/gitflow.png)


    - Criei a branch "main", o README.md para registrar o processo de criação do serviço, um arquivo requirements.txt para dependências, o .gitignore para limitar o que é posto no repositório (a princípio, coloquei lá o que é mais recorrente nos meus projetos). Criei um arquivo de checklists para acompanhamento pessoal. Também criei a estrutura de pastas inicial

### Estrutura de pastas

    servico-mencao-marcas/
    ├── assets/             # Recursos extras de documentação
    │   ├── imgs            # Pasta para imagens
    │   └── docs            # Documentos extras
    ├── README
    ├── .gitignore
    └── requirements.txt


## Desafios e aprendizados

- Esqueci a boa prática do "git pull" depois de criar sincronizar o repositório remoto. Tive que usar o "git push --force-with-lease, sempre com cautela