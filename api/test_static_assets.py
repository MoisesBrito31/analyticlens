#!/usr/bin/env python3
"""
Teste para verificar se os assets estáticos estão sendo servidos corretamente
"""
import os
import sys
import django
from django.test import Client
from django.conf import settings

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

def test_static_assets():
    """Testa se os assets estáticos estão sendo servidos corretamente"""
    client = Client()
    
    print("🔍 Testando assets estáticos...")
    
    # Testar assets principais (usando nomes reais do build)
    static_assets = [
            ('/static/css/index-DyYY6vVE.css', 'CSS Principal'),
    ('/static/js/index-6ofKwcbr.js', 'JavaScript Principal'),
    ('/static/css/bootstrap-icons.woff2', 'Fonte Bootstrap Icons (WOFF2)'),
    ('/static/css/bootstrap-icons.woff', 'Fonte Bootstrap Icons (WOFF)'),
    ('/static/img/logo.svg', 'Logo SVG'),
    ('/static/img/logo-large.svg', 'Logo Large SVG'),
    ('/static/img/favicon.svg', 'Favicon SVG'),
    ('/static/img/favicon.ico', 'Favicon ICO'),
    ]
    
    for url, description in static_assets:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description}: {response.status_code}")
                
                # Verificar se o conteúdo não está vazio
                if len(response.content) > 0:
                    print(f"   → Tamanho: {len(response.content)} bytes")
                else:
                    print(f"   ⚠️  Arquivo vazio!")
                    
            else:
                print(f"❌ {description}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")
    
    # Testar se o template está sendo servido corretamente
    print("\n🔍 Testando template principal...")
    try:
        response = client.get('/')
        print(f"✅ Template principal: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar se as referências aos assets estão corretas
            if '/static/css/' in content or '/static/js/' in content or '/static/img/' in content:
                print("   ✅ Referências aos assets estão corretas")
            else:
                print("   ❌ Referências aos assets incorretas")
                
            # Verificar se o favicon está correto
            if 'href="/static/img/favicon.ico"' in content:
                print("   ✅ Favicon referenciado corretamente")
            else:
                print("   ❌ Favicon não encontrado ou referenciado incorretamente")
                
        else:
            print(f"   ❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Template principal: Erro - {e}")

def test_static_settings():
    """Testa as configurações de arquivos estáticos"""
    print("\n🔍 Testando configurações de arquivos estáticos...")
    
    try:
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        print(f"✅ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        print(f"✅ STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Não definido')}")
        
        # Verificar se os diretórios existem
        for static_dir in settings.STATICFILES_DIRS:
            if os.path.exists(static_dir):
                print(f"✅ Diretório estático existe: {static_dir}")
                
                # Listar alguns arquivos
                frontend_dir = os.path.join(static_dir, 'frontend')
                if os.path.exists(frontend_dir):
                    print(f"   → Pasta frontend encontrada")
                    assets_dir = os.path.join(frontend_dir, 'assets')
                    if os.path.exists(assets_dir):
                        assets = os.listdir(assets_dir)
                        print(f"   → Assets encontrados: {len(assets)} arquivos")
                        for asset in assets[:5]:  # Mostrar apenas os primeiros 5
                            print(f"     - {asset}")
                        if len(assets) > 5:
                            print(f"     ... e mais {len(assets) - 5} arquivos")
                    else:
                        print(f"   ❌ Pasta assets não encontrada")
                else:
                    print(f"   ❌ Pasta frontend não encontrada")
            else:
                print(f"❌ Diretório estático não existe: {static_dir}")
                
    except Exception as e:
        print(f"❌ Erro ao verificar configurações: {e}")

if __name__ == '__main__':
    test_static_assets()
    test_static_settings()
    
    print("\n🎯 Resumo:")
    print("Para funcionar corretamente:")
    print("- ✅ Todos os assets devem retornar status 200")
    print("- ✅ Arquivos não devem estar vazios")
    print("- ✅ Template deve referenciar assets corretamente")
    print("- ✅ Configurações de STATIC devem estar corretas")
