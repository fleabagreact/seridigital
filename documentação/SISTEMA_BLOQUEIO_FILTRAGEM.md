# Sistema de Bloqueio e Filtragem de Comunidades

## Visão Geral

O sistema de bloqueio e filtragem de comunidades foi implementado para proporcionar controle granular sobre o acesso e visibilidade de comunidades na plataforma SeriDigital. Este sistema opera exclusivamente a nível de backend, garantindo segurança e performance.

## Funcionalidades Implementadas

### 1. Bloqueio Individual de Comunidades

**Descrição**: Permite que usuários bloqueiem comunidades específicas que não desejam visualizar.

**Implementação**:

- Tabela `tb_community_blocks` para armazenar bloqueios
- Relacionamento muitos-para-muitos entre usuários e comunidades
- Campo opcional para motivo do bloqueio

**Rotas**:

- `POST /comunidade/block/<community_id>` - Bloquear comunidade
- `POST /comunidade/unblock/<community_id>` - Desbloquear comunidade
- `GET /comunidade/blocked` - Listar comunidades bloqueadas

**Exemplo de Uso**:

```python
# Bloquear uma comunidade
success, message = current_user.block_community(community_id, "Conteúdo inadequado")

# Verificar se está bloqueada
if current_user.is_community_blocked(community_id):
    # Comunidade bloqueada
    pass

# Listar comunidades bloqueadas
blocked_communities = current_user.get_blocked_communities()
```

### 2. Filtragem de Conteúdo Sensível

**Descrição**: Permite que administradores marquem comunidades como contendo conteúdo sensível.

**Implementação**:

- Campo `is_filtered` na tabela `tb_communities`
- Campo `filter_reason` para documentar o motivo
- Controle via checkbox na interface

**Rotas Administrativas**:

- `POST /comunidade/admin/filter/<community_id>` - Marcar como filtrado
- `POST /comunidade/admin/unfilter/<community_id>` - Remover filtro

**Exemplo de Uso**:

```python
# Verificar se comunidade está filtrada
if community.is_filtered:
    # Conteúdo sensível
    pass

# Listar comunidades incluindo filtradas
communities = current_user.get_accessible_communities(include_filtered=True)
```

### 3. Bloqueio Global de Comunidades

**Descrição**: Permite que administradores bloqueiem comunidades globalmente para todos os usuários.

**Implementação**:

- Campo `status` na tabela `tb_communities`
- Valores possíveis: `active`, `blocked`, `private`
- Controle de acesso baseado em status

**Rotas Administrativas**:

- `POST /comunidade/admin/block/<community_id>` - Bloquear globalmente
- `POST /comunidade/admin/unblock/<community_id>` - Desbloquear globalmente

**Exemplo de Uso**:

```python
# Verificar status da comunidade
if community.is_blocked():
    # Comunidade bloqueada globalmente
    pass

if community.is_private():
    # Comunidade privada
    pass

# Verificar acesso do usuário
if community.can_user_access(user_id):
    # Usuário pode acessar
    pass
```

## Estrutura do Banco de Dados

### Tabela `tb_communities` (Campos Adicionados)

```sql
ALTER TABLE tb_communities ADD COLUMN com_status VARCHAR(20) DEFAULT 'active' NOT NULL;
ALTER TABLE tb_communities ADD COLUMN com_is_filtered BOOLEAN DEFAULT 0 NOT NULL;
ALTER TABLE tb_communities ADD COLUMN com_filter_reason VARCHAR(255);
```

**Campos**:

- `com_status`: Status da comunidade (`active`, `blocked`, `private`)
- `com_is_filtered`: Se o conteúdo é filtrado (boolean)
- `com_filter_reason`: Motivo do filtro (texto opcional)

### Tabela `tb_community_blocks` (Nova Tabela)

```sql
CREATE TABLE tb_community_blocks (
    blk_id INTEGER PRIMARY KEY,
    blk_user_id INTEGER NOT NULL,
    blk_community_id INTEGER NOT NULL,
    blk_reason VARCHAR(255),
    blk_created_at DATETIME NOT NULL,
    FOREIGN KEY (blk_user_id) REFERENCES tb_users(usr_id),
    FOREIGN KEY (blk_community_id) REFERENCES tb_communities(com_id)
);
```

**Campos**:

- `blk_id`: Identificador único do bloqueio
- `blk_user_id`: ID do usuário que bloqueou
- `blk_community_id`: ID da comunidade bloqueada
- `blk_reason`: Motivo do bloqueio (opcional)
- `blk_created_at`: Data e hora do bloqueio

## Modelos e Métodos

### Classe `Community`

```python
class Community(db.Model):
    # ... campos existentes ...
    status = db.Column('com_status', db.String(20), default='active', nullable=False)
    is_filtered = db.Column('com_is_filtered', db.Boolean, default=False, nullable=False)
    filter_reason = db.Column('com_filter_reason', db.String(255))
    
    # Métodos
    def is_blocked(self):
        return self.status == 'blocked'
    
    def is_private(self):
        return self.status == 'private'
    
    def is_filtered(self):
        return self.is_filtered
    
    def can_user_access(self, user_id):
        if self.is_blocked():
            return False
        if self.is_private() and self.owner_id != user_id:
            return False
        return True
```

### Classe `CommunityBlock`

```python
class CommunityBlock(db.Model):
    __tablename__ = 'tb_community_blocks'
    
    id = db.Column('blk_id', db.Integer, primary_key=True)
    user_id = db.Column('blk_user_id', db.Integer, db.ForeignKey('tb_users.usr_id'), nullable=False)
    community_id = db.Column('blk_community_id', db.Integer, db.ForeignKey('tb_communities.com_id'), nullable=False)
    reason = db.Column('blk_reason', db.String(255))
    created_at = db.Column('blk_created_at', db.DateTime, default=datetime.utcnow, nullable=False)
```

### Métodos Adicionados à Classe `Usuario`

```python
# Bloquear/desbloquear comunidades
def block_community(self, community_id, reason=None):
    """Bloqueia uma comunidade para o usuário"""
    
def unblock_community(self, community_id):
    """Remove o bloqueio de uma comunidade"""
    
def is_community_blocked(self, community_id):
    """Verifica se uma comunidade está bloqueada pelo usuário"""
    
def get_blocked_communities(self):
    """Retorna todas as comunidades bloqueadas pelo usuário"""
    
def get_accessible_communities(self, include_filtered=False):
    """Retorna todas as comunidades acessíveis ao usuário"""
```

## Fluxo de Controle de Acesso

### 1. Listagem de Comunidades

```python
@comunidade_bp.route('/', methods=['GET'])
@login_required
def comunidade():
    include_filtered = request.args.get('include_filtered', 'false').lower() == 'true'
    comunidades = current_user.get_accessible_communities(include_filtered=include_filtered)
    return render_template('lista_comunidades.html', comunidades=comunidades)
```

**Lógica**:

1. Busca comunidades com status `active`
2. Exclui comunidades bloqueadas pelo usuário
3. Filtra por conteúdo sensível se necessário
4. Ordena por data de criação

### 2. Acesso a Comunidade Específica

```python
@comunidade_bp.route('/<int:community_id>', methods=['GET', 'POST'])
@login_required
def comunidade_users(community_id):
    comunidade = Community.query.get_or_404(community_id)
    
    # Verifica permissões
    if not comunidade.can_user_access(current_user.id):
        flash('Você não tem permissão para acessar esta comunidade.', 'error')
        return redirect(url_for('comunidade.comunidade'))
    
    # Verifica bloqueio individual
    if current_user.is_community_blocked(community_id):
        flash('Esta comunidade está bloqueada para você.', 'error')
        return redirect(url_for('comunidade.comunidade'))
```

**Lógica**:

1. Verifica se a comunidade existe
2. Verifica se o usuário tem permissão de acesso
3. Verifica se a comunidade está bloqueada pelo usuário
4. Permite acesso se todas as verificações passarem

## Interface do Usuário

### Lista de Comunidades

- **Checkbox**: Para incluir/excluir conteúdo filtrado
- **Dropdown**: Menu de ações por comunidade (entrar, bloquear, etc.)
- **Badges**: Indicadores visuais de status (filtrado, privada)
- **Link**: Para visualizar comunidades bloqueadas

### Comunidades Bloqueadas

- **Lista**: Todas as comunidades bloqueadas pelo usuário
- **Botão**: Para desbloquear comunidades
- **Navegação**: Link para voltar à lista principal

## Segurança e Performance

### Medidas de Segurança

1. **Verificação de Permissões**: Todas as rotas verificam permissões
2. **Validação de Dados**: Entrada de dados é validada
3. **Controle de Acesso**: Apenas administradores podem usar rotas administrativas
4. **Proteção CSRF**: Formulários incluem proteção CSRF

### Otimizações de Performance

1. **Queries Otimizadas**: Uso de subqueries para excluir bloqueios
2. **Índices**: Campos de busca são indexados
3. **Lazy Loading**: Relacionamentos carregados sob demanda
4. **Cache**: Resultados podem ser cacheados se necessário

## Testes e Validação

### Cenários de Teste

1. **Bloqueio Individual**:
   - Usuário bloqueia comunidade
   - Comunidade não aparece na lista
   - Usuário não pode acessar comunidade bloqueada
   - Desbloqueio funciona corretamente

2. **Filtragem de Conteúdo**:
   - Administrador marca comunidade como filtrada
   - Conteúdo filtrado só aparece com checkbox ativado
   - Motivo do filtro é armazenado

3. **Bloqueio Global**:
   - Administrador bloqueia comunidade globalmente
   - Nenhum usuário pode acessar
   - Desbloqueio global funciona

4. **Controle de Acesso**:
   - Comunidades privadas só acessíveis pelo proprietário
   - Comunidades bloqueadas não acessíveis
   - Permissões de administrador funcionam

## Manutenção e Monitoramento

### Logs Recomendados

```python
# Exemplo de logging
import logging

logger = logging.getLogger(__name__)

def block_community(self, community_id, reason=None):
    try:
        # ... lógica de bloqueio ...
        logger.info(f"Usuário {self.id} bloqueou comunidade {community_id}")
    except Exception as e:
        logger.error(f"Erro ao bloquear comunidade: {e}")
```

### Métricas Sugeridas

- Número de bloqueios por comunidade
- Comunidades mais bloqueadas
- Frequência de uso do sistema de filtragem
- Performance das queries de listagem

## Próximas Melhorias

1. **Sistema de Relatórios**: Dashboard para administradores
2. **Notificações**: Alertas sobre comunidades bloqueadas/filtradas
3. **API REST**: Endpoints para integração externa
4. **Cache Redis**: Melhorar performance de listagens
5. **Análise de Conteúdo**: Detecção automática de conteúdo sensível
