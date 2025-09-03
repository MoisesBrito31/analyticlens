from typing import Dict, Any, Optional
import requests
from django.utils import timezone
from urllib.parse import urlparse

from .models import VirtualMachine


class ProtocoloVM:
    """
    Responsável por orquestrar a comunicação com as VMs via HTTP (REST).
    Integra com o servidor Flask da VM exposto em vision_machine/vm.py
    """

    def __init__(self, request_timeout_seconds: float = 2.0):
        self.request_timeout_seconds = request_timeout_seconds
        # Controle interno: se deve atualizar DB em erro durante um comando
        self._update_db_on_error = True

    def _base_url(self, vm: VirtualMachine) -> str:
        """
        Resolve a URL base da VM a partir de múltiplas origens de configuração.
        Prioridade:
        1) inspection_config.vm_api_base (URL completa, ex: http://10.0.0.2:6001)
        2) inspection_config.vm_api_host + vm_api_port + vm_api_scheme
        3) vm.ip_address como URL completa (http[s]://host:port)
        4) vm.ip_address + vm.port usando http
        5) 127.0.0.1:5000
        """
        # 1) URL completa na configuração
        vm_api_base = None
        try:
            vm_api_base = (vm.inspection_config or {}).get('vm_api_base')
        except Exception:
            vm_api_base = None
        if vm_api_base:
            return vm_api_base.rstrip('/')

        # 2) Host/Port/Scheme na configuração
        cfg = (vm.inspection_config or {})
        api_host = cfg.get('vm_api_host')
        api_port = cfg.get('vm_api_port')
        api_scheme = cfg.get('vm_api_scheme', 'http')
        if api_host:
            try:
                port = int(api_port) if api_port is not None else (vm.port or 5000)
            except (TypeError, ValueError):
                port = vm.port or 5000
            return f"{api_scheme}://{api_host}:{port}"

        # 3) ip_address já como URL completa
        if vm.ip_address and isinstance(vm.ip_address, str) and vm.ip_address.startswith(('http://', 'https://')):
            parsed = urlparse(vm.ip_address)
            if parsed.scheme and parsed.netloc:
                return vm.ip_address.rstrip('/')

        # 4) ip + port
        if vm.ip_address:
            return f"http://{vm.ip_address}:{vm.port or 5000}"

        # 5) fallback
        return "http://127.0.0.1:5000"

    def _map_status_from_vm(self, vm_status_value: Optional[str]) -> str:
        # VM pode reportar 'running', 'idle', 'error'. Mapeamos para nosso modelo
        if vm_status_value == 'running':
            return 'running'
        if vm_status_value == 'error':
            return 'error'
        # idle/None -> treated as stopped
        return 'stopped'

    def _update_db_from_status(self, vm: VirtualMachine, status_payload: Dict[str, Any]) -> None:
        vm_status = status_payload.get('status')
        vm_mode = status_payload.get('mode')
        vm_error = status_payload.get('error_msg')
        vm_connection_status = 'connected'

        mapped_status = self._map_status_from_vm(vm_status)
        # Não rebaixa 'running' para 'stopped' quando vier de refresh em massa (views)
        if self._update_db_on_error is False and vm.status == 'running' and mapped_status == 'stopped':
            new_status = vm.status
        else:
            new_status = mapped_status

        vm.status = new_status
        # Atualizar modo: VM reporta 'TESTE' ou 'RUN'; DB usa 'TESTE' ou 'PRODUCAO'
        if vm_mode in ['TESTE', 'RUN']:
            vm.mode = 'PRODUCAO' if vm_mode == 'RUN' else 'TESTE'
        vm.connection_status = vm_connection_status
        vm.last_heartbeat = timezone.now()
        vm.error_message = vm_error or ''
        vm.save(update_fields=['status', 'mode', 'connection_status', 'last_heartbeat', 'error_message', 'updated_at'])

    def _handle_http_error(self, vm: VirtualMachine, exc: Exception, update_db_on_error: bool) -> Dict[str, Any]:
        # Se for timeout, marcar como OFFLINE apenas quando autorizado a atualizar DB neste fluxo
        is_timeout = isinstance(exc, requests.Timeout) or (hasattr(requests, 'exceptions') and isinstance(exc, requests.exceptions.Timeout))
        if is_timeout and update_db_on_error:
            vm.status = 'offline'
            vm.connection_status = 'disconnected'
            vm.error_message = 'Timeout ao consultar status da VM'
            vm.last_heartbeat = vm.last_heartbeat  # mantém último heartbeat
            vm.save(update_fields=['status', 'connection_status', 'error_message', 'updated_at'])
            return {
                'ok': False,
                'error': 'Timeout ao consultar status da VM'
            }

        # Em outras falhas de comunicação, opcionalmente marcar desconectado
        if update_db_on_error:
            vm.connection_status = 'disconnected'
            vm.error_message = f"Falha de comunicação com a VM: {str(exc)}"
            vm.save(update_fields=['connection_status', 'error_message', 'updated_at'])
        return {
            'ok': False,
            'error': 'Falha de comunicação com a VM'
        }

    def send_command(self, vm: VirtualMachine, command: str, params: Dict[str, Any], *, update_db_on_error: bool = True) -> Dict[str, Any]:
        command = (command or '').strip().lower()
        handlers = {
            'get_status': self._handle_get_status,
            'start': self._handle_start,
            'stop': self._handle_stop,
            'restart': self._handle_restart,
            'trigger': self._handle_trigger,
            'change_mode': self._handle_change_mode,
            'update_source_config': self._handle_update_source_config,
            'update_trigger_config': self._handle_update_trigger_config,
            'update_inspection_config': self._handle_update_inspection_config,
            'config_tool': self._handle_config_tool,
            'delete_tool': self._handle_delete_tool,
        }

        if command not in handlers:
            return {
                'ok': False,
                'error': f'Comando não suportado: {command}'
            }

        # Ajusta flag de erro para este comando
        previous_flag = self._update_db_on_error
        self._update_db_on_error = update_db_on_error
        try:
            return handlers[command](vm, params or {})
        finally:
            # Restaurar flag anterior
            self._update_db_on_error = previous_flag

    # Atualiza status via HTTP GET e reflete no banco
    def update_status(self, vm: VirtualMachine, mark_offline_on_error: bool = True) -> Dict[str, Any]:
        try:
            url = f"{self._base_url(vm)}/api/status"
            res = requests.get(url, timeout=self.request_timeout_seconds)
            res.raise_for_status()
            data = res.json()
            self._update_db_from_status(vm, data)
            return {'ok': True, 'status': vm.status, 'connection_status': vm.connection_status}
        except Exception as e:
            return self._handle_http_error(vm, e, mark_offline_on_error)

    # Handlers HTTP reais
    def _handle_get_status(self, vm: VirtualMachine, _: Dict[str, Any]) -> Dict[str, Any]:
        # Respeitar flag de atualização configurada em send_command
        return self.update_status(vm, self._update_db_on_error)

    def _post_control(self, vm: VirtualMachine, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self._base_url(vm)}/api/control"
        res = requests.post(url, json=payload, timeout=self.request_timeout_seconds)
        res.raise_for_status()
        return res.json()

    def _handle_start(self, vm: VirtualMachine, _: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self._post_control(vm, {"command": "start_inspection", "params": {}})
            # Buscar status após comando (força atualização pelo response)
            return self.update_status(vm, True)
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_stop(self, vm: VirtualMachine, _: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self._post_control(vm, {"command": "stop_inspection", "params": {}})
            return self.update_status(vm, True)
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_restart(self, vm: VirtualMachine, _: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # stop -> start
            self._post_control(vm, {"command": "stop_inspection", "params": {}})
            self._post_control(vm, {"command": "start_inspection", "params": {}})
            return self.update_status(vm, True)
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_trigger(self, vm: VirtualMachine, _: Dict[str, Any]) -> Dict[str, Any]:
        try:
            data = self._post_control(vm, {"command": "trigger", "params": {}})
            # Atualiza heartbeat ao menos
            vm.last_heartbeat = timezone.now()
            vm.save(update_fields=['last_heartbeat', 'updated_at'])
            return {'ok': True, 'message': data.get('message', 'Trigger enviado')}
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_change_mode(self, vm: VirtualMachine, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            mode = params.get('mode')
            # Aceitar modos do domínio do Django: TESTE, PRODUCAO
            if mode not in ['TESTE', 'RUN', 'PRODUCAO']:
                return {'ok': False, 'error': 'Modo inválido'}
            # Mapear PRODUCAO -> RUN para a VM
            vm_mode = 'RUN' if mode == 'PRODUCAO' else mode
            self._post_control(vm, {"command": "change_mode", "params": {"mode": vm_mode}})
            return self._handle_get_status(vm, {})
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_update_source_config(self, vm: VirtualMachine, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # endpoint dedicado em VM: PUT /api/source_config
            url = f"{self._base_url(vm)}/api/source_config"
            res = requests.put(url, json=params, timeout=self.request_timeout_seconds)
            res.raise_for_status()
            return {'ok': True}
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_update_trigger_config(self, vm: VirtualMachine, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            url = f"{self._base_url(vm)}/api/trigger_config"
            res = requests.put(url, json=params, timeout=self.request_timeout_seconds)
            res.raise_for_status()
            return {'ok': True}
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_update_inspection_config(self, vm: VirtualMachine, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            url = f"{self._base_url(vm)}/api/inspection_config"
            res = requests.put(url, json=params.get('config', {}), timeout=self.request_timeout_seconds)
            res.raise_for_status()
            return {'ok': True}
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_config_tool(self, vm: VirtualMachine, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            data = self._post_control(vm, {"command": "config_tool", "params": params})
            return {'ok': True, **data}
        except Exception as e:
            return self._handle_http_error(vm, e, True)

    def _handle_delete_tool(self, vm: VirtualMachine, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            data = self._post_control(vm, {"command": "delete_tool", "params": params})
            return {'ok': True, **data}
        except Exception as e:
            if self.allow_simulation_fallback:
                return {'ok': True}
            return self._handle_http_error(vm, e, True)


def execute_command(vm: VirtualMachine, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    protocolo = ProtocoloVM()
    return protocolo.send_command(vm, command, params)


def refresh_all_vm_statuses():
    """Executa get_status para todas as VMs ativas e atualiza o banco."""
    protocolo = ProtocoloVM()
    for vm in VirtualMachine.objects.filter(is_active=True):
        try:
            protocolo.update_status(vm, mark_offline_on_error=True)
        except Exception:
            # Ignorar falhas individuais para não quebrar a rota
            continue


