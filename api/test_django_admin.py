#!/usr/bin/env python3
"""
Teste específico para verificar se o Django está servindo o admin corretamente
"""
import os
import sys
import django
from django.test import Client
from django.urls import resolve

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

def test_admin_serving():
    """Testa se o Django está servindo o admin corretamente"""
    client = Client()
    
    print("🔍 Testando se o Django está servindo o admin corretamente...")
    
    # Testar rota admin
    try:
        response = client.get('/admin/')
        print(f"✅ /admin/ -> Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   → Redirecionamento para login (correto)")
            print(f"   → Location: {response.get('Location', 'N/A')}")
        elif response.status_code == 200:
            print("   → Admin carregado diretamente")
        else:
            print(f"   → Status inesperado: {response.status_code}")
        
        # Verificar se o template é o do admin ou do Vue
        if hasattr(response, 'template_name'):
            print(f"   → Template: {response.template_name}")
        else:
            print("   → Sem template (resposta direta)")
            
    except Exception as e:
        print(f"❌ /admin/ -> Erro: {e}")
    
    # Testar rota admin/login
    try:
        response = client.get('/admin/login/')
        print(f"✅ /admin/login/ -> Status: {response.status_code}")
        
        if hasattr(response, 'template_name'):
            print(f"   → Template: {response.template_name}")
        else:
            print("   → Sem template (resposta direta)")
            
    except Exception as e:
        print(f"❌ /admin/login/ -> Erro: {e}")
    
    # Testar se o admin está registrado
    try:
        from django.contrib import admin
        admin_site = admin.site
        
        print(f"\n✅ Admin Site: {len(admin_site._registry)} modelos registrados")
        
        # Listar modelos registrados
        for model in admin_site._registry:
            print(f"   - {model}")
            
    except Exception as e:
        print(f"❌ Admin Site: Erro - {e}")

def test_url_patterns():
    """Testa os padrões de URL"""
    print("\n🔍 Testando padrões de URL...")
    
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

def test_template_loading():
    """Testa o carregamento de templates"""
    print("\n🔍 Testando carregamento de templates...")
    
    try:
        from django.template.loader import get_template
        from django.conf import settings
        
        # Testar template do admin
        try:
            admin_template = get_template('admin/index.html')
            print("✅ Template admin/index.html: Carregado com sucesso")
        except Exception as e:
            print(f"❌ Template admin/index.html: {e}")
        
        # Testar template do Vue
        try:
            vue_template = get_template('index.html')
            print("✅ Template index.html: Carregado com sucesso")
        except Exception as e:
            print(f"❌ Template index.html: {e}")
            
        # Verificar diretórios de templates
        print(f"✅ TEMPLATES DIRS: {settings.TEMPLATES[0]['DIRS']}")
        
    except Exception as e:
        print(f"❌ Erro ao testar templates: {e}")

if __name__ == '__main__':
    test_admin_serving()
    test_url_patterns()
    test_template_loading()
    
    print("\n🎯 Resumo:")
    print("Para funcionar corretamente:")
    print("- ✅ /admin/ deve retornar status 302 (redirecionamento)")
    print("- ✅ /admin/login/ deve retornar status 200")
    print("- ✅ Admin deve usar template admin/index.html")
    print("- ❌ Admin NÃO deve usar template index.html do Vue")
