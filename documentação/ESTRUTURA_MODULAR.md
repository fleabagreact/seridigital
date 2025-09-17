# Estrutura Modular do SeriDigital

## Visão Geral

O SeriDigital foi reorganizado em uma estrutura modular usando **Flask Blueprints** para melhor organização, manutenibilidade e escalabilidade do código.

## Estrutura de Blueprints

| Blueprint | Arquivo | Prefixo URL | Responsabilidade |
|-----------|---------|-------------|------------------|
| `main` | `app/blueprints/main.py` | `/` | Página inicial e dashboard |
| `auth` | `app/blueprints/auth.py` | `/auth` | Autenticação (login/registro) |
| `users` | `app/blueprints/users.py` | `/users` | Gerenciamento de usuários |
| `posts` | `app/blueprints/posts.py` | `/posts` | Sistema de posts |
| `content` | `app/blueprints/content.py` | `/content` | Gerenciamento de conteúdo |
| `chat` | `app/blueprints/chat.py` | `/chat` | Sistema de mensagens privadas |
| `comunidade` | `app/blueprints/comunidade.py` | `/comunidade` | Sistema de comunidades |
| `feedbacks` | `app/blueprints/feedbacks.py` | `/feedbacks` | Sistema de feedback |
| `redirects` | `app/blueprints/redirects.py` | `/` | Redirecionamentos de URLs antigas |

## Sistema de Comunidades

### Funcionalidades Implementadas

✅ **Criação de Comunidades**: Usuários podem criar comunidades com nome e descrição
✅ **Listagem de Comunidades**: Visualização de todas as comunidades disponíveis
✅ **Postagens**: Sistema de postagens dentro das comunidades
✅ **Sistema de Bloqueio**: Usuários podem bloquear comunidades individualmente
✅ **Filtragem de Conteúdo**: Administradores podem marcar comunidades como filtradas
✅ **Controle de Acesso**: Verificação de permissões baseada em status e bloqueios

### Sistema de Bloqueio e Filtragem

#### Bloqueio Individual
- **Funcionalidade**: Usuários podem bloquear comunidades que não desejam ver
- **Implementação**: Tabela `tb_community_blocks` com relacionamento usuário-comunidade
- **Rotas**:
  - `POST /comunidade/block/<id>` - Bloquear comunidade
  - `POST /comunidade/unblock/<id>` - Desbloquear comunidade
  - `GET /comunidade/blocked` - Listar comunidades bloqueadas

#### Filtragem de Conteúdo
- **Funcionalidade**: Administradores podem marcar comunidades como conteúdo sensível
- **Implementação**: Campos `is_filtered` e `filter_reason` na tabela `tb_communities`
- **Controle**: Checkbox para incluir/excluir conteúdo filtrado na listagem

#### Bloqueio Global
- **Funcionalidade**: Administradores podem bloquear comunidades globalmente
- **Implementação**: Campo `status` na tabela `tb_communities` (active/blocked/private)
- **Rotas Administrativas**:
  - `POST /comunidade/admin/block/<id>` - Bloquear globalmente
  - `POST /comunidade/admin/unblock/<id>` - Desbloquear globalmente
  - `POST /comunidade/admin/filter/<id>` - Marcar como filtrado
  - `POST /comunidade/admin/unfilter/<id>` - Remover filtro

### Modelos de Dados

#### Community (tb_communities)
```python
- id: Identificador único
- owner_id: ID do criador da comunidade
- name: Nome da comunidade
- description: Descrição opcional
- status: Status da comunidade (active/blocked/private)
- is_filtered: Se o conteúdo é filtrado
- filter_reason: Motivo do filtro
- created_at: Data de criação
```

#### CommunityBlock (tb_community_blocks)
```python
- id: Identificador único
- user_id: ID do usuário que bloqueou
- community_id: ID da comunidade bloqueada
- reason: Motivo do bloqueio (opcional)
- created_at: Data do bloqueio
```

### Métodos do Usuário
```python
# Bloquear/desbloquear comunidades
user.block_community(community_id, reason=None)
user.unblock_community(community_id)
user.is_community_blocked(community_id)

# Listar comunidades
user.get_blocked_communities()
user.get_accessible_communities(include_filtered=False)
```

### Métodos da Comunidade
```python
# Verificar status
community.is_blocked()
community.is_private()
community.is_filtered()
community.can_user_access(user_id)
```

## Mapeamento de URLs

| URL Antiga | URL Nova | Blueprint |
|------------|----------|-----------|
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

### Comunidades (Melhorias Futuras)
- Sistema de moderação de postagens
- Relatórios de conteúdo inadequado
- Configurações de privacidade avançadas
- Sistema de convites para comunidades privadas
- Estatísticas de atividade das comunidades

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
6. Implementar sistema de relatórios para administradores