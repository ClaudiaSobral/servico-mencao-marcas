# Tarefas do projeto

## Planejamento
- [x] Delimitar entregáveis
- [x] Criar repo
- [x] Criar README.md
- [x] Criar arquivos de apoio

## Framework
- [x] Escolher um framework que faça sentido com a PiniOn (v-tracker)

## Funcionalidades modularizadas (testadas)
- [x] Modelo de validação em JSON
- [x] Ingestão de input em arquivo JSON
- [x] Detecção de menções
- [x] Armazenamento dos dados coletados
- [ ] Execução do script que orquestra os anteriores


## Teste
- [x] Pensar nos testes
- [x] Teste de modelo de validação em JSON
- [x] Teste de ingestão de input em arquivo JSON
- [x] Teste de detecção de menções
- [x] Teste de armazenamento dos dados coletados
- [ ] Teste de execução do script que orquestra os anteriores


# Lembretes
- Tratar "null", "n/a", "none" e variáveis como nulos
✅ Lembrar de verificar se as menções estão com variação para erro de digitação 
- Lembrar de registrar o que os testes fazem
    - Quando escrever sobre os testes, falar sobre opção por testar o básico
- Provavelmente eu vou deixar de fora os testes de carga, de vazamento de memória etc... Considerar também se eu deveria prever mais erros de uso e implementar mais try/excepts
- Considerar também segurança.
✅ A princípio, eu não sei o quanto o modelo lida com uma SQL injection, por exemplo
✅ Explicar marcas_mencionadas = Column(JSON)em armazenamento.py