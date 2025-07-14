#!/bin/bash
# Comandos úteis para desenvolvimento do SeriDigital

echo "🚀 SeriDigital - Comandos de Desenvolvimento"
echo "============================================="

case "$1" in
    "start")
        echo "▶️  Iniciando aplicação..."
        python run.py
        ;;
    "test")
        echo "🧪 Testando rotas..."
        python test_routes.py
        ;;
    "structure")
        echo "📁 Estrutura do projeto:"
        tree app/ -I "__pycache__"
        ;;
    "blueprints")
        echo "📋 Verificando blueprints..."
        python -c "from app import create_app; app = create_app(); [print(f'✅ {bp.name}') for bp in app.blueprints.values()]"
        ;;
    "routes")
        echo "🛣️  Listando todas as rotas..."
        python -c "
from app import create_app
app = create_app()
with app.app_context():
    for rule in app.url_map.iter_rules():
        print(f'{rule.endpoint:30} {rule.rule:30} {list(rule.methods)}')
"
        ;;
    "clean")
        echo "🧹 Limpando cache..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        echo "✅ Cache limpo!"
        ;;
    *)
        echo "Uso: $0 {start|test|structure|blueprints|routes|clean}"
        echo ""
        echo "Comandos disponíveis:"
        echo "  start      - Inicia a aplicação"
        echo "  test       - Testa todas as rotas"
        echo "  structure  - Mostra estrutura do projeto"
        echo "  blueprints - Lista blueprints registrados"
        echo "  routes     - Lista todas as rotas"
        echo "  clean      - Limpa arquivos de cache"
        ;;
esac