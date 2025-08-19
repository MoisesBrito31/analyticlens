#!/usr/bin/env python3
"""
Teste simples dos modelos de VM
"""
import os
import sys
import django

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

# Testar import dos modelos
try:
    from api.models import VirtualMachine, VMInspectionTool, VMHeartbeat
    print("✅ Modelos importados com sucesso!")
    
    # Verificar campos
    vm_fields = [f.name for f in VirtualMachine._meta.fields]
    print(f"📋 Campos da VM: {vm_fields}")
    
    tool_fields = [f.name for f in VMInspectionTool._meta.fields]
    print(f"🔧 Campos da Ferramenta: {tool_fields}")
    
    heartbeat_fields = [f.name for f in VMHeartbeat._meta.fields]
    print(f"💓 Campos do Heartbeat: {heartbeat_fields}")
    
    print("\n🎉 Todos os modelos estão funcionando corretamente!")
    
except Exception as e:
    print(f"❌ Erro ao importar modelos: {e}")
    import traceback
    traceback.print_exc()
