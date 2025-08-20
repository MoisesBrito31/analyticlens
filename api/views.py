from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import json

# DRF imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# Local imports
from .models import VirtualMachine
from .serializers import (
    VirtualMachineListSerializer,
    VirtualMachineSerializer,
    VirtualMachineCreateSerializer,
    VirtualMachineUpdateSerializer,
    VMActionSerializer,
    VMSearchSerializer,
    VMStatusSummarySerializer
)
from .protocolo import execute_command, refresh_all_vm_statuses, ProtocoloVM


def home_view(request):
    """View simples para a página inicial da API"""
    return JsonResponse({
        'message': 'API AnalyticLens funcionando!',
        'endpoints': {
            'vms': '/api/vms',
            'vm_detail': '/api/vms/{id}',
            'vm_action': '/api/vms/{id}/action',
            'vm_status_summary': '/api/vms/status/summary'
        }
    })


def health_check(request):
    """Health check simples da API"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat()
    })


class VMListCreate(APIView):
    """Lista todas as VMs ou cria uma nova - VERSÃO SIMPLIFICADA"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Atualizar status de todas as VMs antes de responder (sem rebaixar nem marcar offline em erro)
            refresh_all_vm_statuses()
            # Validar parâmetros de busca
            search_serializer = VMSearchSerializer(data=request.GET)
            if not search_serializer.is_valid():
                return Response(
                    {'erro': 'Parâmetros de busca inválidos', 'details': search_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parâmetros validados
            status_filter = search_serializer.validated_data.get('status', '')
            mode = search_serializer.validated_data.get('mode', '')
            connection_status = search_serializer.validated_data.get('connection_status', '')
            search = search_serializer.validated_data.get('search', '')
            
            # Query base
            queryset = VirtualMachine.objects.filter(is_active=True)
            
            # Aplicar filtros
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if mode:
                queryset = queryset.filter(mode=mode)
            if connection_status:
                queryset = queryset.filter(connection_status=connection_status)
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(machine_id__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # Serializar dados
            serializer = VirtualMachineListSerializer(queryset, many=True)
            
            response_data = {
                'vms': serializer.data,
                'total_count': queryset.count()
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'erro': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            # Atualizar status de todas as VMs antes de criar nova
            refresh_all_vm_statuses()
            serializer = VirtualMachineCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'erro': 'Dados inválidos', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Criar VM associada ao usuário
            vm = serializer.save(owner=request.user)
            
            return Response({
                'message': 'VM criada com sucesso',
                'vm_id': vm.id,
                'machine_id': vm.machine_id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'erro': f'Erro ao criar VM: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VMDetail(APIView):
    """Obtém, atualiza ou remove uma VM específica - VERSÃO SIMPLIFICADA"""
    permission_classes = [IsAuthenticated]

    def get_object(self, vm_id):
        try:
            return VirtualMachine.objects.get(id=vm_id, is_active=True)
        except VirtualMachine.DoesNotExist:
            return None

    def get(self, request, vm_id):
        # Atualiza status desta VM e reflete imediatamente no banco
        vm = self.get_object(vm_id)
        if vm:
            ProtocoloVM().update_status(vm, mark_offline_on_error=True)
        if not vm:
            return Response(
                {'erro': 'VM não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = VirtualMachineSerializer(vm)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, vm_id):
        # Atualizar status de todas as VMs antes de atualizar (sem rebaixar nem marcar offline em erro)
        refresh_all_vm_statuses()
        vm = self.get_object(vm_id)
        if not vm:
            return Response(
                {'erro': 'VM não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = VirtualMachineUpdateSerializer(vm, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {'erro': 'Dados inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return Response({
            'message': 'VM atualizada com sucesso'
        }, status=status.HTTP_200_OK)

    def delete(self, request, vm_id):
        # Atualizar status de todas as VMs antes de remover (sem rebaixar nem marcar offline em erro)
        refresh_all_vm_statuses()
        vm = self.get_object(vm_id)
        if not vm:
            return Response(
                {'erro': 'VM não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remoção definitiva (hard delete)
        vm.delete()
        return Response({
            'message': 'VM apagada com sucesso'
        }, status=status.HTTP_200_OK)


class VMAction(APIView):
    """Executa ações básicas na VM - VERSÃO SIMPLIFICADA"""
    permission_classes = [IsAuthenticated]

    def get_object(self, vm_id):
        try:
            return VirtualMachine.objects.get(id=vm_id, is_active=True)
        except VirtualMachine.DoesNotExist:
            return None

    def post(self, request, vm_id):
        try:
            vm = self.get_object(vm_id)
            if not vm:
                return Response(
                    {'erro': 'VM não encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validar ação (ainda usamos o serializer para validar o campo 'action')
            action_serializer = VMActionSerializer(data=request.data)
            if not action_serializer.is_valid():
                return Response(
                    {'erro': 'Ação inválida', 'details': action_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            action = action_serializer.validated_data['action']
            params = {k: v for k, v in request.data.items() if k != 'action'}

            # Executar comando e, ao final, forçar atualização de status desta VM
            resultado = execute_command(vm, action, params)
            ProtocoloVM().update_status(vm, mark_offline_on_error=True)
            if not resultado.get('ok'):
                return Response(
                    {'erro': resultado.get('error', 'Falha ao executar comando')},
                    status=status.HTTP_400_BAD_REQUEST
                )

            mensagem_por_acao = {
                'start': 'VM iniciada com sucesso',
                'stop': 'VM parada com sucesso',
                'restart': 'VM reiniciada com sucesso',
                'trigger': 'Trigger executado com sucesso',
                'get_status': 'Status obtido com sucesso',
            }

            return Response({
                'message': mensagem_por_acao.get(action, 'Ação executada com sucesso'),
                **{k: v for k, v in resultado.items() if k != 'ok'}
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'erro': f'Erro ao executar ação: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VMStatusSummary(APIView):
    """Retorna um resumo simples do status de todas as VMs"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            vms = VirtualMachine.objects.filter(is_active=True)
            
            # Contadores simples
            status_counts = {}
            connection_counts = {}
            mode_counts = {}
            
            for vm in vms:
                # Status
                vm_status = vm.status
                status_counts[vm_status] = status_counts.get(vm_status, 0) + 1
                
                # Connection status
                conn_status = vm.connection_status
                connection_counts[conn_status] = connection_counts.get(conn_status, 0) + 1
                
                # Mode
                mode = vm.mode
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
            
            # VMs com erro (apenas IDs e nomes)
            error_vms = vms.filter(status='error')[:5]
            error_vms_data = []
            for vm in error_vms:
                error_vms_data.append({
                    'id': vm.id,
                    'name': vm.name,
                    'error_message': vm.error_message,
                    'last_heartbeat': vm.last_heartbeat.isoformat() if vm.last_heartbeat else None,
                })
            
            # VMs offline há muito tempo
            offline_threshold = timezone.now() - timedelta(hours=1)
            offline_vms = vms.filter(
                last_heartbeat__lt=offline_threshold
            ).exclude(status='offline')[:5]
            
            offline_vms_data = []
            for vm in offline_vms:
                offline_vms_data.append({
                    'id': vm.id,
                    'name': vm.name,
                    'last_heartbeat': vm.last_heartbeat.isoformat() if vm.last_heartbeat else None,
                })
            
            summary = {
                'total_vms': vms.count(),
                'status_counts': status_counts,
                'connection_counts': connection_counts,
                'mode_counts': mode_counts,
                'error_vms': error_vms_data,
                'offline_vms': offline_vms_data,
                'timestamp': timezone.now().isoformat(),
            }
            
            return Response(summary, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'erro': f'Erro ao gerar resumo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
