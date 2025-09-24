# Seridigital

Repositório oficial do projeto **Seridigital**, desenvolvido como parte da Prática Profissional dos alunos do IFRN Campus Caicó.

## Alunos

- **Anna Júlia Galvão de Medeiros**
- **Andrei Moisés Medeiros Delfino**
- **Gustavo Henrique Alves de Melo**
- **Jeffersson Dos Anjos Santos**
- **Luiza Souza e Silva**
- **Maria Rita Lucena Santos**

## Funcionalidades Principais

### Sistema de Comunidades

- ✅ Criação e gerenciamento de comunidades
- ✅ Sistema de postagens
- ✅ Sistema de bloqueio individual de comunidades
- ✅ Filtragem de conteúdo sensível
- ✅ Bloqueio global por administradores
- ✅ Controle de acesso baseado em permissões

### Sistema de Usuários

- ✅ Autenticação e registro
- ✅ Perfis de usuário
- ✅ Sistema de seguidores
- ✅ Mensagens privadas

### Sistema de Conteúdo

- ✅ Gerenciamento de séries e filmes
- ✅ Sistema de avaliações
- ✅ Histórico de visualização
- ✅ Categorização de conteúdo

## Documentação

- [Estrutura Modular](ESTRUTURA_MODULAR.md) - Organização do projeto em blueprints
- [Sistema de Bloqueio e Filtragem](SISTEMA_BLOQUEIO_FILTRAGEM.md) - Documentação completa do sistema de controle de comunidades
- [Resumo da Reorganização](RESUMO_REORGANIZACAO.md) - Histórico das mudanças no projeto

## Tecnologias Utilizadas

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Banco de Dados**: SQLite
- **Frontend**: Bootstrap, HTML/CSS/JavaScript
- **Migrações**: Alembic

## Instalação e Execução

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute a aplicação: `python run.py`

## Comandos de Desenvolvimento

```bash
# Iniciar aplicação
./comandos_dev.sh start

# Testar rotas
./comandos_dev.sh test

# Ver estrutura do projeto
./comandos_dev.sh structure

# Listar rotas
./comandos_dev.sh routes
```
