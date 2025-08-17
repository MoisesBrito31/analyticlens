#!/usr/bin/env python3
"""
AnalyticLens - Vision Machine (VM)
Servidor Flask para máquina de visão computacional

Este módulo implementa uma VM Flask que se comunica com o Django orquestrador
via REST API, WebSocket e Webhooks conforme o protocolo definido.
"""

import os
import json
import time
import logging
import asyncio
import signal
import atexit
import glob
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit, disconnect
import cv2
import numpy as np

# Import do sistema de ferramentas
try:
    from inspection_processor import InspectionProcessor
    TOOLS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Sistema de ferramentas não disponível: {str(e)}")
    TOOLS_AVAILABLE = False

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageSource:
    """Classe para gerenciar diferentes fontes de imagem"""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.source_type = source_config.get('type', 'camera')
        self.capture = None
        self.image_files = []
        self.current_image_index = 0
        
        # Inicializar source
        self._initialize_source()
    
    def _initialize_source(self):
        """Inicializa o source baseado no tipo configurado"""
        try:
            if self.source_type == 'pasta':
                self._initialize_folder_source()
            elif self.source_type == 'camera':
                self._initialize_camera_source()
            elif self.source_type == 'camera_IP':
                self._initialize_rtsp_source()
            else:
                error_msg = f"Tipo de source não suportado: {self.source_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"Erro ao inicializar source {self.source_type}: {str(e)}")
            # Re-raise para que o erro seja capturado pelo update_source_config
            raise
    
    def _initialize_folder_source(self):
        """Inicializa source de pasta com imagens"""
        folder_path = self.source_config.get('folder_path', './test_images')
        logger.info(f"📁 Inicializando source de pasta: {folder_path}")
        
        try:
            # Verificar se pasta existe
            if not os.path.exists(folder_path):
                logger.warning(f"⚠️ Pasta não encontrada: {folder_path}")
                os.makedirs(folder_path, exist_ok=True)
                logger.info(f"✅ Pasta criada: {folder_path}")
            else:
                logger.info(f"✅ Pasta encontrada: {folder_path}")
            
            # Buscar imagens na pasta
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
            logger.info(f"🔍 Buscando imagens com extensões: {image_extensions}")
            
            for ext in image_extensions:
                files_found = glob.glob(os.path.join(folder_path, ext))
                files_found.extend(glob.glob(os.path.join(folder_path, ext.upper())))
                if files_found:
                    logger.info(f"📸 Encontradas {len(files_found)} imagens com extensão {ext}")
                self.image_files.extend(files_found)
            
            self.image_files.sort()
            logger.info(f"🎯 Total de imagens encontradas: {len(self.image_files)}")
            if self.image_files:
                logger.info(f"📋 Primeiras 3 imagens: {self.image_files[:3]}")
                logger.info(f"📋 Últimas 3 imagens: {self.image_files[-3:]}")
            else:
                warning_msg = f"Nenhuma imagem encontrada na pasta: {folder_path}"
                logger.warning(warning_msg)
                # Não é um erro crítico, apenas um aviso
                
        except Exception as e:
            error_msg = f"Erro ao inicializar source de pasta {folder_path}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _initialize_camera_source(self):
        """Inicializa source de câmera local"""
        camera_id = self.source_config.get('camera_id', 0)
        
        try:
            self.capture = cv2.VideoCapture(camera_id)
            if not self.capture.isOpened():
                error_msg = f"Não foi possível abrir câmera {camera_id}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Configurar propriedades da câmera
            resolution = self.source_config.get('resolution', (640, 480))
            fps = self.source_config.get('fps', 30)
            
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            self.capture.set(cv2.CAP_PROP_FPS, fps)
            
            logger.info(f"Source câmera {camera_id} inicializado: {resolution[0]}x{resolution[1]} @ {fps}fps")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar câmera {camera_id}: {str(e)}")
            self.capture = None
            raise  # Re-raise para propagar o erro
    
    def _initialize_rtsp_source(self):
        """Inicializa source de câmera IP via RTSP"""
        rtsp_url = self.source_config.get('rtsp_url', '')
        
        if not rtsp_url:
            error_msg = "URL RTSP não configurada"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            self.capture = cv2.VideoCapture(rtsp_url)
            if not self.capture.isOpened():
                error_msg = f"Não foi possível conectar ao RTSP: {rtsp_url}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Configurar timeout para RTSP
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            logger.info(f"Source RTSP inicializado: {rtsp_url}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar RTSP {rtsp_url}: {str(e)}")
            self.capture = None
            raise  # Re-raise para propagar o erro
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Obtém o próximo frame da fonte de imagem"""
        try:
            if self.source_type == 'pasta':
                return self._get_folder_frame()
            elif self.source_type in ['camera', 'camera_IP']:
                return self._get_camera_frame()
            else:
                error_msg = f"Tipo de source não suportado: {self.source_type}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"Erro ao obter frame: {str(e)}"
            logger.error(f"❌ {error_msg}")
            # Re-raise para ser capturado pelo _processing_loop
            raise Exception(error_msg)
    
    def _get_folder_frame(self) -> Optional[np.ndarray]:
        """Obtém frame da pasta de imagens (fila cíclica)"""
        if not self.image_files:
            logger.warning("⚠️ Nenhuma imagem encontrada na pasta")
            return None
        
        try:
            # Ler imagem atual
            image_path = self.image_files[self.current_image_index]
            logger.info(f"📁 Lendo imagem: {image_path}")
            
            frame = cv2.imread(image_path)
            
            if frame is None:
                error_msg = f"Erro ao ler imagem: {image_path}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            # Avançar para próxima imagem (fila cíclica)
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            
            logger.info(f"✅ Imagem lida com sucesso: {frame.shape}")
            return frame
            
        except Exception as e:
            error_msg = f"Erro ao ler imagem da pasta: {str(e)}"
            logger.error(f"❌ {error_msg}")
            # Re-raise para ser capturado pelo _processing_loop
            raise Exception(error_msg)
    
    def _get_camera_frame(self) -> Optional[np.ndarray]:
        """Obtém frame da câmera (local ou IP)"""
        if self.capture is None or not self.capture.isOpened():
            error_msg = "Câmera não está disponível"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        try:
            ret, frame = self.capture.read()
            if not ret:
                error_msg = "Falha ao ler frame da câmera"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            return frame
            
        except Exception as e:
            error_msg = f"Erro ao ler frame da câmera: {str(e)}"
            logger.error(f"❌ {error_msg}")
            # Re-raise para ser capturado pelo _processing_loop
            raise Exception(error_msg)
    
    def release(self):
        """Libera recursos da câmera"""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
            logger.info("Recursos da câmera liberados")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Atualiza configuração do source"""
        try:
            old_type = self.source_type
            
            # Liberar recursos antigos
            self.release()
            
            # Atualizar configuração
            self.source_config.update(new_config)
            self.source_type = self.source_config.get('type', 'camera')
            
            # Reinicializar com nova configuração
            self._initialize_source()
            
            logger.info(f"Source atualizado de {old_type} para {self.source_type}")
            
        except Exception as e:
            error_msg = f"Erro ao atualizar configuração do source: {str(e)}"
            logger.error(error_msg)
            # Re-raise para que o erro seja capturado pelo update_source_config
            raise

class TestModeProcessor:
    """Processador para o modo teste da VM"""
    
    def __init__(self, vm_instance, socketio_instance):
        self.vm = vm_instance
        self.socketio = socketio_instance
        self.running = False
        self.processing_thread = None
        self.frame_count = 0
        self.approved_count = 0
        self.rejected_count = 0
        self.last_websocket_update = 0
        self.websocket_update_interval = 1.0  # 1 segundo
        
        # Controle para modo gatilho
        self.trigger_requested = False
        self.trigger_lock = threading.Lock()
        
    def start(self):
        """Inicia o processamento em modo teste"""
        if self.running:
            logger.warning("⚠️ Processador de teste já está rodando")
            return
        
        # Verificar se há erro ativo
        if self.vm.status == 'error':
            logger.error("❌ Não é possível iniciar processamento com erro ativo")
            return
        
        logger.info("🚀 Iniciando processador de teste...")
        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        logger.info("✅ Processador de modo teste iniciado com sucesso")
        logger.info(f"📊 Thread ID: {self.processing_thread.ident}")
        logger.info(f"📊 Thread ativo: {self.processing_thread.is_alive()}")
    
    def stop(self):
        """Para o processamento em modo teste"""
        logger.info("🛑 Parando processador de teste...")
        self.running = False
        if self.processing_thread and self.processing_thread.is_alive():
            logger.info("⏳ Aguardando thread finalizar...")
            self.processing_thread.join(timeout=2)
            logger.info(f"📊 Thread finalizada: {not self.processing_thread.is_alive()}")
        logger.info("✅ Processador de modo teste parado")
    
    def request_trigger(self):
        """Solicita execução de uma inspeção (modo gatilho)"""
        with self.trigger_lock:
            self.trigger_requested = True
            logger.info("🔘 Trigger solicitado para próxima execução")
    
    def _processing_loop(self):
        """Loop principal de processamento"""
        logger.info("🔄 Loop de processamento iniciado")
        while self.running:
            try:
                # Verificar se está em modo teste
                if self.vm.mode != 'TESTE':
                    time.sleep(0.1)
                    continue
                
                # Verificar se há erro ativo - se sim, parar processamento
                if self.vm.status == 'error':
                    logger.warning("⚠️ VM em estado de erro, aguardando resolução...")
                    time.sleep(1)
                    continue
                
                # Verificar se image_source existe
                if not hasattr(self.vm, 'image_source') or self.vm.image_source is None:
                    error_message = "Source de imagem não disponível"
                    logger.error(f"❌ {error_message}")
                    self.vm.set_error(error_message)
                    self.running = False
                    break
                
                # Verificar tipo de trigger
                trigger_type = self.vm.trigger_config.get('type', 'continuous')
                
                if trigger_type == 'trigger':
                    # Modo gatilho: só processar se trigger foi solicitado
                    with self.trigger_lock:
                        if not self.trigger_requested:
                            time.sleep(0.1)  # Aguardar trigger
                            continue
                        else:
                            self.trigger_requested = False  # Consumir trigger
                            logger.info("🔘 Trigger consumido, processando frame...")
                
                # Obter frame da fonte de imagem
                frame = self.vm.image_source.get_frame()
                if frame is not None:
                    logger.info(f"📸 Frame {self.frame_count + 1} obtido, processando...")
                    
                    # Processar frame (simulação de inspeção)
                    result = self._process_frame(frame)
                    
                    # Atualizar contadores
                    self.frame_count += 1
                    if result['approved']:
                        self.approved_count += 1
                    else:
                        self.rejected_count += 1
                    
                    logger.info(f"✅ Frame {self.frame_count} processado: {'Aprovado' if result['approved'] else 'Reprovado'}")
                    
                    # Enviar para WebSocket se necessário
                    self._send_websocket_update(result)
                else:
                    logger.warning("⚠️ Nenhum frame obtido da fonte de imagem")
                
                # Aguardar conforme configuração de trigger
                if trigger_type == 'continuous':
                    # Modo contínuo: usar intervalo configurado
                    interval_ms = self.vm.trigger_config.get('interval_ms', 500)
                    time.sleep(interval_ms / 1000.0)
                elif trigger_type == 'trigger':
                    # Modo gatilho: aguardar próximo trigger
                    time.sleep(0.1)  # Verificação rápida para novos triggers
                
            except Exception as e:
                error_message = f"Erro crítico no loop de processamento: {str(e)}"
                logger.error(f"❌ {error_message}")
                
                # Mudar status da VM para error e parar processamento
                self.vm.set_error(error_message)
                
                # Parar o processador
                self.running = False
                
                logger.error("🛑 Processador parado devido a erro crítico")
                break
    
    def _process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Processa um frame usando sistema de ferramentas ou simulação"""
        try:
            start_time = time.time()
            
            # Verificar se há processador de ferramentas disponível
            if hasattr(self.vm, 'inspection_processor') and self.vm.inspection_processor:
                # Usar sistema de ferramentas
                logger.info("🔧 Processando frame com sistema de ferramentas...")
                inspection_result = self.vm.inspection_processor.process_inspection(frame)
                
                # Extrair resultado de aprovação
                overall_pass = inspection_result.get('inspection_summary', {}).get('overall_pass', True)
                approved = overall_pass
                
                # Calcular tempo total
                total_time = (time.time() - start_time) * 1000
                
                # Enviar resultado completo via WebSocket
                self._send_inspection_result(inspection_result)
                
                return {
                    'approved': approved,
                    'processing_time_ms': total_time,
                    'inspection_result': inspection_result
                }
            else:
                # Fallback para simulação (comportamento anterior)
                logger.info("🎲 Processando frame com simulação (sem ferramentas)...")
                processing_time = np.random.uniform(10, 50)
                time.sleep(processing_time / 1000.0)
                
                approved = np.random.choice([True, False], p=[0.8, 0.2])
                total_time = (time.time() - start_time) * 1000
                
                return {
                    'approved': approved,
                'processing_time_ms': int(total_time),
                'frame_shape': frame.shape,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_message = f"Erro ao processar frame: {str(e)}"
            logger.error(f"❌ {error_message}")
            # Re-raise para ser capturado pelo _processing_loop
            raise Exception(error_message)
    
    def _send_websocket_update(self, result: Dict[str, Any]):
        """Envia atualização para WebSocket (limitado a 1 por segundo)"""
        # Verificar se há erro ativo
        if self.vm.status == 'error':
            logger.warning("⚠️ Não enviando WebSocket devido a erro ativo")
            return
            
        current_time = time.time()
        
        if current_time - self.last_websocket_update >= self.websocket_update_interval:
            try:
                # Preparar dados para WebSocket
                source_type = self.vm.image_source.source_type if self.vm.image_source else 'none'
                
                # Extrair timestamp baseado no tipo de resultado
                if 'timestamp' in result:
                    # Resultado do sistema antigo (simulação)
                    timestamp = result['timestamp']
                elif 'inspection_result' in result and 'timestamp' in result['inspection_result']:
                    # Resultado do sistema de ferramentas
                    timestamp = result['inspection_result']['timestamp']
                else:
                    # Fallback: usar timestamp atual
                    timestamp = datetime.now().isoformat()
                
                # Extrair informações baseadas no tipo de resultado
                if 'inspection_result' in result:
                    # Sistema de ferramentas - usar dados completos da inspeção
                    inspection_summary = result['inspection_result']['inspection_summary']
                    total_time = inspection_summary.get('total_processing_time_ms', 0)
                    tools_config = self.vm.inspection_config.get('tools', [])
                    tools_results = result['inspection_result']['tool_results']
                else:
                    # Sistema antigo (simulação) - usar dados básicos
                    total_time = result.get('processing_time_ms', 0)
                    tools_config = []
                    tools_results = []
                
                websocket_data = {
                    'aprovados': self.approved_count,
                    'reprovados': self.rejected_count,
                    'frame': self.frame_count,
                    'time': f"{total_time:.2f}ms",
                    'tools': tools_config,  # JSON de configuração da inspeção
                    'result': tools_results,  # Lista resultante de todos os processos das tools
                    'timestamp': timestamp,
                    'source_type': source_type,
                    'mode': self.vm.mode
                }
                
                logger.info(f"📡 Enviando para WebSocket: {websocket_data}")
                
                # Enviar para todos os clientes conectados
                self.socketio.emit('test_result', websocket_data, namespace='/')
                
                self.last_websocket_update = current_time
                logger.info(f"✅ WebSocket atualizado com sucesso: Frame {self.frame_count}")
                
            except Exception as e:
                error_message = f"Erro ao enviar para WebSocket: {str(e)}"
                logger.error(f"❌ {error_message}")
                # Mudar status da VM para error
                self.vm.set_error(error_message)
                # Parar o processador
                self.running = False
        else:
            logger.debug(f"⏳ WebSocket rate-limited: {self.websocket_update_interval - (current_time - self.last_websocket_update):.2f}s restantes")
    
    def _send_inspection_result(self, inspection_result: Dict[str, Any]):
        """Envia resultado completo de inspeção via WebSocket"""
        try:
            # Enviar resultado de inspeção via WebSocket
            self.socketio.emit('inspection_result', {
                'status': 'success',
                'inspection_result': inspection_result,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("📡 Resultado de inspeção enviado via WebSocket")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar resultado de inspeção via WebSocket: {str(e)}")

class VisionMachine:
    """Classe principal da máquina de visão computacional"""
    
    def __init__(self, machine_id: str, django_url: str, config_file: str = None):
        self.machine_id = machine_id
        self.django_url = django_url
        # Usar vm_config.json como nome padrão
        self.config_file = config_file or "vm_config.json"
        
        # Carregar configurações salvas ou usar padrões
        self._load_config()
        
        # Inicializar source de imagem com tratamento de erro
        try:
            self.image_source = ImageSource(self.source_config)
            logger.info(f"✅ Source de imagem inicializado com sucesso")
        except Exception as e:
            error_message = f"Erro ao inicializar source de imagem: {str(e)}"
            logger.error(f"❌ {error_message}")
            # Definir erro mas permitir que a VM continue
            self.set_error(error_message)
            # Criar um source vazio para evitar quebra
            self.image_source = None
            logger.warning("⚠️ VM inicializada com erro, mas servidor continuará funcionando")
        
        # Inicializar processador de inspeção com ferramentas
        self.inspection_processor = None
        if TOOLS_AVAILABLE and hasattr(self, 'inspection_config') and self.inspection_config.get('tools'):
            try:
                self.inspection_processor = InspectionProcessor(self.inspection_config)
                logger.info(f"✅ Processador de ferramentas inicializado com {len(self.inspection_processor.tools)} ferramentas")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar processador de ferramentas: {str(e)}")
                self.inspection_processor = None
        else:
            logger.info("ℹ️ Processador de ferramentas não configurado ou não disponível")
        
        logger.info(f"VM {machine_id} inicializada em modo {self.mode}")
        
        # Verificar se deve iniciar inspeção automaticamente
        self._check_auto_start_inspection()

    def _load_config(self):
        """Carrega configurações do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                # Arquivo existe: ler configurações salvas
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Carregar configurações salvas
                self.status = config.get('status', 'idle')
                self.mode = config.get('mode', 'TESTE')
                self.connection_status = config.get('connection_status', 'disconnected')
                self.inspection_config = config.get('inspection_config', {})
                self.error_msg = config.get('error_msg', '')  # Carregar mensagem de erro
                self.source_config = config.get('source_config', {
                    "type": "pasta",
                    "camera_id": 0,
                    "resolution": (640, 480),
                    "fps": 30,
                    "folder_path": "./test_images",
                    "rtsp_url": ""
                })
                self.trigger_config = config.get('trigger_config', {
                    "type": "continuous",
                    "interval_ms": 500  # 500ms para processamento mais rápido
                })
                
                logger.info(f"Configurações carregadas de {self.config_file}")
            else:
                # Arquivo não existe: usar configurações padrão e salvar
                logger.info(f"Arquivo {self.config_file} não encontrado, usando configurações padrão")
                self._set_default_config()
                # Salvar configurações padrão no arquivo
                self.save_config()
                logger.info(f"Configurações padrão salvas em {self.config_file}")
                
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {str(e)}")
            # Em caso de erro, usar configurações padrão
            self._set_default_config()
            logger.info("Usando configurações padrão devido a erro")

    def _set_default_config(self):
        """Define configurações padrão"""
        self.status = "idle"
        self.mode = "TESTE"
        self.connection_status = "disconnected"
        self.inspection_config = {}
        self.error_msg = ""  # Mensagem de erro
        
        self.source_config = {
            "type": "pasta",
            "camera_id": 0,
            "resolution": (640, 480),
            "fps": 30,
            "folder_path": "./test_images",
            "rtsp_url": ""
        }
        
        self.trigger_config = {
            "type": "continuous",  # "continuous" ou "trigger"
            "interval_ms": 500    # 500ms para processamento mais rápido (apenas modo contínuo)
        }

    def save_config(self):
        """Salva configurações atuais no arquivo JSON"""
        try:
            config = {
                'machine_id': self.machine_id,
                'django_url': self.django_url,
                'status': self.status,
                'mode': self.mode,
                'connection_status': self.connection_status,
                'inspection_config': self.inspection_config,
                'source_config': self.source_config,
                'trigger_config': self.trigger_config,
                'error_msg': self.error_msg,  # Salvar mensagem de erro
                'last_saved': datetime.utcnow().isoformat()
            }
            
            # Garantir que o diretório existe
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configurações salvas em {self.config_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações em {self.config_file}: {str(e)}")

    def update_source_config(self, new_config: Dict[str, Any]):
        """Atualiza configuração de source e salva"""
        try:
            # Atualizar configuração
            self.source_config.update(new_config)
            
            # Atualizar source de imagem se existir
            if hasattr(self, 'image_source') and self.image_source is not None:
                try:
                    self.image_source.update_config(self.source_config)
                    logger.info("✅ Source de imagem atualizado com sucesso")
                except Exception as update_error:
                    logger.warning(f"⚠️ Erro ao atualizar source existente, tentando recriar: {str(update_error)}")
                    # Tentar recriar o source
                    try:
                        self.image_source = ImageSource(self.source_config)
                        logger.info("✅ Source de imagem recriado com sucesso")
                    except Exception as recreate_error:
                        error_message = f"Erro ao recriar source de imagem: {str(recreate_error)}"
                        logger.error(f"❌ {error_message}")
                        self.set_error(error_message)
                        raise Exception(error_message)
            else:
                # Tentar criar novo source se não existir
                try:
                    self.image_source = ImageSource(self.source_config)
                    logger.info("✅ Novo source de imagem criado com sucesso")
                except Exception as source_error:
                    error_message = f"Erro ao criar source de imagem: {str(source_error)}"
                    logger.error(f"❌ {error_message}")
                    self.set_error(error_message)
                    raise Exception(error_message)
            
            # Sempre salvar após atualização
            self.save_config()
            logger.info("Configuração de source atualizada e salva")
            
            # Limpar erro se a configuração foi bem-sucedida
            if self.error_msg:
                self.clear_error()
                
        except Exception as e:
            error_message = f"Erro ao configurar source: {str(e)}"
            logger.error(error_message)
            self.set_error(error_message)
            raise  # Re-raise para que a API retorne o erro

    def update_trigger_config(self, new_config: Dict[str, Any]):
        """Atualiza configuração de trigger e salva"""
        try:
            # Validar configuração de trigger
            self._validate_trigger_config(new_config)
            
            # Atualizar configuração
            self.trigger_config.update(new_config)
            
            # Sempre salvar após atualização
            self.save_config()
            logger.info("Configuração de trigger atualizada e salva")
            
        except Exception as e:
            error_message = f"Erro ao atualizar configuração de trigger: {str(e)}"
            logger.error(error_message)
            raise Exception(error_message)
    
    def _validate_trigger_config(self, config: Dict[str, Any]):
        """Valida configuração de trigger"""
        trigger_type = config.get('type')
        
        if trigger_type not in ['continuous', 'trigger']:
            raise ValueError(f"Tipo de trigger inválido: {trigger_type}. Deve ser 'continuous' ou 'trigger'")
        
        if trigger_type == 'continuous':
            interval_ms = config.get('interval_ms', 100)
            if interval_ms < 100:  # Mínimo de 100ms para evitar sobrecarga
                raise ValueError(f"Intervalo muito baixo para modo contínuo: {interval_ms}ms. Mínimo: 100ms")
        
        logger.info(f"✅ Configuração de trigger válida: tipo={trigger_type}")

    def update_inspection_config(self, new_config: Dict[str, Any]):
        """Atualiza configuração de inspeção e salva"""
        # Atualizar configuração
        self.inspection_config.update(new_config)
        
        # Recriar inspection_processor com nova configuração
        if TOOLS_AVAILABLE and self.inspection_config.get('tools'):
            try:
                self.inspection_processor = InspectionProcessor(self.inspection_config)
                logger.info(f"✅ Processador de ferramentas recriado com {len(self.inspection_processor.tools)} ferramentas")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao recriar processador de ferramentas: {str(e)}")
                self.inspection_processor = None
        else:
            logger.info("ℹ️ Processador de ferramentas não configurado ou não disponível")
            self.inspection_processor = None
        
        # Sempre salvar após atualização
        self.save_config()
        logger.info("Configuração de inspeção atualizada e salva")

    def change_mode(self, new_mode: str):
        """Muda o modo de operação e salva"""
        if new_mode in ['TESTE', 'RUN']:
            self.mode = new_mode
            self.status = 'idle'
            # Limpar erro ao mudar modo
            self.error_msg = ""
            # Sempre salvar após mudança de modo
            self.save_config()
            logger.info(f"Modo alterado para: {new_mode} e configurações salvas")
            return True
        else:
            logger.warning(f"Modo inválido: {new_mode}")
            return False
    
    def set_error(self, error_message: str):
        """Define uma mensagem de erro e salva"""
        self.error_msg = error_message
        self.status = 'error'
        self.save_config()
        logger.error(f"Erro definido: {error_message}")
    
    def clear_error(self):
        """Limpa o erro e retorna para status idle"""
        if self.error_msg:
            old_error = self.error_msg
            self.error_msg = ""
            self.status = 'idle'
            self.save_config()
            logger.info(f"Erro limpo: {old_error}")
            return True
        return False
    
    def _check_auto_start_inspection(self):
        """Verifica se deve iniciar inspeção automaticamente baseado no status salvo"""
        if self.status == 'running':
            logger.info("🚀 Status 'running' detectado, preparando para iniciar inspeção automaticamente...")
            
            # Verificar se image_source está disponível ou pode ser recriado
            if not hasattr(self, 'image_source') or self.image_source is None:
                logger.info("🔄 Source de imagem não disponível, tentando recriar para auto-start...")
                try:
                    self.image_source = ImageSource(self.source_config)
                    logger.info("✅ Source de imagem recriado com sucesso para auto-start")
                    # Limpar erro se existir
                    if self.error_msg:
                        self.clear_error()
                except Exception as source_error:
                    logger.warning(f"⚠️ Não é possível iniciar inspeção automática: erro ao recriar source: {str(source_error)}")
                    self.status = 'idle'  # Voltar para idle se não puder iniciar
                    self.save_config()
                    return
            
            # Verificar se está em modo TESTE
            if self.mode == 'TESTE':
                logger.info("🧪 Modo TESTE detectado, inspeção será iniciada automaticamente")
                # A inspeção será iniciada pelo FlaskVisionServer após inicialização completa
            else:
                logger.info(f"⚠️ Modo atual não é TESTE ({self.mode}), inspeção não será iniciada automaticamente")
                self.status = 'idle'  # Voltar para idle se não for modo teste
                self.save_config()

class FlaskVisionServer:
    """Servidor Flask para a VM de visão computacional"""
    
    def __init__(self, machine_id: str = "vm_default", django_url: str = "http://localhost:8000", config_file: str = None):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'vm_secret_key_change_in_production'
        
        # Configuração CORS
        CORS(self.app)
        
        # SocketIO para WebSocket
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False,
            async_mode='threading'
        )
        
        # Instância da VM
        self.vm = VisionMachine(machine_id, django_url, config_file)
        
        # Processador de modo teste
        self.test_processor = TestModeProcessor(self.vm, self.socketio)
        
        # Configurar handlers de shutdown
        self._setup_shutdown_handlers()
        
        # Configurar rotas
        self._setup_routes()
        self._setup_socketio_events()
        
        logger.info(f"Servidor Flask VM inicializado para {machine_id}")
        
        # Verificar se deve iniciar inspeção automaticamente
        self._check_auto_start_inspection()

    def _setup_shutdown_handlers(self):
        """Configura handlers para shutdown graceful"""
        def signal_handler(signum, frame):
            logger.info(f"Recebido sinal {signum}, salvando configurações...")
            try:
                # Parar processador de teste
                self.test_processor.stop()
                # Sempre salvar configurações antes de sair
                self.vm.save_config()
                logger.info("Configurações salvas. Encerrando...")
            except Exception as e:
                logger.error(f"Erro ao salvar configurações: {str(e)}")
            finally:
                os._exit(0)
        
        # Registrar handlers para diferentes sinais
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Kill
        
        # Registrar função para ser chamada na saída
        atexit.register(self._cleanup)
        
        logger.info("Handlers de shutdown configurados")
    
    def _check_auto_start_inspection(self):
        """Verifica se deve iniciar inspeção automaticamente após inicialização completa"""
        if self.vm.status == 'running' and self.vm.mode == 'TESTE':
            logger.info("🚀 Iniciando inspeção automática após inicialização...")
            
            # Verificar se image_source está disponível antes de iniciar
            if not hasattr(self.vm, 'image_source') or self.vm.image_source is None:
                logger.warning("⚠️ Source de imagem não disponível para auto-start, tentando recriar...")
                try:
                    self.vm.image_source = ImageSource(self.vm.source_config)
                    logger.info("✅ Source de imagem recriado com sucesso para auto-start")
                    # Limpar erro se existir
                    if self.vm.error_msg:
                        self.vm.clear_error()
                except Exception as source_error:
                    logger.error(f"❌ Erro ao recriar source para auto-start: {str(source_error)}")
                    self.vm.set_error(f"Erro ao recriar source para auto-start: {str(source_error)}")
                    self.vm.status = 'idle'
                    self.vm.save_config()
                    return
            
            # Aguardar um pouco para garantir que tudo está pronto
            import time
            time.sleep(1)
            
            try:
                # Iniciar processador de teste
                self.test_processor.start()
                logger.info("✅ Inspeção automática iniciada com sucesso")
                
                # Confirmar que o status está correto
                if self.vm.status != 'running':
                    self.vm.status = 'running'
                    self.vm.save_config()
                    logger.info("✅ Status confirmado como 'running'")
                    
            except Exception as e:
                error_message = f"Erro ao iniciar inspeção automática: {str(e)}"
                logger.error(f"❌ {error_message}")
                self.vm.set_error(error_message)
                self.vm.status = 'idle'
                self.vm.save_config()
        else:
            logger.info("ℹ️ Inspeção automática não necessária")
    
    def _cleanup(self):
        """Limpeza antes de sair"""
        try:
            # Parar processador de teste
            self.test_processor.stop()
            # Sempre salvar configurações antes de sair
            self.vm.save_config()
            logger.info("Configurações salvas durante limpeza")
        except Exception as e:
            logger.error(f"Erro durante limpeza: {str(e)}")

    def _setup_routes(self):
        """Configura as rotas REST da API"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Retorna o status atual da VM"""
            # Informações adicionais sobre trigger
            trigger_info = {
                "type": self.vm.trigger_config.get('type', 'continuous'),
                "interval_ms": self.vm.trigger_config.get('interval_ms', 500),
                "waiting_for_trigger": False
            }
            
            # Se estiver em modo gatilho e rodando, verificar se está aguardando
            if (self.vm.trigger_config.get('type') == 'trigger' and 
                self.vm.status == 'running' and 
                hasattr(self.test_processor, 'trigger_requested')):
                trigger_info["waiting_for_trigger"] = not self.test_processor.trigger_requested
            
            return jsonify({
                "machine_id": self.vm.machine_id,
                "status": self.vm.status,
                "mode": self.vm.mode,
                "connection_status": self.vm.connection_status,
                "error_msg": self.vm.error_msg,  # Incluir mensagem de erro
                "timestamp": datetime.utcnow().isoformat(),
                "source_config": self.vm.source_config,
                "trigger_config": self.vm.trigger_config,
                "trigger_info": trigger_info,
                "source_available": self.vm.image_source is not None
            })
        
        @self.app.route('/api/control', methods=['POST'])
        def control():
            """Endpoint para controle da VM pelo orquestrador"""
            try:
                data = request.get_json()
                command = data.get('command')
                params = data.get('params', {})
                
                if command == 'change_mode':
                    new_mode = params.get('mode')
                    if new_mode in ['TESTE', 'RUN']:
                        self.vm.change_mode(new_mode)
                        return jsonify({"success": True, "new_mode": new_mode})
                    else:
                        return jsonify({"success": False, "error": "Modo inválido"}), 400
                
                elif command == 'update_inspection_config':
                    self.vm.update_inspection_config(params.get('config', {}))
                    return jsonify({"success": True})
                
                elif command == 'start_inspection':
                    logger.info(f"🚀 Comando start_inspection recebido, modo atual: {self.vm.mode}")
                    
                    # Verificar se há erro ativo
                    if self.vm.status == 'error':
                        error_msg = "Não é possível iniciar inspeção com erro ativo"
                        logger.error(f"❌ {error_msg}")
                        return jsonify({"success": False, "error": error_msg}), 400
                    
                    # Verificar se image_source está disponível ou pode ser recriado
                    if not hasattr(self.vm, 'image_source') or self.vm.image_source is None:
                        logger.info("🔄 Source de imagem não disponível, tentando recriar...")
                        try:
                            self.vm.image_source = ImageSource(self.vm.source_config)
                            logger.info("✅ Source de imagem recriado com sucesso")
                            # Limpar erro se existir
                            if self.vm.error_msg:
                                self.vm.clear_error()
                        except Exception as source_error:
                            error_msg = f"Erro ao recriar source de imagem: {str(source_error)}"
                            logger.error(f"❌ {error_msg}")
                            return jsonify({"success": False, "error": error_msg}), 400
                    
                    # Verificar se já está rodando
                    if self.vm.status == 'running':
                        logger.info("ℹ️ Inspeção já está rodando")
                        return jsonify({"success": True, "message": "Inspeção já está rodando"})
                    
                    self.vm.status = 'running'
                    # Iniciar processador de teste se estiver em modo teste
                    if self.vm.mode == 'TESTE':
                        logger.info("🧪 Modo TESTE detectado, iniciando processador...")
                        self.test_processor.start()
                        logger.info("✅ Processador de teste iniciado com sucesso")
                    else:
                        logger.info(f"⚠️ Modo atual não é TESTE: {self.vm.mode}")
                    logger.info("Inspeção iniciada")
                    return jsonify({"success": True})
                
                elif command == 'stop_inspection':
                    logger.info("🛑 Comando stop_inspection recebido")
                    self.vm.status = 'idle'
                    # Parar processador de teste
                    self.test_processor.stop()
                    logger.info("Inspeção parada")
                    return jsonify({"success": True})
                
                elif command == 'trigger':
                    logger.info("🔘 Comando trigger recebido")
                    
                    # Verificar se está em modo gatilho
                    if self.vm.trigger_config.get('type') != 'trigger':
                        error_msg = "Comando trigger só é válido quando trigger_config.type = 'trigger'"
                        logger.warning(f"⚠️ {error_msg}")
                        return jsonify({"success": False, "error": error_msg}), 400
                    
                    # Verificar se inspeção está rodando
                    if self.vm.status != 'running':
                        error_msg = "Comando trigger só é válido quando inspeção está rodando"
                        logger.warning(f"⚠️ {error_msg}")
                        return jsonify({"success": False, "error": error_msg}), 400
                    
                    # Solicitar trigger no processador
                    self.test_processor.request_trigger()
                    logger.info("✅ Trigger solicitado com sucesso")
                    return jsonify({"success": True, "message": "Trigger solicitado"})
                
                else:
                    return jsonify({"success": False, "error": "Comando não reconhecido"}), 400
                    
            except Exception as e:
                logger.error(f"Erro no controle: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/source_config', methods=['GET', 'PUT'])
        def source_config():
            """Gerencia configuração local do source de imagens"""
            if request.method == 'GET':
                return jsonify(self.vm.source_config)
            else:
                try:
                    data = request.get_json()
                    self.vm.update_source_config(data)
                    logger.info("Configuração de source atualizada")
                    return jsonify({"success": True})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/trigger_config', methods=['GET', 'PUT'])
        def trigger_config():
            """Gerencia configuração local do trigger"""
            if request.method == 'GET':
                return jsonify(self.vm.trigger_config)
            else:
                try:
                    data = request.get_json()
                    self.vm.update_trigger_config(data)
                    logger.info("Configuração de trigger atualizada")
                    return jsonify({"success": True})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/inspection_config', methods=['GET', 'PUT'])
        def inspection_config():
            """Gerencia configuração local de inspeção"""
            if request.method == 'GET':
                return jsonify(self.vm.inspection_config)
            else:
                try:
                    data = request.get_json()
                    self.vm.update_inspection_config(data)
                    logger.info("Configuração de inspeção atualizada")
                    return jsonify({"success": True})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/error', methods=['GET', 'POST', 'DELETE'])
        def error_management():
            """Gerencia mensagens de erro da VM"""
            if request.method == 'GET':
                return jsonify({
                    "status": self.vm.status,
                    "error_msg": self.vm.error_msg
                })
            elif request.method == 'POST':
                try:
                    data = request.get_json()
                    error_message = data.get('error_msg', '')
                    if error_message:
                        self.vm.set_error(error_message)
                        return jsonify({"success": True, "message": "Erro definido"})
                    else:
                        return jsonify({"success": False, "error": "Mensagem de erro não fornecida"}), 400
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500
            elif request.method == 'DELETE':
                try:
                    if self.vm.clear_error():
                        return jsonify({"success": True, "message": "Erro limpo"})
                    else:
                        return jsonify({"success": False, "error": "Nenhum erro para limpar"}), 404
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500

    def _setup_socketio_events(self):
        """Configura eventos do SocketIO/WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Cliente conectado via WebSocket"""
            logger.info(f"Cliente WebSocket conectado: {request.sid}")
            emit('connected', {
                'machine_id': self.vm.machine_id,
                'status': self.vm.status,
                'mode': self.vm.mode
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Cliente desconectado via WebSocket"""
            logger.info(f"Cliente WebSocket desconectado: {request.sid}")
        
        @self.socketio.on('request_status')
        def handle_status_request():
            """Cliente solicita status atual"""
            emit('status_update', {
                'machine_id': self.vm.machine_id,
                'status': self.vm.status,
                'mode': self.vm.mode,
                'timestamp': datetime.utcnow().isoformat()
            })

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Executa o servidor Flask"""
        logger.info(f"Iniciando servidor VM na porta {port}")
        
        # Sempre usar SocketIO para garantir WebSocket
        self.socketio.run(
            self.app, 
            host=host, 
            port=port, 
            debug=debug,
            allow_unsafe_werkzeug=True
        )

def main():
    """Função principal para execução da VM"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AnalyticLens Vision Machine')
    parser.add_argument('--machine-id', default='vm_001', help='ID único da máquina')
    parser.add_argument('--django-url', default='http://localhost:8000', help='URL do Django orquestrador')
    parser.add_argument('--config-file', help='Arquivo de configuração personalizado')
    parser.add_argument('--host', default='0.0.0.0', help='Host para bind do servidor')
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    # Criar e executar servidor
    server = FlaskVisionServer(
        machine_id=args.machine_id,
        django_url=args.django_url,
        config_file=args.config_file
    )
    
    try:
        server.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao executar servidor: {str(e)}")

if __name__ == '__main__':
    main()
