#!/usr/bin/env python3
"""
Teste Completo do Sistema de Ferramentas da Vision Machine

Este script testa todas as funcionalidades de tools:
1. Sistema de backup/restauração de configuração
2. Teste do processador de ferramentas
3. Comandos config_tool e delete_tool
4. Validação de integridade
"""

import cv2
import numpy as np
import json
import requests
import time
from inspection_processor import InspectionProcessor

# Configuração da VM
VM_URL = "http://localhost:5000"
API_CONTROL = f"{VM_URL}/api/control"
API_INSPECTION_CONFIG = f"{VM_URL}/api/inspection_config"

class ToolsTestManager:
    """Gerenciador de testes de tools com backup/restauração"""
    
    def __init__(self):
        self.original_config = None
        self.backup_created = False
        
    def create_backup(self):
        """Cria backup da configuração atual de tools"""
        try:
            print("💾 Criando backup da configuração atual...")
            response = requests.get(API_INSPECTION_CONFIG)
            
            if response.status_code == 200:
                self.original_config = response.json()
                self.backup_created = True
                print(f"   ✅ Backup criado com {len(self.original_config.get('tools', []))} tools")
                return True
            else:
                print(f"   ❌ Erro ao obter configuração: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao criar backup: {str(e)}")
            return False
    
    def restore_backup(self):
        """Restaura a configuração original de tools"""
        if not self.backup_created or not self.original_config:
            print("⚠️ Nenhum backup para restaurar")
            return False
        
        try:
            print("🔄 Restaurando configuração original...")
            
            # Restaurar cada tool original
            tools = self.original_config.get('tools', [])
            for tool in tools:
                response = requests.post(API_CONTROL, json={
                    "command": "config_tool",
                    "params": tool
                })
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Tool {result['tool_name']} restaurada")
                else:
                    print(f"   ❌ Erro ao restaurar tool {tool.get('name')}: {response.status_code}")
            
            print("   ✅ Configuração original restaurada")
            return True
            
        except Exception as e:
            print(f"   ❌ Erro ao restaurar backup: {str(e)}")
            return False
    
    def test_processor_functionality(self):
        """Testa a funcionalidade básica do processador de ferramentas"""
        print("\n🧪 Testando funcionalidade do processador de ferramentas...")
        
        # Configuração de teste
        test_config = {
            "tools": [
                {
                    "id": 1,
                    "name": "grayscale_filter",
                    "type": "grayscale",
                    "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
                    "method": "luminance",
                    "normalize": True,
                    "inspec_pass_fail": False
                },
                {
                    "id": 2,
                    "name": "blob_1",
                    "type": "blob",
                    "ROI": {"x": 0, "y": 10, "w": 100, "h": 100},
                    "th_max": 255,
                    "th_min": 130,
                    "area_min": 100,
                    "area_max": 1000,
                    "test_total_area_max": 100,
                    "test_total_area_min": 50,
                    "test_blob_count_max": 5,
                    "test_blob_count_min": 4,
                    "total_area_test": True,
                    "blob_count_test": True,
                    "inspec_pass_fail": True
                }
            ]
        }
        
        try:
            # 1. Inicializar processador
            print("   1️⃣ Inicializando processador...")
            processor = InspectionProcessor(test_config)
            print(f"      ✅ Processador inicializado com {len(processor.tools)} ferramentas")
            
            # 2. Validar ferramentas
            print("   2️⃣ Validando ferramentas...")
            if processor.validate_all_tools():
                print("      ✅ Todas as ferramentas passaram na validação")
            else:
                print("      ❌ Algumas ferramentas falharam na validação")
                return False
            
            # 3. Criar imagem de teste
            print("   3️⃣ Criando imagem de teste...")
            width, height = 640, 480
            test_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            
            # Adicionar retângulos para simular blobs
            cv2.rectangle(test_image, (10, 20), (80, 90), (200, 200, 200), -1)
            cv2.rectangle(test_image, (20, 30), (70, 80), (180, 180, 180), -1)
            cv2.rectangle(test_image, (30, 40), (60, 70), (160, 160, 160), -1)
            
            print(f"      ✅ Imagem de teste criada: {test_image.shape}")
            
            # 4. Processar inspeção
            print("   4️⃣ Processando inspeção...")
            result = processor.process_inspection(test_image)
            
            # 5. Verificar resultados
            print("   5️⃣ Verificando resultados...")
            summary = result['inspection_summary']
            
            if summary['total_tools'] == 2 and summary['successful_tools'] == 2:
                print("      ✅ Processador funcionando corretamente")
                print(f"      📊 Tempo total: {summary['total_processing_time_ms']:.2f}ms")
                return True
            else:
                print(f"      ❌ Problemas no processamento: {summary}")
                return False
                
        except Exception as e:
            print(f"      ❌ Erro no teste do processador: {str(e)}")
            return False
    
    def test_config_tool(self):
        """Testa o comando config_tool"""
        print("\n🔧 Testando comando config_tool...")
        
        # 1. Teste: Atualizar tool existente
        print("   1️⃣ Testando atualização de tool existente...")
        
        update_config = {
            "id": 1,
            "name": "grayscale_filter",
            "type": "grayscale",
            "ROI": {"x": 50, "y": 50, "w": 600, "h": 400},
            "method": "luminance",
            "normalize": False,
            "inspec_pass_fail": True
        }
        
        try:
            response = requests.post(API_CONTROL, json={
                "command": "config_tool",
                "params": update_config
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ Tool atualizada: {result['tool_name']} ({result['action']})")
            else:
                print(f"      ❌ Erro ao atualizar: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
            return False
        
        # 2. Teste: Adicionar nova tool
        print("   2️⃣ Testando adição de nova tool...")
        
        new_tool_config = {
            "id": 999,
            "name": "math_tool_test",
            "type": "math",
            "ROI": {"x": 100, "y": 100, "w": 200, "h": 200},
            "operation": "add",
            "value": 50,
            "inspec_pass_fail": False
        }
        
        try:
            response = requests.post(API_CONTROL, json={
                "command": "config_tool",
                "params": new_tool_config
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ Nova tool adicionada: {result['tool_name']} (ID: {result['tool_id']})")
            else:
                print(f"      ❌ Erro ao adicionar: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
            return False
        
        # 3. Verificar configuração atual
        print("   3️⃣ Verificando configuração atual...")
        
        try:
            response = requests.get(API_INSPECTION_CONFIG)
            if response.status_code == 200:
                config = response.json()
                tools = config.get('tools', [])
                print(f"      ✅ Total de tools: {len(tools)}")
                
                for tool in tools:
                    print(f"         - {tool.get('name')} (ID: {tool.get('id')})")
            else:
                print(f"      ❌ Erro ao obter configuração: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
            return False
        
        return True
    
    def test_delete_tool(self):
        """Testa o comando delete_tool"""
        print("\n🗑️ Testando comando delete_tool...")
        
        # 1. Teste: Remover tool existente
        print("   1️⃣ Testando remoção de tool existente...")
        
        try:
            response = requests.post(API_CONTROL, json={
                "command": "delete_tool",
                "params": {"id": 2}
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ Tool removida: {result['tool_name']} (ID: {result['tool_id']})")
            else:
                print(f"      ❌ Erro ao remover: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
            return False
        
        # 2. Teste: Tentar remover tool inexistente
        print("   2️⃣ Testando remoção de tool inexistente...")
        
        try:
            response = requests.post(API_CONTROL, json={
                "command": "delete_tool",
                "params": {"id": 999}
            })
            
            if response.status_code == 500:
                result = response.json()
                print(f"      ✅ Erro capturado corretamente: {result.get('error')}")
            else:
                print(f"      ⚠️ Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
        
        # 3. Verificar configuração após remoção
        print("   3️⃣ Verificando configuração após remoção...")
        
        try:
            response = requests.get(API_INSPECTION_CONFIG)
            if response.status_code == 200:
                config = response.json()
                tools = config.get('tools', [])
                print(f"      ✅ Tools restantes: {len(tools)}")
                
                for tool in tools:
                    print(f"         - {tool.get('name')} (ID: {tool.get('id')})")
            else:
                print(f"      ❌ Erro ao obter configuração: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
            return False
        
        return True
    
    def test_error_handling(self):
        """Testa o tratamento de erros dos comandos"""
        print("\n⚠️ Testando tratamento de erros...")
        
        # 1. Teste: config_tool sem parâmetros
        print("   1️⃣ Testando config_tool sem parâmetros...")
        
        try:
            response = requests.post(API_CONTROL, json={
                "command": "config_tool"
            })
            
            if response.status_code == 400:
                result = response.json()
                print(f"      ✅ Erro capturado: {result.get('error')}")
            else:
                print(f"      ⚠️ Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
        
        # 2. Teste: delete_tool sem parâmetros
        print("   2️⃣ Testando delete_tool sem parâmetros...")
        
        try:
            response = requests.post(API_CONTROL, json={
                "command": "delete_tool"
            })
            
            if response.status_code == 400:
                result = response.json()
                print(f"      ✅ Erro capturado: {result.get('error')}")
            else:
                print(f"      ⚠️ Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
        
        # 3. Teste: delete_tool com ID inválido
        print("   3️⃣ Testando delete_tool com ID inválido...")
        
        try:
            response = requests.post(API_CONTROL, json={
                "command": "delete_tool",
                "params": {"id": "abc"}
            })
            
            if response.status_code == 400:
                result = response.json()
                print(f"      ✅ Erro capturado: {result.get('error')}")
            else:
                print(f"      ⚠️ Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erro na requisição: {str(e)}")
        
        return True
    
    def run_all_tests(self):
        """Executa todos os testes de tools"""
        print("🚀 Iniciando Teste Completo do Sistema de Tools")
        print("=" * 70)
        
        # Verificar se a VM está rodando
        try:
            response = requests.get(f"{VM_URL}/api/error")
            if response.status_code != 200:
                print("❌ VM não está respondendo corretamente")
                return False
        except Exception as e:
            print(f"❌ Não foi possível conectar com a VM: {str(e)}")
            print("   Certifique-se de que a VM está rodando em http://localhost:5000")
            return False
        
        print("✅ VM está rodando e respondendo!")
        
        # Criar backup da configuração atual
        if not self.create_backup():
            print("❌ Falha ao criar backup, abortando testes")
            return False
        
        test_results = []
        
        try:
            # Executar todos os testes
            print("\n" + "=" * 70)
            print("🧪 EXECUTANDO TESTES")
            print("=" * 70)
            
            # Teste 1: Funcionalidade do processador
            result1 = self.test_processor_functionality()
            test_results.append(("Processador de Ferramentas", result1))
            
            # Teste 2: Comando config_tool
            result2 = self.test_config_tool()
            test_results.append(("Comando config_tool", result2))
            
            # Teste 3: Comando delete_tool
            result3 = self.test_delete_tool()
            test_results.append(("Comando delete_tool", result3))
            
            # Teste 4: Tratamento de erros
            result4 = self.test_error_handling()
            test_results.append(("Tratamento de Erros", result4))
            
        finally:
            # Sempre restaurar backup
            print("\n" + "=" * 70)
            print("🔄 RESTAURANDO CONFIGURAÇÃO ORIGINAL")
            print("=" * 70)
            
            self.restore_backup()
        
        # Exibir resultados
        print("\n" + "=" * 70)
        print("📊 RESULTADOS DOS TESTES")
        print("=" * 70)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n📈 Resumo: {passed}/{total} testes passaram")
        
        if passed == total:
            print("🎉 Todos os testes passaram com sucesso!")
            return True
        else:
            print("⚠️ Alguns testes falharam")
            return False

def main():
    """Função principal"""
    test_manager = ToolsTestManager()
    success = test_manager.run_all_tests()
    
    if success:
        print("\n🏁 Teste completo concluído com sucesso!")
        exit(0)
    else:
        print("\n💥 Teste completo falhou!")
        exit(1)

if __name__ == "__main__":
    main()
