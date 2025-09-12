#!/usr/bin/env python3
"""
Script de teste automatizado para a Vision Machine (VM)
Testa todas as funcionalidades implementadas
"""

import requests
import json
import time
import socketio
import os
import glob
from datetime import datetime

# Configuração
VM_URL = "http://localhost:5000"
DJANGO_URL = "http://localhost:8000"

def test_api_endpoints():
    """Testa todos os endpoints da API"""
    print("🧪 TESTANDO ENDPOINTS DA API...")
    
    # Teste 1: Status inicial
    print("\n1️⃣ Testando /api/status...")
    try:
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status obtido: {data['status']}")
            print(f"   Modo: {data['mode']}")
            print(f"   Source: {data['source_config']['type']}")
            if data.get('error_msg'):
                print(f"   Erro: {data['error_msg']}")
            print(f"   Source disponível: {data.get('source_available', 'N/A')}")
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar status: {str(e)}")
        return False
    
    # Teste 2: Configuração de source
    print("\n2️⃣ Testando /api/source_config...")
    try:
        response = requests.get(f"{VM_URL}/api/source_config")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuração de source obtida: {data['type']}")
        else:
            print(f"❌ Erro ao obter source config: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar source config: {str(e)}")
        return False
    
    # Teste 3: Configuração de trigger
    print("\n3️⃣ Testando /api/trigger_config...")
    try:
        response = requests.get(f"{VM_URL}/api/trigger_config")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuração de trigger obtida: {data['type']} - {data['interval_ms']}ms")
        else:
            print(f"❌ Erro ao obter trigger config: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar trigger config: {str(e)}")
        return False
    
    # Teste 4: Informações de erro
    print("\n4️⃣ Testando /api/error...")
    try:
        response = requests.get(f"{VM_URL}/api/error")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Informações de erro obtidas: {data['status']}")
            if data.get('error_msg'):
                print(f"   Mensagem: {data['error_msg']}")
            else:
                print("   ✅ Nenhum erro ativo")
        else:
            print(f"❌ Erro ao obter informações de erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar endpoint de erro: {str(e)}")
        return False
    
    return True

def test_logging_basic():
    """Testa pipeline básico de logging: habilita, processa e verifica .alog."""
    print("\n🧪 TESTANDO LOGGING BÁSICO...")
    try:
        # Salvar config anterior
        status_before = requests.get(f"{VM_URL}/api/status").json()
        prev_logging = status_before.get('logging_config', {})
        prev_trigger = status_before.get('trigger_config', {})

        # Habilitar logging com batch pequeno
        print("1️⃣ Habilitando logging...")
        res = requests.put(f"{VM_URL}/api/logging_config", json={
            "enabled": True,
            "policy": "ALL",
            "batch_size": 2,
            "batch_ms": 200,
            "mode": "keep_last",
            "max_logs": 50
        })
        if res.status_code != 200:
            print(f"❌ Falha ao habilitar logging: {res.status_code}")
            return False

        # Garantir trigger contínuo rápido
        print("2️⃣ Configurando trigger contínuo para gerar frames...")
        res = requests.put(f"{VM_URL}/api/trigger_config", json={"type": "continuous", "interval_ms": 300})
        if res.status_code != 200:
            print(f"❌ Falha ao configurar trigger: {res.status_code}")
            return False

        # Iniciar inspeção
        print("3️⃣ Iniciando inspeção...")
        res = requests.post(f"{VM_URL}/api/control", json={"command": "start_inspection", "params": {}})
        if res.status_code != 200:
            print(f"❌ Falha ao iniciar inspeção: {res.status_code}")
            return False

        # Aguardar processamento e flush do batch (poll com timeout)
        deadline = time.time() + 6.0
        logs_count = 0
        buffer_size = 0
        while time.time() < deadline:
            st = requests.get(f"{VM_URL}/api/status").json()
            logs_count = int(st.get('logs_count', 0))
            buffer_size = int(st.get('logging_buffer_size', 0))
            if logs_count > 0:
                break
            time.sleep(0.3)

        print(f"📦 logs_count={logs_count}, buffer_size={buffer_size}")
        if logs_count < 1:
            # Fallback: checar diretórios comuns (vision_machine/logs e ./logs)
            try:
                vm_logs = os.path.join(os.path.dirname(__file__), 'logs')
                root_logs = os.path.join(os.getcwd(), 'logs')
                cnt = 0
                for path in [vm_logs, root_logs]:
                    if os.path.exists(path):
                        cnt += len([f for f in os.listdir(path) if f.endswith('.alog')])
                if cnt < 1:
                    print("❌ Nenhum .alog encontrado após processamento (filesystem)")
                    return False
                else:
                    print(f"✅ Logs encontrados no filesystem: {cnt}")
            except Exception as fs_err:
                print(f"❌ Erro ao verificar filesystem: {fs_err}")
                return False

        print("✅ Logging básico funcionando")

        # Parar inspeção
        requests.post(f"{VM_URL}/api/control", json={"command": "stop_inspection", "params": {}})

        # Restaurar configurações anteriores
        print("4️⃣ Restaurando configurações anteriores...")
        try:
            requests.put(f"{VM_URL}/api/logging_config", json=prev_logging)
        except Exception:
            pass
        try:
            requests.put(f"{VM_URL}/api/trigger_config", json=prev_trigger)
        except Exception:
            pass

        return True
    except Exception as e:
        print(f"❌ Erro no teste de logging: {str(e)}")
        return False

def test_source_configuration():
    """Testa configuração de diferentes tipos de source"""
    print("\n🧪 TESTANDO CONFIGURAÇÃO DE SOURCE...")
    
    # Teste 1: Configurar source para pasta
    print("\n1️⃣ Testando configuração de pasta...")
    try:
        data = {
            "type": "pasta",
            "folder_path": "./test_images"
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 200:
            print("✅ Source configurado para pasta com sucesso")
        else:
            print(f"❌ Erro ao configurar source para pasta: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar configuração de pasta: {str(e)}")
        return False
    
    # Teste 2: Configurar source para câmera (deve falhar se não houver câmera)
    print("\n2️⃣ Testando configuração de câmera inválida...")
    try:
        data = {
            "type": "camera",
            "camera_id": 999  # Câmera inexistente
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 500:
            print("✅ Erro esperado ao configurar câmera inexistente")
            # Verificar se o erro foi definido
            time.sleep(0.5)
            error_response = requests.get(f"{VM_URL}/api/error")
            if error_response.status_code == 200:
                error_data = error_response.json()
                if error_data.get('error_msg'):
                    print(f"   ✅ Erro capturado: {error_data['error_msg']}")
                else:
                    print("   ❌ Erro não foi capturado")
                    return False
            else:
                print("   ❌ Não foi possível verificar erro")
                return False
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar configuração de câmera: {str(e)}")
        return False
    
    # Teste 3: Limpar erro
    print("\n3️⃣ Testando limpeza de erro...")
    try:
        response = requests.delete(f"{VM_URL}/api/error")
        if response.status_code == 200:
            print("✅ Erro limpo com sucesso")
        else:
            print(f"❌ Erro ao limpar erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar limpeza: {str(e)}")
        return False
    
    # Teste 4: Voltar para source de pasta válido
    print("\n4️⃣ Restaurando source de pasta...")
    try:
        data = {
            "type": "pasta",
            "folder_path": "./test_images"
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 200:
            print("✅ Source de pasta restaurado com sucesso")
        else:
            print(f"❌ Erro ao restaurar source de pasta: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao restaurar source de pasta: {str(e)}")
        return False
    
    return True

def test_mode_control():
    """Testa controle de modo da VM"""
    print("\n🧪 TESTANDO CONTROLE DE MODO...")
    
    # Teste 1: Mudar para modo TESTE
    print("\n1️⃣ Mudando para modo TESTE...")
    try:
        data = {
            "command": "change_mode",
            "params": {"mode": "TESTE"}
        }
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Modo alterado para TESTE")
        else:
            print(f"❌ Erro ao alterar modo: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar mudança de modo: {str(e)}")
        return False
    
    # Teste 2: Verificar status após mudança
    print("\n2️⃣ Verificando status após mudança...")
    try:
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            if data['mode'] == 'TESTE':
                print("✅ Modo confirmado como TESTE")
            else:
                print(f"❌ Modo incorreto: {data['mode']}")
                return False
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        return False
    
    return True

def test_inspection_control():
    """Testa controle de inspeção"""
    print("\n🧪 TESTANDO CONTROLE DE INSPEÇÃO...")
    
    # Pré-requisito: Garantir que source esteja configurado para pasta
    print("\n0️⃣ Configurando source para pasta antes do teste...")
    try:
        data = {
            "type": "pasta",
            "folder_path": "./test_images"
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 200:
            print("✅ Source configurado para pasta com sucesso")
        else:
            print(f"❌ Erro ao configurar source para pasta: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao configurar source para pasta: {str(e)}")
        return False
    
    # Aguardar um pouco para a configuração ser aplicada
    time.sleep(1)
    
    # Verificar se a pasta de imagens existe e tem arquivos
    print("\n🔍 Verificando pasta de imagens...")
    folder_path = "./test_images"
    if os.path.exists(folder_path):
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']:
            image_files.extend(glob.glob(os.path.join(folder_path, ext)))
            image_files.extend(glob.glob(os.path.join(folder_path, ext.upper())))
        print(f"   📁 Pasta encontrada: {folder_path}")
        print(f"   📸 Imagens encontradas: {len(image_files)}")
        if image_files:
            print(f"   📋 Primeiras 3: {[os.path.basename(f) for f in image_files[:3]]}")
        else:
            print("   ⚠️ Nenhuma imagem encontrada na pasta!")
    else:
        print(f"   ❌ Pasta não encontrada: {folder_path}")
    
    # Diagnóstico: Verificar estado antes de iniciar inspeção
    print("\n🔍 Diagnóstico: Verificando estado da VM...")
    try:
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Status: {data['status']}")
            print(f"   🎮 Modo: {data['mode']}")
            print(f"   📸 Source: {data['source_config']['type']}")
            print(f"   📁 Pasta: {data['source_config'].get('folder_path', 'N/A')}")
            print(f"   ✅ Source disponível: {data.get('source_available', 'N/A')}")
            if data.get('error_msg'):
                print(f"   ❌ Erro: {data['error_msg']}")
        else:
            print(f"   ❌ Erro ao obter status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro no diagnóstico: {str(e)}")
    
    # Teste 1: Iniciar inspeção
    print("\n1️⃣ Iniciando inspeção...")
    try:
        data = {"command": "start_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Inspeção iniciada com sucesso")
        else:
            # Tentar obter detalhes do erro
            try:
                error_data = response.json()
                print(f"❌ Erro ao iniciar inspeção: {response.status_code} - {error_data}")
            except:
                print(f"❌ Erro ao iniciar inspeção: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar início de inspeção: {str(e)}")
        return False
    
    # Teste 2: Verificar status após início
    print("\n2️⃣ Verificando status após início...")
    try:
        time.sleep(1)  # Aguardar um pouco
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'running':
                print("✅ Status confirmado como 'running'")
            else:
                print(f"❌ Status incorreto: {data['status']}")
                return False
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        return False
    
    # Teste 3: Tentar iniciar novamente (deve retornar que já está rodando)
    print("\n3️⃣ Tentando iniciar inspeção novamente...")
    try:
        data = {"command": "start_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('message') == 'Inspeção já está rodando':
                print("✅ Comportamento correto: inspeção já está rodando")
            else:
                print(f"⚠️ Resposta inesperada: {result}")
        else:
            print(f"❌ Erro ao tentar iniciar novamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar início duplo: {str(e)}")
        return False
    
    return True

def test_websocket_basic():
    """Teste básico de WebSocket"""
    print("\n🧪 TESTANDO WEBSOCKET BÁSICO...")
    
    try:
        # Criar cliente SocketIO
        sio = socketio.Client(
            logger=False,
            reconnection=False
        )
        
        # Variáveis para controle
        connected = False
        status_received = False
        
        # Configurar eventos
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            print("✅ Conectado ao WebSocket")
            sio.emit('request_status')
        
        @sio.event
        def disconnect():
            nonlocal connected
            connected = False
            print("❌ Desconectado do WebSocket")
        
        @sio.on('connected')
        def on_connected(data):
            print(f"✅ Evento 'connected' recebido: {data}")
        
        @sio.on('status_update')
        def on_status_update(data):
            nonlocal status_received
            status_received = True
            print(f"✅ Evento 'status_update' recebido: {data}")
        
        # Conectar
        print("🔄 Conectando ao WebSocket...")
        sio.connect(f"{VM_URL}", namespaces=['/'])
        
        # Aguardar conexão e eventos
        start_time = time.time()
        while not connected or not status_received:
            if time.time() - start_time > 10:
                print("❌ Timeout aguardando eventos do WebSocket")
                sio.disconnect()
                return False
            time.sleep(0.1)
        
        print("✅ WebSocket funcionando corretamente")
        sio.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste WebSocket: {str(e)}")
        return False

def test_websocket_with_processing():
    """Teste WebSocket com processamento ativo"""
    print("\n🧪 TESTANDO WEBSOCKET COM PROCESSAMENTO...")
    
    # Pré-requisito 1: Garantir que source esteja configurado para pasta
    print("\n0️⃣ Configurando source para pasta antes do teste...")
    try:
        data = {
            "type": "pasta",
            "folder_path": "./test_images"
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 200:
            print("✅ Source configurado para pasta com sucesso")
        else:
            print(f"❌ Erro ao configurar source para pasta: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao configurar source para pasta: {str(e)}")
        return False
    
    # Pré-requisito 2: Garantir que trigger esteja configurado como contínuo
    print("\n1️⃣ Configurando trigger como contínuo antes do teste...")
    try:
        data = {
            "type": "continuous",
            "interval_ms": 500  # Intervalo menor para teste mais rápido
        }
        response = requests.put(f"{VM_URL}/api/trigger_config", json=data)
        if response.status_code == 200:
            print("✅ Trigger configurado como contínuo com sucesso")
        else:
            print(f"❌ Erro ao configurar trigger contínuo: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao configurar trigger contínuo: {str(e)}")
        return False
    
    # Aguardar um pouco para as configurações serem aplicadas
    time.sleep(1)
    
    try:
        # Criar cliente SocketIO
        sio = socketio.Client(
            logger=False,
            reconnection=False
        )
        
        # Variáveis para controle
        connected = False
        test_results_received = []
        required_results = 3  # Reduzido para teste mais rápido
        
        # Configurar eventos
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            print("✅ Conectado ao WebSocket")
        
        @sio.event
        def disconnect():
            nonlocal connected
            connected = False
            print("❌ Desconectado do WebSocket")
        
        @sio.on('test_result')
        def on_test_result(data):
            nonlocal test_results_received
            test_results_received.append(data)
            print(f"🎯 RESULTADO RECEBIDO! Frame {data.get('frame', 'N/A')} - {data.get('time', 'N/A')}")
            print(f"📊 Total recebido: {len(test_results_received)}/{required_results}")
        
        # Conectar
        print("🔄 Conectando ao WebSocket...")
        sio.connect(f"{VM_URL}", namespaces=['/'])
        
        # Aguardar conexão
        start_time = time.time()
        while not connected and (time.time() - start_time) < 5:
            time.sleep(0.1)
        
        if not connected:
            print("❌ Falha ao conectar ao WebSocket")
            sio.disconnect()
            return False
        
        print("✅ WebSocket conectado, aguardando resultados...")
        
        # IMPORTANTE: Iniciar a inspeção para que a VM comece a processar frames
        print("🚀 Iniciando inspeção para gerar frames...")
        try:
            data = {"command": "start_inspection"}
            response = requests.post(f"{VM_URL}/api/control", json=data)
            if response.status_code == 200:
                print("✅ Inspeção iniciada com sucesso")
            else:
                try:
                    error_data = response.json()
                    print(f"❌ Erro ao iniciar inspeção: {response.status_code} - {error_data}")
                except:
                    print(f"❌ Erro ao iniciar inspeção: {response.status_code}")
                sio.disconnect()
                return False
        except Exception as e:
            print(f"❌ Erro ao iniciar inspeção: {str(e)}")
            sio.disconnect()
            return False
        
        # Aguardar um pouco para a inspeção começar
        time.sleep(2)
        
        # Aguardar resultados
        start_time = time.time()
        while len(test_results_received) < required_results:
            if time.time() - start_time > 30:
                print(f"❌ Timeout: recebidos {len(test_results_received)}/{required_results} resultados")
                sio.disconnect()
                return False
            time.sleep(0.1)
        
        print(f"✅ Teste WebSocket concluído: {len(test_results_received)} resultados recebidos")
        sio.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste WebSocket com processamento: {str(e)}")
        return False

def test_error_handling():
    """Testa o sistema de tratamento de erros"""
    print("\n🧪 TESTANDO SISTEMA DE TRATAMENTO DE ERROS...")
    
    # Teste 1: Forçar erro via configuração inválida
    print("\n1️⃣ Forçando erro via configuração inválida...")
    try:
        data = {
            "type": "camera_IP",
            "rtsp_url": ""  # URL vazia deve gerar erro
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 500:
            print("✅ Erro esperado ao configurar RTSP inválido")
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar configuração inválida: {str(e)}")
        return False
    
    # Teste 2: Verificar se erro foi definido
    print("\n2️⃣ Verificando se erro foi definido...")
    try:
        time.sleep(0.5)
        response = requests.get(f"{VM_URL}/api/error")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'error' and data.get('error_msg'):
                print(f"✅ Erro definido corretamente: {data['error_msg']}")
            else:
                print(f"❌ Erro não foi definido corretamente: {data}")
                return False
        else:
            print(f"❌ Erro ao verificar erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar erro: {str(e)}")
        return False
    
    # Teste 3: Tentar iniciar inspeção com erro (deve falhar)
    print("\n3️⃣ Tentando iniciar inspeção com erro...")
    try:
        data = {"command": "start_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 400:
            print("✅ Comportamento correto: inspeção não inicia com erro")
        else:
            print(f"❌ Comportamento incorreto: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar início com erro: {str(e)}")
        return False
    
    # Teste 4: Limpar erro
    print("\n4️⃣ Limpando erro...")
    try:
        response = requests.delete(f"{VM_URL}/api/error")
        if response.status_code == 200:
            print("✅ Erro limpo com sucesso")
        else:
            print(f"❌ Erro ao limpar: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao limpar erro: {str(e)}")
        return False
    
    # Teste 5: Restaurar source de pasta válido
    print("\n5️⃣ Restaurando source de pasta válido...")
    try:
        data = {
            "type": "pasta",
            "folder_path": "./test_images"
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 200:
            print("✅ Source de pasta restaurado com sucesso")
        else:
            print(f"❌ Erro ao restaurar source de pasta: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao restaurar source de pasta: {str(e)}")
        return False
    
    # Teste 6: Verificar se status voltou para idle
    print("\n6️⃣ Verificando se status voltou para idle...")
    try:
        time.sleep(0.5)
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'idle':
                print("✅ Status voltou para idle após limpeza do erro")
            else:
                print(f"❌ Status incorreto após limpeza: {data['status']}")
                return False
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        return False
    
    return True

def test_cleanup():
    """Limpa o estado da VM após os testes"""
    print("\n🧹 LIMPANDO ESTADO DA VM...")
    
    try:
        # Parar inspeção se estiver rodando
        data = {"command": "stop_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Inspeção parada")
        else:
            print(f"⚠️ Não foi possível parar inspeção: {response.status_code}")
        
        # Voltar para modo TESTE
        data = {
            "command": "change_mode",
            "params": {"mode": "TESTE"}
        }
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Modo alterado para TESTE")
        else:
            print(f"⚠️ Não foi possível alterar modo: {response.status_code}")
        
        # Restaurar source de pasta
        data = {
            "type": "pasta",
            "folder_path": "./test_images"
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 200:
            print("✅ Source de pasta restaurado")
        else:
            print(f"⚠️ Não foi possível restaurar source: {response.status_code}")
        
        # Restaurar configuração de trigger padrão
        data = {
            "type": "continuous",
            "interval_ms": 1000
        }
        response = requests.put(f"{VM_URL}/api/trigger_config", json=data)
        if response.status_code == 200:
            print("✅ Configuração de trigger restaurada")
        else:
            print(f"⚠️ Não foi possível restaurar trigger: {response.status_code}")
        
        print("✅ Limpeza concluída")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {str(e)}")
        return False

def test_trigger_modes():
    """Testa os dois tipos de trigger: contínuo e gatilho"""
    print("\n🧪 TESTANDO MODOS DE TRIGGER...")
    
    # Pré-requisito: Garantir que source esteja configurado para pasta
    print("\n0️⃣ Configurando source para pasta antes do teste...")
    try:
        data = {
            "type": "pasta",
            "folder_path": "./test_images"
        }
        response = requests.put(f"{VM_URL}/api/source_config", json=data)
        if response.status_code == 200:
            print("✅ Source configurado para pasta com sucesso")
        else:
            print(f"❌ Erro ao configurar source para pasta: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao configurar source para pasta: {str(e)}")
        return False
    
    # Aguardar um pouco para a configuração ser aplicada
    time.sleep(1)
    
    # Teste 1: Modo Contínuo
    print("\n1️⃣ Testando modo contínuo...")
    try:
        # Configurar modo contínuo
        data = {
            "type": "continuous",
            "interval_ms": 1000
        }
        response = requests.put(f"{VM_URL}/api/trigger_config", json=data)
        if response.status_code == 200:
            print("✅ Trigger configurado para modo contínuo")
        else:
            print(f"❌ Erro ao configurar trigger contínuo: {response.status_code}")
            return False
        
        # Verificar configuração
        response = requests.get(f"{VM_URL}/api/trigger_config")
        if response.status_code == 200:
            config = response.json()
            print(f"   📊 Tipo: {config['type']}")
            print(f"   ⏱️ Intervalo: {config['interval_ms']}ms")
        else:
            print(f"❌ Erro ao verificar configuração: {response.status_code}")
            return False
        
        # Iniciar inspeção
        data = {"command": "start_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Inspeção contínua iniciada")
        else:
            print(f"❌ Erro ao iniciar inspeção contínua: {response.status_code}")
            return False
        
        # Aguardar algumas execuções automáticas
        print("   ⏳ Aguardando execuções automáticas...")
        time.sleep(5)
        
        # Verificar status
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"   📊 Status: {status_data['status']}")
            print(f"   🔄 Trigger info: {status_data.get('trigger_info', 'N/A')}")
        
        # Parar inspeção
        data = {"command": "stop_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Inspeção contínua parada")
        else:
            print(f"⚠️ Erro ao parar inspeção: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro no teste de modo contínuo: {str(e)}")
        return False
    
    # Aguardar um pouco entre os testes
    time.sleep(2)
    
    # Teste 2: Modo Gatilho
    print("\n2️⃣ Testando modo gatilho...")
    try:
        # Configurar modo gatilho
        data = {"type": "trigger"}
        response = requests.put(f"{VM_URL}/api/trigger_config", json=data)
        if response.status_code == 200:
            print("✅ Trigger configurado para modo gatilho")
        else:
            print(f"❌ Erro ao configurar trigger gatilho: {response.status_code}")
            return False
        
        # Verificar configuração
        response = requests.get(f"{VM_URL}/api/trigger_config")
        if response.status_code == 200:
            config = response.json()
            print(f"   📊 Tipo: {config['type']}")
        else:
            print(f"❌ Erro ao verificar configuração: {response.status_code}")
            return False
        
        # Iniciar inspeção
        data = {"command": "start_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Inspeção em modo gatilho iniciada")
        else:
            print(f"❌ Erro ao iniciar inspeção em modo gatilho: {response.status_code}")
            return False
        
        # Verificar se está aguardando trigger
        time.sleep(1)
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            status_data = response.json()
            trigger_info = status_data.get('trigger_info', {})
            if trigger_info.get('waiting_for_trigger'):
                print("✅ VM aguardando trigger")
            else:
                print("⚠️ VM não está aguardando trigger")
        
        # Enviar alguns triggers
        for i in range(3):
            print(f"   🔘 Enviando trigger {i+1}/3...")
            data = {"command": "trigger"}
            response = requests.post(f"{VM_URL}/api/control", json=data)
            if response.status_code == 200:
                print(f"      ✅ Trigger {i+1} executado com sucesso")
            else:
                print(f"      ❌ Erro no trigger {i+1}: {response.status_code}")
                return False
            
            # Aguardar processamento
            time.sleep(2)
        
        # Verificar status final
        response = requests.get(f"{VM_URL}/api/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"   📊 Status final: {status_data['status']}")
            print(f"   🔄 Trigger info: {status_data.get('trigger_info', 'N/A')}")
        
        # Parar inspeção
        data = {"command": "stop_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 200:
            print("✅ Inspeção em modo gatilho parada")
        else:
            print(f"⚠️ Erro ao parar inspeção: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro no teste de modo gatilho: {str(e)}")
        return False
    
    # Teste 3: Validações de trigger
    print("\n3️⃣ Testando validações de trigger...")
    try:
        # Tentar usar comando trigger em modo contínuo (deve falhar)
        print("   🔍 Testando trigger em modo contínuo...")
        
        # Configurar modo contínuo
        data = {"type": "continuous", "interval_ms": 1000}
        response = requests.put(f"{VM_URL}/api/trigger_config", json=data)
        if response.status_code != 200:
            print(f"      ❌ Erro ao configurar modo contínuo: {response.status_code}")
            return False
        
        # Iniciar inspeção
        data = {"command": "start_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code != 200:
            print(f"      ❌ Erro ao iniciar inspeção: {response.status_code}")
            return False
        
        # Tentar comando trigger (deve falhar)
        data = {"command": "trigger"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 400:
            print("      ✅ Comportamento correto: trigger rejeitado em modo contínuo")
        else:
            print(f"      ❌ Comportamento incorreto: {response.status_code}")
            return False
        
        # Parar inspeção
        data = {"command": "stop_inspection"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code != 200:
            print(f"      ⚠️ Erro ao parar inspeção: {response.status_code}")
        
        # Tentar comando trigger sem inspeção rodando (deve falhar)
        print("   🔍 Testando trigger sem inspeção rodando...")
        data = {"command": "trigger"}
        response = requests.post(f"{VM_URL}/api/control", json=data)
        if response.status_code == 400:
            print("      ✅ Comportamento correto: trigger rejeitado sem inspeção")
        else:
            print(f"      ❌ Comportamento incorreto: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste de validações: {str(e)}")
        return False
    
    print("✅ Testes de trigger concluídos com sucesso")
    return True

def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTES COMPLETOS DA VISION MACHINE")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Endpoints da API", test_api_endpoints),
        ("Configuração de Source", test_source_configuration),
        ("Controle de Modo", test_mode_control),
        ("Controle de Inspeção", test_inspection_control),
        ("Logging Básico", test_logging_basic),
        ("WebSocket Básico", test_websocket_basic),
        ("WebSocket com Processamento", test_websocket_with_processing),
        ("Sistema de Tratamento de Erros", test_error_handling),
        ("Limpeza", test_cleanup),
        ("Modos de Trigger", test_trigger_modes)
    ]
    
    # Executar testes
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {str(e)}")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"❌ Testes falharam: {total - passed}")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        return False

if __name__ == '__main__':
    main()
