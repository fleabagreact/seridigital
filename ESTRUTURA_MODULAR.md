# Estrutura Modular do SeriDigital

## Visão Geral

O projeto foi reorganizado usando uma arquitetura modular baseada em Flask Blueprints para facilitar a manutenção e escalabilidade. Cada funcionalidade principal está separada em seu próprio módulo.

## Estrutura de Diretórios

```
app/
├── __init__.py                 # Configuração principal da aplicação
├── config.py                   # Configurações
├── models.py                   # Modelos do banco de dados
├── extensions.py               # Extensões do Flask
├── blueprints/                 # Módulos organizados por funcionalidade
│   ├── __init__.py
│   ├── main.py                 # Páginas principais (index, etc.)
│   ├── auth.py                 # Autenticação (login, registro, logout)
│   ├── users.py                # Gerenciamento de usuários
│   ├── posts.py                # Sistema de posts (futuro)
│   └── content.py              # Gerenciamento de conteúdo
├── templates/                  # Templates organizados por módulo
│   ├── base.html              # Template base
│   ├── main/
│   │   └── index.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── users/
│   │   ├── list.html
│   │   ├── profile.html
│   │   └── edit.html
│   ├── posts/
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── view.html
│   │   └── edit.html
│   └── content/
│       ├── list.html
│       ├── create.html
│       ├── view.html
│       └── edit.html
└── static/                     # Arquivos estáticos (CSS, JS, imagens)
```

## Módulos (Blueprints)

### 1. Main (`main.py`)
- **Responsabilidade**: Páginas principais e navegação geral
- **Rotas**:
  - `/` - Página inicial
- **Prefixo**: Nenhum

### 2. Auth (`auth.py`)
- **Responsabilidade**: Autenticação e autorização
- **Rotas**:
  - `/auth/login` - Login de usuários
  - `/auth/register` - Cadastro de novos usuários
  - `/auth/logout` - Logout
- **Prefixo**: `/auth`

### 3. Users (`users.py`)
- **Responsabilidade**: Gerenciamento de perfis de usuários
- **Rotas**:
  - `/users/list` - Lista de usuários
  - `/users/profile/<id>` - Perfil de usuário
  - `/users/edit/<id>` - Editar perfil
  - `/users/delete` - Deletar conta
- **Prefixo**: `/users`

### 4. Posts (`posts.py`)
- **Responsabilidade**: Sistema de posts da comunidade (em desenvolvimento)
- **Rotas**:
  - `/posts/` - Lista de posts
  - `/posts/create` - Criar post
  - `/posts/<id>` - Visualizar post
  - `/posts/<id>/edit` - Editar post
  - `/posts/<id>/delete` - Deletar post
- **Prefixo**: `/posts`

### 5. Content (`content.py`)
- **Responsabilidade**: Gerenciamento de conteúdo (séries, filmes, etc.)
- **Rotas**:
  - `/content/` - Lista de conteúdo
  - `/content/create` - Adicionar conteúdo
  - `/content/<id>` - Visualizar conteúdo
  - `/content/<id>/edit` - Editar conteúdo
  - `/content/<id>/delete` - Deletar conteúdo
- **Prefixo**: `/content`

## Vantagens da Nova Estrutura

### 1. **Modularidade**
- Cada funcionalidade está isolada em seu próprio módulo
- Facilita a manutenção e desenvolvimento de novas features
- Permite trabalho em equipe mais eficiente

### 2. **Escalabilidade**
- Fácil adição de novos módulos
- Estrutura preparada para crescimento do projeto
- Separação clara de responsabilidades

### 3. **Organização**
- Templates organizados por funcionalidade
- Código mais limpo e fácil de navegar
- Redução de conflitos em desenvolvimento

### 4. **Reutilização**
- Template base comum a todos os módulos
- Componentes reutilizáveis
- Padrões consistentes

## Migração das Rotas Antigas

### Mapeamento de URLs:

| Rota Antiga | Nova Rota | Módulo |
|-------------|-----------|---------|
| `/` | `/` | main |
| `/cad_users` | `/auth/register` | auth |
| `/login` | `/auth/login` | auth |
| `/logout` | `/auth/logout` | auth |
| `/lista_users` | `/users/list` | users |
| `/atualizar_usuario/<id>` | `/users/edit/<id>` | users |
| `/deletar_usuario` | `/users/delete` | users |

## Como Adicionar Novos Módulos

1. **Criar o arquivo do blueprint**:
   ```python
   # app/blueprints/novo_modulo.py
   from flask import Blueprint
   
   novo_modulo_bp = Blueprint('novo_modulo', __name__, url_prefix='/novo_modulo')
   
   @novo_modulo_bp.route('/')
   def index():
       return render_template('novo_modulo/index.html')
   ```

2. **Registrar no app principal**:
   ```python
   # app/__init__.py
   from .blueprints.novo_modulo import novo_modulo_bp
   app.register_blueprint(novo_modulo_bp)
   ```

3. **Criar templates**:
   ```
   app/templates/novo_modulo/
   ├── index.html
   └── ...
   ```

## Funcionalidades Futuras Planejadas

### Posts
- Sistema completo de posts da comunidade
- Comentários e likes
- Categorização e tags
- Sistema de moderação

### Conteúdo
- Sistema de avaliações e reviews
- Recomendações personalizadas
- Histórico de visualização
- Categorias e filtros avançados

### Usuários
- Sistema de seguir/seguidores
- Mensagens privadas
- Configurações avançadas de perfil
- Sistema de badges/conquistas

## Considerações Técnicas

- **Flask-Login**: Mantido para autenticação
- **SQLAlchemy**: Modelos de banco inalterados
- **Templates**: Migrados para estrutura modular com template base
- **Bootstrap**: Integrado no template base para UI consistente
- **Compatibilidade**: URLs antigas podem ser redirecionadas se necessário

## Próximos Passos

1. Testar todas as funcionalidades migradas
2. Implementar sistema de posts completo
3. Adicionar funcionalidades de conteúdo avançadas
4. Implementar sistema de notificações
5. Adicionar testes automatizados para cada módulo