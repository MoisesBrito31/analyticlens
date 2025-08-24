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
from .models import (
    VirtualMachine, Inspection, InspectionTool, ToolKind,
    GrayscaleTool, BlurTool, ThresholdTool, MorphologyTool, BlobToolConfig, MathTool
)
from .serializers import (
    VirtualMachineListSerializer,
    VirtualMachineSerializer,
    VirtualMachineCreateSerializer,
    VirtualMachineUpdateSerializer,
    VMActionSerializer,
    VMSearchSerializer,
    VMStatusSummarySerializer,
    SaveInspectionRequestSerializer
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


class SaveInspection(APIView):
    """Cria/atualiza uma inspeção para uma VM a partir do estado atual da VM."""
    permission_classes = [IsAuthenticated]

    def post(self, request, vm_id):
        try:
            # Validar entrada
            body = SaveInspectionRequestSerializer(data=request.data)
            if not body.is_valid():
                return Response({'erro': body.errors}, status=status.HTTP_400_BAD_REQUEST)

            data = body.validated_data
            name = data['name']
            overwrite = data.get('overwrite', False)

            # Buscar VM
            try:
                vm = VirtualMachine.objects.get(id=vm_id, is_active=True)
            except VirtualMachine.DoesNotExist:
                return Response({'erro': 'VM não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            # Upsert de Inspection
            insp = Inspection.objects.filter(vm=vm, name=name).first()
            if insp and not overwrite:
                return Response({'exists': True, 'message': 'Inspeção já existe', 'confirm_overwrite': True}, status=status.HTTP_409_CONFLICT)

            if not insp:
                insp = Inspection(vm=vm, name=name)
            insp.description = f"Importada da VM {vm.machine_id} em {timezone.now().isoformat()}"
            insp.save()

            # Limpar ferramentas existentes se overwrite
            if overwrite:
                insp.tools.all().delete()

            # Ler configuração atual da VM
            cfg = vm.inspection_config or {}
            tools_cfg = cfg.get('tools', []) if isinstance(cfg, dict) else []

            # Se houver payload com último resultado válido, extrair parâmetros úteis
            payload = data.get('payload') or {}
            last_tools = []
            if isinstance(payload, dict):
                # Preferir lista padronizada de resultados 'result'
                if isinstance(payload.get('result'), list):
                    last_tools = payload['result']
                elif isinstance(payload.get('tools'), list):
                    last_tools = payload['tools']

            # Se não houver config na VM, tentar usar tools do payload
            if not tools_cfg and isinstance(payload, dict):
                if isinstance(payload.get('tools'), list):
                    tools_cfg = payload['tools']
                elif isinstance(payload.get('result'), list):
                    # Construir uma configuração mínima a partir dos resultados
                    built = []
                    for i, rt in enumerate(payload['result']):
                        if not isinstance(rt, dict):
                            continue
                        built.append({
                            'id': rt.get('tool_id'),
                            'name': rt.get('tool_name') or f'tool_{i+1}',
                            'type': (rt.get('tool_type') or '').lower(),
                            'ROI': rt.get('ROI') or {},
                            'inspec_pass_fail': bool(rt.get('pass_fail')) if isinstance(rt.get('pass_fail'), bool) else False,
                        })
                    tools_cfg = built

            # Mapear ToolKind por slug
            kinds = {k.slug: k.id for k in ToolKind.objects.all()}

            # Criar tools em ordem
            created = []
            for idx, t in enumerate(tools_cfg):
                # Unificar campos possíveis entre config e resultado
                t_type = str((t.get('type') or t.get('tool_type') or '')).lower()
                t_name = t.get('name') or t.get('tool_name') or f"tool_{idx+1}"
                t_roi = t.get('ROI') or t.get('roi') or {}
                tool = InspectionTool(
                    inspection=insp,
                    order_index=idx,
                    name=t_name,
                    type=t_type,
                    roi_x=int(t_roi.get('x', 0) or 0),
                    roi_y=int(t_roi.get('y', 0) or 0),
                    roi_w=int(t_roi.get('w', 0) or 0),
                    roi_h=int(t_roi.get('h', 0) or 0),
                    inspec_pass_fail=bool(t.get('inspec_pass_fail', False)),
                    tool_kind_id=kinds.get(t_type)
                )
                tool.save()
                created.append(tool.id)

                # Tentar preencher configs específicas usando a própria config e, se disponível, o último resultado
                # Buscar possível match no last_tools por nome ou id
                last = None
                for lt in last_tools:
                    if isinstance(lt, dict) and (lt.get('tool_name') == t.get('name') or lt.get('tool_id') == t.get('id')):
                        last = lt
                        break

                if t_type == 'grayscale':
                    GrayscaleTool.objects.create(
                        tool=tool,
                        method=str(t.get('method') or 'luminance'),
                        normalize=bool(t.get('normalize', False))
                    )
                elif t_type == 'blur':
                    BlurTool.objects.create(
                        tool=tool,
                        method=str(t.get('method') or 'gaussian'),
                        ksize=int(t.get('ksize', 3) or 3),
                        sigma=float(t.get('sigma', 0.0) or 0.0)
                    )
                elif t_type == 'threshold':
                    ThresholdTool.objects.create(
                        tool=tool,
                        mode=str(t.get('mode') or 'binary'),
                        th_min=int(t.get('th_min', 0) or 0),
                        th_max=int(t.get('th_max', 255) or 255)
                    )
                elif t_type == 'morphology':
                    MorphologyTool.objects.create(
                        tool=tool,
                        kernel=int(t.get('kernel', 3) or 3),
                        open=int(t.get('open', 0) or 0),
                        close=int(t.get('close', 0) or 0),
                        shape=str(t.get('shape') or 'ellipse')
                    )
                elif t_type == 'blob':
                    BlobToolConfig.objects.create(
                        tool=tool,
                        th_min=int(t.get('th_min', 0) or 0),
                        th_max=int(t.get('th_max', 255) or 255),
                        area_min=float(t.get('area_min', 0.0) or 0.0),
                        area_max=float(t.get('area_max', 1e12) or 1e12),
                        total_area_test=bool(t.get('total_area_test', False)),
                        blob_count_test=bool(t.get('blob_count_test', False)),
                        test_total_area_min=float(t.get('test_total_area_min', 0.0) or 0.0),
                        test_total_area_max=float(t.get('test_total_area_max', 1e12) or 1e12),
                        test_blob_count_min=int(t.get('test_blob_count_min', 0) or 0),
                        test_blob_count_max=int(t.get('test_blob_count_max', 1_000_000) or 1_000_000),
                        contour_chain=str(t.get('contour_chain') or 'SIMPLE'),
                        approx_epsilon_ratio=float(t.get('approx_epsilon_ratio', 0.01) or 0.01),
                        polygon_max_points=int(t.get('polygon_max_points', 0) or 0)
                    )
                elif t_type == 'math':
                    # MathTool referencia outra tool (por id) se possível
                    ref_name = t.get('reference_tool_name') or None
                    ref_id = t.get('reference_tool_id') or None
                    ref_obj = None
                    if ref_id:
                        ref_obj = insp.tools.filter(order_index__lt=tool.order_index, id=ref_id).first()
                    if not ref_obj and ref_name:
                        ref_obj = insp.tools.filter(order_index__lt=tool.order_index, name=ref_name).first()
                    MathTool.objects.create(
                        tool=tool,
                        operation=str(t.get('operation') or ''),
                        reference_tool=ref_obj,
                        custom_formula=str(t.get('custom_formula') or '')
                    )

            return Response({
                'message': 'Inspeção salva',
                'inspection_id': insp.id,
                'tools_created': len(created)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
