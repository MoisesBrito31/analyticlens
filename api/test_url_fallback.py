#!/usr/bin/env python3
"""
Teste específico para verificar se o fallback não está capturando rotas do Django
"""
import os
import sys
import django
from django.test import Client
from django.urls import resolve, reverse

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

def test_url_resolution():
    """Testa a resolução específica de URLs"""
    print("🔍 Testando resolução específica de URLs...")
    
    # Testar rota admin
    try:
        resolved = resolve('/admin/')
        print(f"✅ /admin/ -> {resolved.func} (namespace: {resolved.namespace})")
        
        if 'admin' in str(resolved.func):
            print("   ✅ Corretamente resolvido para o admin Django")
        else:
            print("   ❌ Resolvido incorretamente")
            
    except Exception as e:
        print(f"❌ /admin/ -> Erro: {e}")
    
    # Testar rota admin/login
    try:
        resolved = resolve('/admin/login/')
        print(f"✅ /admin/login/ -> {resolved.func} (namespace: {resolved.namespace})")
    except Exception as e:
        print(f"❌ /admin/login/ -> Erro: {e}")
    
    # Testar rota API
    try:
        resolved = resolve('/api/')
        print(f"✅ /api/ -> {resolved.func} (namespace: {resolved.namespace})")
    except Exception as e:
        print(f"❌ /api/ -> Erro: {e}")
    
    # Testar rota que deve cair no fallback
    try:
        resolved = resolve('/pagina-que-nao-existe/')
        print(f"✅ /pagina-que-nao-existe/ -> {resolved.func} (namespace: {resolved.namespace})")
        
        if 'TemplateView' in str(resolved.func):
            print("   ✅ Corretamente resolvido para o fallback Vue")
        else:
            print("   ❌ Resolvido incorretamente")
            
    except Exception as e:
        print(f"❌ /pagina-que-nao-existe/ -> Erro: {e}")

def test_fallback_pattern():
    """Testa o padrão de fallback"""
    print("\n🔍 Testando padrão de fallback...")
    
    import re
    
    # Padrão atual
    pattern = r'^(?!admin|api|static|media).*$'
    
    # URLs para testar
    test_urls = [
        '/admin/',
        '/admin/login/',
        '/api/',
        '/api/auth/',
        '/static/css/',
        '/media/images/',
        '/pagina-que-nao-existe/',
        '/home',
        '/machines',
        '/configurations'
    ]
    
    print(f"Padrão: {pattern}")
    print("\nTestando URLs:")
    
    for url in test_urls:
        matches = bool(re.match(pattern, url))
        status = "✅ NÃO capturado" if not matches else "❌ CAPTURADO"
        print(f"  {url} -> {status}")
        
        if url.startswith(('/admin', '/api', '/static', '/media')) and matches:
            print(f"    ⚠️  PROBLEMA: Rota do Django sendo capturada pelo fallback!")
        elif not url.startswith(('/admin', '/api', '/static', '/media')) and not matches:
            print(f"    ⚠️  PROBLEMA: Rota do Vue NÃO sendo capturada pelo fallback!")

def test_client_responses():
    """Testa respostas do cliente para diferentes URLs"""
    print("\n🔍 Testando respostas do cliente...")
    
    client = Client()
    
    # URLs para testar
    test_urls = [
        ('/admin/', 'Admin Django'),
        ('/api/', 'API'),
        ('/pagina-que-nao-existe/', 'Fallback Vue')
    ]
    
    for url, description in test_urls:
        try:
            response = client.get(url)
            print(f"✅ {description} ({url}): {response.status_code}")
            
            # Verificar se retorna o template correto
            if hasattr(response, 'template_name'):
                if 'index.html' in str(response.template_name):
                    print(f"   → Retorna template Vue (fallback)")
                else:
                    print(f"   → Retorna template Django")
            else:
                print(f"   → Resposta direta do Django")
                
        except Exception as e:
            print(f"❌ {description} ({url}): Erro - {e}")

if __name__ == '__main__':
    test_url_resolution()
    test_fallback_pattern()
    test_client_responses()
    
    print("\n🎯 Resumo:")
    print("Para funcionar corretamente:")
    print("- ✅ /admin/ deve ser resolvido pelo Django (não pelo fallback)")
    print("- ✅ /api/ deve ser resolvido pelo Django (não pelo fallback)")
    print("- ✅ /pagina-que-nao-existe/ deve ser capturada pelo fallback")
    print("- ❌ Rotas do Django NÃO devem ser capturadas pelo fallback")
