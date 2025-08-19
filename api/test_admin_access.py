#!/usr/bin/env python3
"""
Teste específico para verificar acesso ao admin Django
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

def test_admin_access():
    """Testa especificamente o acesso ao admin"""
    client = Client()
    
    print("🔍 Testando acesso ao Admin Django...")
    
    # Testar rota admin
    try:
        response = client.get('/admin/')
        print(f"✅ Admin Django: {response.status_code} - {response.reason_phrase}")
        
        if response.status_code == 302:
            print("   → Redirecionamento para login (esperado)")
        elif response.status_code == 200:
            print("   → Admin carregado diretamente")
        else:
            print(f"   → Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Admin Django: Erro - {e}")
    
    # Testar rota admin/login
    try:
        response = client.get('/admin/login/')
        print(f"✅ Admin Login: {response.status_code} - {response.reason_phrase}")
    except Exception as e:
        print(f"❌ Admin Login: Erro - {e}")
    
    # Testar se o admin está registrado
    try:
        from django.contrib import admin
        admin_site = admin.site
        print(f"✅ Admin Site: {len(admin_site._registry)} modelos registrados")
        
        # Listar modelos registrados
        for model in admin_site._registry:
            print(f"   - {model}")
            
    except Exception as e:
        print(f"❌ Admin Site: Erro - {e}")

def test_url_resolution():
    """Testa a resolução de URLs"""
    print("\n🔍 Testando resolução de URLs...")
    
    try:
        from server.urls import urlpatterns
        
        print("📋 Padrões de URL registrados:")
        for i, pattern in enumerate(urlpatterns):
            print(f"  {i+1}. {pattern.pattern} -> {pattern.callback}")
            
            # Verificar se é o admin
            if 'admin' in str(pattern.pattern):
                print(f"     ⭐ É uma rota de admin!")
                
            if hasattr(pattern, 'url_patterns'):
                for sub_pattern in pattern.url_patterns:
                    print(f"     └─ {sub_pattern.pattern}")
                    
    except Exception as e:
        print(f"❌ Erro ao verificar URLs: {e}")

def test_static_files():
    """Testa arquivos estáticos"""
    print("\n🔍 Testando arquivos estáticos...")
    
    try:
        from django.conf import settings
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        print(f"✅ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        
        # Testar se o template index.html existe
        template_path = os.path.join(settings.BASE_DIR, 'server', 'templates', 'index.html')
        if os.path.exists(template_path):
            print(f"✅ Template index.html: Encontrado")
        else:
            print(f"❌ Template index.html: Não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao verificar arquivos estáticos: {e}")

if __name__ == '__main__':
    test_admin_access()
    test_url_resolution()
    test_static_files()
    
    print("\n🎯 Resumo:")
    print("Se o admin estiver funcionando, você deve ver:")
    print("- ✅ Admin Django: 302 - Found (redirecionamento para login)")
    print("- ✅ Admin Login: 200 - OK")
    print("- ✅ Admin Site: X modelos registrados")
    print("- ⭐ É uma rota de admin! nas URLs")
