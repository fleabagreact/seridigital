#!/usr/bin/env python3
"""
Script para testar todas as rotas da aplicação
"""
import requests
import sys

BASE_URL = 'http://127.0.0.1:5000'

# Rotas para testar (GET requests)
ROUTES_TO_TEST = [
    '/',                           # main.index
    '/auth/login',                 # auth.login
    '/auth/register',              # auth.register
    '/users/list',                 # users.list_users
    '/posts/',                     # posts.list_posts
    '/content/',                   # content.list_content
    # Redirecionamentos
    '/cad_users',                  # redirects.old_register
    '/lista_users',                # redirects.old_list_users
]

def test_routes():
    """Testa se todas as rotas estão respondendo"""
    print("Testando rotas da aplicação...\n")
    
    success_count = 0
    total_count = len(ROUTES_TO_TEST)
    
    for route in ROUTES_TO_TEST:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5, allow_redirects=True)
            
            if response.status_code == 200:
                print(f"OK  {route} - (200)")
                success_count += 1
            elif response.status_code in [301, 302]:
                print(f"RED {route} - ({response.status_code})")
                success_count += 1
            else:
                print(f"ERR {route} - ({response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"ERR {route} - Erro de conexão: {e}")
    
    print(f"\nResultado: {success_count}/{total_count} rotas funcionando")
    
    if success_count == total_count:
        print("Todos os testes passaram!")
        return True
    else:
        print("Alguns testes falharam.")
        return False

def check_server():
    """Verifica se o servidor está rodando"""
    try:
        requests.get(BASE_URL, timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False

if __name__ == '__main__':
    print("SeriDigital - Teste de Rotas\n")
    
    if not check_server():
        print(f"Servidor não está rodando em {BASE_URL}")
        print("Execute 'python run.py' em outro terminal primeiro")
        sys.exit(1)
    
    success = test_routes()
    sys.exit(0 if success else 1)