#!/usr/bin/env python3
"""
Teste simples para verificar se o Django está servindo arquivos estáticos
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

def test_simple_static():
    """Testa se o Django está servindo arquivos estáticos básicos"""
    client = Client()
    
    print("🔍 Testando arquivos estáticos básicos...")
    
    # Verificar se os arquivos existem fisicamente
    static_dir = settings.STATICFILES_DIRS[0]
    frontend_dir = os.path.join(static_dir, 'frontend')
    assets_dir = os.path.join(frontend_dir, 'assets')
    
    print(f"📁 Diretório estático: {static_dir}")
    print(f"📁 Pasta frontend: {frontend_dir}")
    print(f"📁 Pasta assets: {assets_dir}")
    
    if os.path.exists(static_dir):
        print("✅ Diretório estático existe")
        if os.path.exists(frontend_dir):
            print("✅ Pasta frontend existe")
            if os.path.exists(assets_dir):
                print("✅ Pasta assets existe")
                
                # Listar arquivos
                files = os.listdir(assets_dir)
                print(f"📋 Arquivos em assets: {len(files)}")
                for file in files:
                    file_path = os.path.join(assets_dir, file)
                    size = os.path.getsize(file_path)
                    print(f"   - {file} ({size} bytes)")
            else:
                print("❌ Pasta assets não existe")
        else:
            print("❌ Pasta frontend não existe")
    else:
        print("❌ Diretório estático não existe")
    
    # Testar URLs específicas
    print("\n🔍 Testando URLs específicas...")
    
    test_urls = [
            '/static/css/index-DyYY6vVE.css',
    '/static/js/index-6ofKwcbr.js',
    '/static/css/bootstrap-icons.woff2',
    '/static/img/favicon.svg'
    ]
    
    for url in test_urls:
        try:
            response = client.get(url)
            print(f"🌐 {url}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Conteúdo: {len(response.content)} bytes")
            elif response.status_code == 404:
                print(f"   ❌ Não encontrado")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {url}: Erro - {e}")
    
    # Testar se o Django está configurado para servir arquivos estáticos
    print("\n🔍 Verificando configurações...")
    
    from django.contrib.staticfiles.handlers import StaticFilesHandler
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    print(f"✅ STATIC_URL: {settings.STATIC_URL}")
    print(f"✅ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print(f"✅ DEBUG: {settings.DEBUG}")
    
    # Verificar se o middleware está funcionando
    if 'django.contrib.staticfiles.middleware.StaticFilesMiddleware' in [m.__class__.__name__ for m in settings.MIDDLEWARE]:
        print("✅ StaticFilesMiddleware está ativo")
    else:
        print("❌ StaticFilesMiddleware não está ativo")

if __name__ == '__main__':
    test_simple_static()
