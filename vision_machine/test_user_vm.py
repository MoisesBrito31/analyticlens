#!/usr/bin/env python3
"""
Script de teste interativo para a Vision Machine (VM)
Permite controle manual dos comandos da VM
"""

import requests
import json
import time
import socketio
from datetime import datetime
import os # Adicionado para verificar a existência da pasta

# Configuração
VM_URL = "http://localhost:5000"
DJANGO_URL = "http://localhost:8000"

class VMController:
    """Controlador interativo para a VM"""
    
    def __init__(self):
        self.vm_url = VM_URL
        self.socketio = None
        self.connected = False
        self.test_results = []
        
    def show_menu(self):
        """Mostra o menu de comandos disponíveis"""
        print("\n" + "="*60)
        print("🎮 CONTROLADOR INTERATIVO DA VISION MACHINE")
        print("="*60)
        print("📋 COMANDOS DISPONÍVEIS:")
        print("  1. status          - Mostra status atual da VM")
        print("  2. mode <TESTE|RUN> - Altera modo da VM")
        print("  3. start           - Inicia inspeção")
        print("  4. stop            - Para inspeção")
        print("  5. source          - Mostra configuração de source")
        print("  6. trigger         - Mostra configuração de trigger")
        print("  7. websocket       - Conecta ao WebSocket")
        print("  8. disconnect      - Desconecta do WebSocket")
        print("  9. results         - Mostra resultados recebidos")
        print("  10. clear          - Limpa resultados")
        print("  11. error          - Mostra informações de erro")
        print("  12. set_error <msg> - Define uma mensagem de erro")
        print("  13. clear_error    - Limpa mensagem de erro")
        print("  14. source_pasta <caminho> - Configura source para pasta")
        print("  15. source_camera <id> - Configura source para câmera local")
        print("  16. source_rtsp <url> - Configura source para câmera IP")
        print("  17. help           - Mostra este menu")
        print("  18. end            - Finaliza o programa")
        print("="*60)
        print("💡 Exemplos: mode TESTE, start, status, set_error 'Falha na câmera'")
        print("💡 Source: source_pasta './minhas_imagens', source_camera 1, source_rtsp 'rtsp://192.168.1.100:554'")
        print("💡 Use Ctrl+C para sair a qualquer momento")
        print("="*60)
    
    def execute_command(self, command):
        """Executa um comando"""
        try:
            parts = command.strip().split()
            if not parts:
                return
            
            cmd = parts[0].lower()
            
            if cmd == "status":
                self.get_status()
            elif cmd == "mode":
                if len(parts) > 1:
                    self.change_mode(parts[1])
                else:
                    print("❌ Uso: mode <TESTE|RUN>")
            elif cmd == "start":
                self.start_inspection()
            elif cmd == "stop":
                self.stop_inspection()
            elif cmd == "source":
                self.get_source_config()
            elif cmd == "trigger":
                self.get_trigger_config()
            elif cmd == "websocket":
                self.connect_websocket()
            elif cmd == "disconnect":
                self.disconnect_websocket()
            elif cmd == "results":
                self.show_results()
            elif cmd == "clear":
                self.clear_results()
            elif cmd == "error":
                self.get_error_info()
            elif cmd == "set_error":
                if len(parts) > 1:
                    error_msg = " ".join(parts[1:])
                    self.set_error(error_msg)
                else:
                    print("❌ Uso: set_error <mensagem>")
            elif cmd == "clear_error":
                self.clear_error()
            elif cmd == "source_pasta":
                if len(parts) > 1:
                    folder_path = parts[1]
                    self.set_source_pasta(folder_path)
                else:
                    print("❌ Uso: source_pasta <caminho>")
            elif cmd == "source_camera":
                if len(parts) > 1:
                    try:
                        camera_id = int(parts[1])
                        self.set_source_camera(camera_id)
                    except ValueError:
                        print("❌ ID da câmera deve ser um número")
                else:
                    print("❌ Uso: source_camera <id>")
            elif cmd == "source_rtsp":
                if len(parts) > 1:
                    rtsp_url = parts[1]
                    self.set_source_rtsp(rtsp_url)
                else:
                    print("❌ Uso: source_rtsp <url>")
            elif cmd == "help":
                self.show_menu()
            elif cmd == "end":
                print("👋 Finalizando programa...")
                return False
            else:
                print(f"❌ Comando não reconhecido: {cmd}")
                print("💡 Digite 'help' para ver comandos disponíveis")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao executar comando: {str(e)}")
            return True
    
    def get_status(self):
        """Obtém status atual da VM"""
        try:
            response = requests.get(f"{self.vm_url}/api/status")
            if response.status_code == 200:
                data = response.json()
                print(f"\n📊 STATUS DA VM:")
                print(f"   🆔 ID: {data['machine_id']}")
                print(f"   📈 Status: {data['status']}")
                print(f"   🎮 Modo: {data['mode']}")
                print(f"   🔌 Conexão: {data['connection_status']}")
                if data.get('error_msg'):
                    print(f"   ❌ Erro: {data['error_msg']}")
                print(f"   📅 Timestamp: {data['timestamp']}")
                print(f"   📸 Source: {data['source_config']['type']}")
                print(f"   ⚡ Trigger: {data['trigger_config']['type']}")
            else:
                print(f"❌ Erro ao obter status: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro na conexão: {str(e)}")
    
    def change_mode(self, new_mode):
        """Altera modo da VM"""
        if new_mode not in ['TESTE', 'RUN']:
            print(f"❌ Modo inválido: {new_mode}. Use TESTE ou RUN")
            return
        
        try:
            data = {
                "command": "change_mode",
                "params": {"mode": new_mode}
            }
            response = requests.post(
                f"{self.vm_url}/api/control",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Modo alterado para: {result['new_mode']}")
                # Verificar status após mudança
                time.sleep(0.5)
                self.get_status()
            else:
                print(f"❌ Erro ao alterar modo: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao alterar modo: {str(e)}")
    
    def start_inspection(self):
        """Inicia inspeção"""
        try:
            data = {"command": "start_inspection"}
            response = requests.post(
                f"{self.vm_url}/api/control",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Inspeção iniciada: {result['success']}")
                # Verificar status após início
                time.sleep(0.5)
                self.get_status()
            else:
                print(f"❌ Erro ao iniciar inspeção: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao iniciar inspeção: {str(e)}")
    
    def stop_inspection(self):
        """Para inspeção"""
        try:
            data = {"command": "stop_inspection"}
            response = requests.post(
                f"{self.vm_url}/api/control",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Inspeção parada: {result['success']}")
                # Verificar status após parada
                time.sleep(0.5)
                self.get_status()
            else:
                print(f"❌ Erro ao parar inspeção: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao parar inspeção: {str(e)}")
    
    def get_source_config(self):
        """Obtém configuração de source"""
        try:
            response = requests.get(f"{self.vm_url}/api/source_config")
            if response.status_code == 200:
                data = response.json()
                print(f"\n📸 CONFIGURAÇÃO DE SOURCE:")
                print(f"   🎯 Tipo: {data['type']}")
                print(f"   📁 Pasta: {data.get('folder_path', 'N/A')}")
                print(f"   📷 Câmera ID: {data.get('camera_id', 'N/A')}")
                print(f"   📐 Resolução: {data.get('resolution', 'N/A')}")
                print(f"   🎬 FPS: {data.get('fps', 'N/A')}")
                print(f"   🌐 RTSP URL: {data.get('rtsp_url', 'N/A')}")
            else:
                print(f"❌ Erro ao obter source config: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao obter source config: {str(e)}")
    
    def get_trigger_config(self):
        """Obtém configuração de trigger"""
        try:
            response = requests.get(f"{self.vm_url}/api/trigger_config")
            if response.status_code == 200:
                data = response.json()
                print(f"\n⚡ CONFIGURAÇÃO DE TRIGGER:")
                print(f"   🎯 Tipo: {data['type']}")
                print(f"   ⏱️ Intervalo: {data.get('interval_ms', 'N/A')}ms")
            else:
                print(f"❌ Erro ao obter trigger config: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao obter trigger config: {str(e)}")
    
    def connect_websocket(self):
        """Conecta ao WebSocket"""
        if self.connected:
            print("⚠️ Já conectado ao WebSocket")
            return
        
        try:
            print("🔄 Conectando ao WebSocket...")
            
            # Criar cliente SocketIO
            self.socketio = socketio.Client(
                logger=False,
                reconnection=False
            )
            
            # Configurar eventos
            @self.socketio.event
            def connect():
                nonlocal self
                self.connected = True
                print("✅ Conectado ao WebSocket!")
                self.socketio.emit('request_status')
            
            @self.socketio.event
            def disconnect():
                nonlocal self
                self.connected = False
                print("❌ Desconectado do WebSocket")
            
            @self.socketio.on('connected')
            def on_connected(data):
                print(f"✅ Evento 'connected' recebido: {data}")
            
            @self.socketio.on('status_update')
            def on_status_update(data):
                print(f"✅ Evento 'status_update' recebido: {data}")
            
            @self.socketio.on('test_result')
            def on_test_result(data):
                nonlocal self
                self.test_results.append(data)
                print(f"🎯 RESULTADO RECEBIDO! Frame {data.get('frame', 'N/A')} - {data.get('time', 'N/A')}")
                print(f"📊 Total recebido: {len(self.test_results)}")
            
            # Conectar
            self.socketio.connect(f"{self.vm_url}", namespaces=['/'])
            
            # Aguardar conexão
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < 5:
                time.sleep(0.1)
            
            if self.connected:
                print("🎉 WebSocket conectado e funcionando!")
                print("💡 Agora inicie uma inspeção para receber resultados em tempo real")
            else:
                print("❌ Falha ao conectar ao WebSocket")
                self.socketio = None
                
        except Exception as e:
            print(f"❌ Erro ao conectar WebSocket: {str(e)}")
            self.socketio = None
    
    def disconnect_websocket(self):
        """Desconecta do WebSocket"""
        if not self.connected or not self.socketio:
            print("⚠️ Não está conectado ao WebSocket")
            return
        
        try:
            self.socketio.disconnect()
            self.connected = False
            self.socketio = None
            print("✅ Desconectado do WebSocket")
        except Exception as e:
            print(f"❌ Erro ao desconectar: {str(e)}")
    
    def show_results(self):
        """Mostra resultados recebidos via WebSocket"""
        if not self.test_results:
            print("📭 Nenhum resultado recebido ainda")
            return
        
        print(f"\n📊 RESULTADOS RECEBIDOS ({len(self.test_results)}):")
        for i, result in enumerate(self.test_results, 1):
            print(f"  {i}. Frame {result.get('frame', 'N/A')} - {result.get('time', 'N/A')}")
            print(f"     Aprovados: {result.get('aprovados', 'N/A')} | Reprovados: {result.get('reprovados', 'N/A')}")
            print(f"     Timestamp: {result.get('timestamp', 'N/A')}")
            if i < len(self.test_results):
                print()
    
    def clear_results(self):
        """Limpa resultados recebidos"""
        self.test_results.clear()
        print("🧹 Resultados limpos")
    
    def get_error_info(self):
        """Obtém informações de erro da VM"""
        try:
            response = requests.get(f"{self.vm_url}/api/error")
            if response.status_code == 200:
                data = response.json()
                print(f"\n❌ INFORMAÇÕES DE ERRO:")
                print(f"   📈 Status: {data['status']}")
                if data.get('error_msg'):
                    print(f"   💬 Mensagem: {data['error_msg']}")
                else:
                    print("   ✅ Nenhum erro ativo")
            else:
                print(f"❌ Erro ao obter informações de erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro na conexão: {str(e)}")
    
    def set_error(self, error_message: str):
        """Define uma mensagem de erro na VM"""
        try:
            data = {"error_msg": error_message}
            response = requests.post(
                f"{self.vm_url}/api/error",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Erro definido: {result['message']}")
                # Verificar status após definição do erro
                time.sleep(0.5)
                self.get_status()
            else:
                print(f"❌ Erro ao definir mensagem de erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao definir mensagem de erro: {str(e)}")
    
    def clear_error(self):
        """Limpa a mensagem de erro da VM"""
        try:
            response = requests.delete(f"{self.vm_url}/api/error")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Erro limpo: {result['message']}")
                # Verificar status após limpeza do erro
                time.sleep(0.5)
                self.get_status()
            elif response.status_code == 404:
                print("⚠️ Nenhum erro para limpar")
            else:
                print(f"❌ Erro ao limpar mensagem de erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao limpar mensagem de erro: {str(e)}")
    
    def set_source_pasta(self, folder_path: str):
        """Configura source para pasta de imagens"""
        try:
            # Verificar se a pasta existe
            if not os.path.exists(folder_path):
                print(f"⚠️ Pasta não encontrada: {folder_path}")
                create = input("Deseja criar a pasta? (s/n): ").strip().lower()
                if create != 's':
                    print("❌ Operação cancelada")
                    return
            
            data = {
                "type": "pasta",
                "folder_path": folder_path
            }
            response = requests.put(
                f"{self.vm_url}/api/source_config",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"✅ Source configurado para pasta: {folder_path}")
                # Verificar configuração após mudança
                time.sleep(0.5)
                self.get_source_config()
            else:
                print(f"❌ Erro ao configurar source: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao configurar source: {str(e)}")
    
    def set_source_camera(self, camera_id: int):
        """Configura source para câmera local"""
        try:
            data = {
                "type": "camera",
                "camera_id": camera_id,
                "resolution": [640, 480],
                "fps": 30
            }
            response = requests.put(
                f"{self.vm_url}/api/source_config",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"✅ Source configurado para câmera ID: {camera_id}")
                # Verificar configuração após mudança
                time.sleep(0.5)
                self.get_source_config()
            else:
                print(f"❌ Erro ao configurar source: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao configurar source: {str(e)}")
    
    def set_source_rtsp(self, rtsp_url: str):
        """Configura source para câmera IP via RTSP"""
        try:
            data = {
                "type": "camera_IP",
                "rtsp_url": rtsp_url
            }
            response = requests.put(
                f"{self.vm_url}/api/source_config",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"✅ Source configurado para RTSP: {rtsp_url}")
                # Verificar configuração após mudança
                time.sleep(0.5)
                self.get_source_config()
            else:
                print(f"❌ Erro ao configurar source: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao configurar source: {str(e)}")
    
    def run(self):
        """Executa o controlador interativo"""
        print("🚀 Iniciando Controlador Interativo da Vision Machine...")
        print(f"📍 URL da VM: {self.vm_url}")
        
        # Verificar se a VM está rodando
        try:
            response = requests.get(f"{self.vm_url}/api/status")
            if response.status_code == 200:
                print("✅ VM está rodando e acessível!")
            else:
                print(f"⚠️ VM respondeu com status {response.status_code}")
        except Exception as e:
            print(f"❌ VM não está acessível: {str(e)}")
            print("💡 Certifique-se de que a VM está rodando (python vm.py)")
            return
        
        # Mostrar menu inicial
        self.show_menu()
        
        # Loop principal
        try:
            while True:
                try:
                    command = input("\n🎮 Digite um comando (ou 'help' para menu): ").strip()
                    
                    if not command:
                        continue
                    
                    # Executar comando
                    if not self.execute_command(command):
                        break
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️ Interrompido pelo usuário (Ctrl+C)")
                    break
                except EOFError:
                    print("\n\n👋 Finalizando...")
                    break
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrompido pelo usuário (Ctrl+C)")
        
        finally:
            # Limpeza final
            if self.connected and self.socketio:
                try:
                    self.disconnect_websocket()
                except:
                    pass
            
            print("\n👋 Controlador finalizado!")

def main():
    """Função principal"""
    controller = VMController()
    controller.run()

if __name__ == '__main__':
    main()
