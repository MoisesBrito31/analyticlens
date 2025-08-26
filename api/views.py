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
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.text import slugify
import base64
import os


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
            # Extrair payload (último JSON do WebSocket ou objeto montado no frontend)
            payload = data.get('payload') or {}
            # Tentar preencher imagem de referência a partir do payload
            # Aceita campos: image_base64/mime/resolution ou final_image como base64
            ref_b64 = None
            ref_mime = None
            ref_w = None
            ref_h = None
            if isinstance(payload, dict):
                # Preferir imagem final processada
                if isinstance(payload.get('inspection_result'), dict) and isinstance(payload['inspection_result'].get('final_image'), str):
                    candidate = payload['inspection_result']['final_image']
                    if candidate and candidate != '[hidden]':
                        ref_b64 = candidate
                        ref_mime = payload.get('mime') or 'image/jpeg'
                # Caso contrário, usar image_base64 do test_result
                if not ref_b64 and isinstance(payload.get('image_base64'), str):
                    candidate = payload['image_base64']
                    # Evitar salvar placeholder oculto
                    if candidate and candidate != '[hidden]':
                        ref_b64 = candidate
                        ref_mime = payload.get('mime') or 'image/jpeg'
                # Resolução
                if isinstance(payload.get('resolution'), list) and len(payload['resolution']) == 2:
                    try:
                        ref_w = int(payload['resolution'][0])
                        ref_h = int(payload['resolution'][1])
                    except Exception:
                        ref_w, ref_h = None, None

            if ref_b64:
                # Salvar arquivo em server/media/inspections/<vm_id>/ com nome determinístico por inspeção
                try:
                    ext = 'jpg'
                    if ref_mime and '/' in ref_mime:
                        ext = ref_mime.split('/')[-1]
                    subdir = os.path.join('inspections', str(vm.id))
                    abs_subdir = os.path.join(settings.MEDIA_ROOT, subdir)
                    os.makedirs(abs_subdir, exist_ok=True)
                    safe_name = slugify(insp.name) or f"inspection_{insp.id or 'new'}"
                    filename = f"{safe_name}.{ext}"
                    file_path = os.path.join(subdir, filename)
                    abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    # Se já houver uma referência anterior e overwrite for verdadeiro, remover o arquivo antigo
                    if overwrite and insp.reference_image_path:
                        old_abs = os.path.join(settings.MEDIA_ROOT, insp.reference_image_path)
                        if os.path.exists(old_abs):
                            try:
                                os.remove(old_abs)
                            except Exception:
                                pass
                    # Decodificar base64 (pode vir com prefixo data:)
                    b64_data = ref_b64.split(',')[-1]
                    binary = base64.b64decode(b64_data)
                    with open(abs_path, 'wb') as f:
                        f.write(binary)
                    insp.reference_image_path = file_path
                    insp.reference_image_mime = ref_mime
                    insp.reference_image_width = ref_w
                    insp.reference_image_height = ref_h
                except Exception:
                    # Não falha a operação por erro de imagem
                    insp.reference_image_path = None

            insp.save()

            # Limpar ferramentas existentes se overwrite
            if overwrite:
                insp.tools.all().delete()

            # Ler configuração atual da VM
            cfg = vm.inspection_config or {}
            tools_cfg = cfg.get('tools', []) if isinstance(cfg, dict) else []

            # Se houver payload com último resultado válido, extrair parâmetros úteis
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


class InspectionsList(APIView):
    """Lista inspeções com VM e ferramentas (nome e tipo)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Filtros opcionais: por vm_id ou busca por nome
            vm_id = request.GET.get('vm_id')
            search = request.GET.get('search', '').strip()

            qs = Inspection.objects.select_related('vm').prefetch_related('tools')
            if vm_id:
                qs = qs.filter(vm_id=vm_id)
            if search:
                qs = qs.filter(name__icontains=search)

            inspections = []
            for insp in qs:
                tools_list = []
                for t in insp.tools.all():
                    tools_list.append({
                        'id': t.id,
                        'name': t.name,
                        'type': t.type,
                    })
                inspections.append({
                    'id': insp.id,
                    'name': insp.name,
                    'vm': {
                        'id': insp.vm.id,
                        'name': insp.vm.name,
                    },
                    'tools': tools_list,
                    'reference_image_url': (settings.MEDIA_URL + insp.reference_image_path) if insp.reference_image_path else None,
                    'reference_image_mime': insp.reference_image_mime,
                    'reference_image_resolution': [insp.reference_image_width, insp.reference_image_height] if (insp.reference_image_width and insp.reference_image_height) else None,
                    'updated_at': insp.updated_at.isoformat() if insp.updated_at else None,
                    'created_at': insp.created_at.isoformat() if insp.created_at else None,
                })

            return Response({'inspections': inspections, 'total_count': len(inspections)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InspectionDetail(APIView):
    """CRUD offline de uma inspeção (sem comunicar com a VM)."""
    permission_classes = [IsAuthenticated]

    def get_object(self, insp_id):
        try:
            return Inspection.objects.select_related('vm').get(id=insp_id)
        except Inspection.DoesNotExist:
            return None

    def get(self, request, insp_id):
        insp = self.get_object(insp_id)
        if not insp:
            return Response({'erro': 'Inspeção não encontrada'}, status=status.HTTP_404_NOT_FOUND)
        tools = []
        for t in insp.tools.order_by('order_index', 'id').all():
            td = {
                'id': t.id,
                'name': t.name,
                'type': t.type,
                'order_index': t.order_index,
                'ROI': {'x': t.roi_x, 'y': t.roi_y, 'w': t.roi_w, 'h': t.roi_h},
                'inspec_pass_fail': t.inspec_pass_fail,
            }
            # Enrich with type-specific config
            if t.type == 'grayscale' and hasattr(t, 'grayscale') and t.grayscale:
                td.update({
                    'method': t.grayscale.method,
                    'normalize': t.grayscale.normalize,
                })
            elif t.type == 'blur' and hasattr(t, 'blur') and t.blur:
                td.update({
                    'method': t.blur.method,
                    'ksize': t.blur.ksize,
                    'sigma': t.blur.sigma,
                })
            elif t.type == 'threshold' and hasattr(t, 'threshold') and t.threshold:
                td.update({
                    'mode': t.threshold.mode,
                    'th_min': t.threshold.th_min,
                    'th_max': t.threshold.th_max,
                })
            elif t.type == 'morphology' and hasattr(t, 'morphology') and t.morphology:
                td.update({
                    'kernel': t.morphology.kernel,
                    'open': t.morphology.open,
                    'close': t.morphology.close,
                    'shape': t.morphology.shape,
                })
            elif t.type == 'blob' and hasattr(t, 'blob') and t.blob:
                td.update({
                    'th_min': t.blob.th_min,
                    'th_max': t.blob.th_max,
                    'area_min': t.blob.area_min,
                    'area_max': t.blob.area_max,
                    'total_area_test': t.blob.total_area_test,
                    'blob_count_test': t.blob.blob_count_test,
                    'test_total_area_min': t.blob.test_total_area_min,
                    'test_total_area_max': t.blob.test_total_area_max,
                    'test_blob_count_min': t.blob.test_blob_count_min,
                    'test_blob_count_max': t.blob.test_blob_count_max,
                    'contour_chain': t.blob.contour_chain,
                    'approx_epsilon_ratio': t.blob.approx_epsilon_ratio,
                    'polygon_max_points': t.blob.polygon_max_points,
                })
            elif t.type == 'math' and hasattr(t, 'math') and t.math:
                td.update({
                    'operation': t.math.operation,
                    'reference_tool_id': t.math.reference_tool_id,
                    'custom_formula': t.math.custom_formula,
                })
            tools.append(td)
        return Response({
            'id': insp.id,
            'name': insp.name,
            'description': insp.description,
            'vm': {'id': insp.vm.id, 'name': insp.vm.name},
            'reference_image_url': (settings.MEDIA_URL + insp.reference_image_path) if insp.reference_image_path else None,
            'tools': tools,
        })

    def put(self, request, insp_id):
        try:
            insp = self.get_object(insp_id)
            if not insp:
                return Response({'erro': 'Inspeção não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            body = request.data if isinstance(request.data, dict) else {}
            name = body.get('name')
            description = body.get('description')
            tools = body.get('tools')

            if isinstance(name, str) and name:
                insp.name = name
            if isinstance(description, str):
                insp.description = description
            insp.save()

            if isinstance(tools, list):
                # Estratégia simples: substituir conjunto por completo (poderemos otimizar depois)
                insp.tools.all().delete()
                kinds = {k.slug: k.id for k in ToolKind.objects.all()}
                created = 0
                for idx, t in enumerate(tools):
                    t_type = str((t.get('type') or '').lower())
                    t_name = t.get('name') or f'tool_{idx+1}'
                    t_roi = t.get('ROI') or {}
                    tool = InspectionTool(
                        inspection=insp,
                        order_index=int(t.get('order_index', idx)),
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
                    created += 1

                    # Criar configs específicas
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
                        # Tenta resolver referência pela ordem/nome já criados
                        ref_obj = None
                        ref_id = t.get('reference_tool_id')
                        ref_name = t.get('reference_tool_name')
                        if ref_id is not None:
                            ref_obj = insp.tools.filter(order_index__lt=tool.order_index, id=ref_id).first()
                        if not ref_obj and ref_name:
                            ref_obj = insp.tools.filter(order_index__lt=tool.order_index, name=ref_name).first()
                        MathTool.objects.create(
                            tool=tool,
                            operation=str(t.get('operation') or ''),
                            reference_tool=ref_obj,
                            custom_formula=str(t.get('custom_formula') or '')
                        )

            return Response({'success': True})
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, insp_id):
        try:
            insp = self.get_object(insp_id)
            if not insp:
                return Response({'erro': 'Inspeção não encontrada'}, status=status.HTTP_404_NOT_FOUND)
            insp.delete()
            return Response({'success': True})
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InspectionUpdateVM(APIView):
    """Atualiza a inspeção configurada na VM (online) com o JSON fornecido."""
    permission_classes = [IsAuthenticated]

    def post(self, request, insp_id):
        try:
            # body.tools é obrigatório (somente tools para VM)
            body = request.data if isinstance(request.data, dict) else {}
            tools = body.get('tools')
            if not isinstance(tools, list):
                return Response({'erro': 'Campo tools é obrigatório como lista'}, status=status.HTTP_400_BAD_REQUEST)

            insp = Inspection.objects.select_related('vm').filter(id=insp_id).first()
            if not insp:
                return Response({'erro': 'Inspeção não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            vm = insp.vm
            # Montar payload de configuração de inspeção conforme VM espera
            config_payload = {
                'config': {
                    'tools': tools
                }
            }

            # Enviar para VM via protocolo
            protocolo = ProtocoloVM()
            result = protocolo.send_command(vm, 'update_inspection_config', params=config_payload)
            if not result.get('ok', False):
                return Response({'erro': result.get('error', 'Falha ao atualizar VM')}, status=status.HTTP_502_BAD_GATEWAY)

            return Response({'success': True})
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
