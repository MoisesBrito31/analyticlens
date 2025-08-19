#!/usr/bin/env python3
"""
Teste para verificar se o Django consegue importar o middleware
"""
import os
import sys
import django

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

try:
    django.setup()
    print("✅ Django configurado com sucesso")
    
    # Tentar importar o middleware
    try:
        from django.contrib.staticfiles.middleware import StaticFilesMiddleware
        print("✅ StaticFilesMiddleware importado com sucesso")
        
        # Verificar se está na lista de MIDDLEWARE
        from django.conf import settings
        print(f"📋 MIDDLEWARE configurado: {len(settings.MIDDLEWARE)} itens")
        
        for i, middleware in enumerate(settings.MIDDLEWARE):
            print(f"  {i+1}. {middleware}")
            if 'StaticFilesMiddleware' in middleware:
                print(f"     ⭐ StaticFilesMiddleware encontrado!")
                
    except ImportError as e:
        print(f"❌ Erro ao importar StaticFilesMiddleware: {e}")
        
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
