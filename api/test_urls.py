#!/usr/bin/env python3
"""
Teste das URLs do Django para identificar conflitos
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

def test_urls():
    """Testa as principais URLs do sistema"""
    client = Client()
    
    print("🔍 Testando URLs do Django...")
    
    # Testar admin
    try:
        response = client.get('/admin/')
        print(f"✅ Admin: {response.status_code} - {response.reason_phrase}")
    except Exception as e:
        print(f"❌ Admin: Erro - {e}")
    
    # Testar API
    try:
        response = client.get('/api/')
        print(f"✅ API: {response.status_code} - {response.reason_phrase}")
    except Exception as e:
        print(f"❌ API: Erro - {e}")
    
    # Testar API auth
    try:
        response = client.get('/api/auth/')
        print(f"✅ API Auth: {response.status_code} - {response.reason_phrase}")
    except Exception as e:
        print(f"❌ API Auth: Erro - {e}")
    
    # Testar rota que deve cair no fallback
    try:
        response = client.get('/teste-vue-route/')
        print(f"✅ Fallback Vue: {response.status_code} - {response.reason_phrase}")
        if response.status_code == 200:
            print(f"   Template usado: {response.template_name}")
    except Exception as e:
        print(f"❌ Fallback Vue: Erro - {e}")
    
    # Testar static files
    try:
        response = client.get('/static/frontend/')
        print(f"✅ Static Files: {response.status_code} - {response.reason_phrase}")
    except Exception as e:
        print(f"❌ Static Files: Erro - {e}")

def test_url_patterns():
    """Testa os padrões de URL registrados"""
    from server.urls import urlpatterns
    
    print("\n📋 Padrões de URL registrados:")
    for i, pattern in enumerate(urlpatterns):
        print(f"  {i+1}. {pattern.pattern} -> {pattern.callback}")
        if hasattr(pattern, 'url_patterns'):
            for sub_pattern in pattern.url_patterns:
                print(f"     └─ {sub_pattern.pattern}")

if __name__ == '__main__':
    test_urls()
    test_url_patterns()
