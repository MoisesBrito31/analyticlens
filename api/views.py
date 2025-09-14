from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json

# DRF imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import status

# Local imports
from .models import (
    VirtualMachine, Inspection, InspectionTool, ToolKind,
    GrayscaleTool, BlurTool, ThresholdTool, MorphologyTool, BlobToolConfig, MathTool,
    InspectionResult
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
import shutil
import mimetypes
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


class VMLoggingConfig(APIView):
    """Atualiza a configuração de logging na VM via protocolo."""
    permission_classes = [IsAuthenticated]

    def post(self, request, vm_id):
        try:
            try:
                vm = VirtualMachine.objects.get(id=vm_id, is_active=True)
            except VirtualMachine.DoesNotExist:
                return Response({'erro': 'VM não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            body = request.data if isinstance(request.data, dict) else {}
            allowed = {'enabled', 'mode', 'policy', 'max_logs', 'batch_size', 'batch_ms'}
            params = {k: body.get(k) for k in allowed if k in body}
            if not params:
                return Response({'erro': 'Nenhum parâmetro de logging fornecido'}, status=status.HTTP_400_BAD_REQUEST)

            proto = ProtocoloVM()
            result = proto.send_command(vm, 'update_logging_config', params=params)
            if not result.get('ok', False):
                return Response({'erro': result.get('error', 'Falha ao atualizar logging na VM')}, status=status.HTTP_502_BAD_GATEWAY)

            # Retornar estado atualizado da VM
            ProtocoloVM().update_status(vm, mark_offline_on_error=True)
            serializer = VirtualMachineSerializer(vm)
            return Response({'success': True, 'vm': serializer.data})
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VMClearLogs(APIView):
    """Limpa os logs (.alog) do disco da VM via protocolo."""
    permission_classes = [IsAuthenticated]

    def post(self, request, vm_id):
        try:
            try:
                vm = VirtualMachine.objects.get(id=vm_id, is_active=True)
            except VirtualMachine.DoesNotExist:
                return Response({'erro': 'VM não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            proto = ProtocoloVM()
            result = proto.send_command(vm, 'clear_logs', params={})
            if not result.get('ok', False):
                return Response({'erro': result.get('error', 'Falha ao limpar logs')}, status=status.HTTP_502_BAD_GATEWAY)

            # Atualizar status da VM após limpeza
            ProtocoloVM().update_status(vm, mark_offline_on_error=True)
            serializer = VirtualMachineSerializer(vm)
            payload = {'success': True, 'vm': serializer.data}
            # anexar métricas de limpeza quando disponíveis
            for k in ('removed', 'errors', 'remaining'):
                if k in result:
                    payload[k] = result[k]
            return Response(payload)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VMSyncLogs(APIView):
    """Solicita à VM que envie os .alog ao orquestrador e limpe os enviados."""
    permission_classes = [IsAuthenticated]

    def post(self, request, vm_id):
        try:
            try:
                vm = VirtualMachine.objects.get(id=vm_id, is_active=True)
            except VirtualMachine.DoesNotExist:
                return Response({'erro': 'VM não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            proto = ProtocoloVM()
            # Passar django_url explicitamente para garantir base correta do orquestrador
            params = {}
            try:
                if vm.django_url:
                    params['django_url'] = vm.django_url
            except Exception:
                pass
            result = proto.send_command(vm, 'sync_logs', params=params)
            if not result.get('ok', False):
                return Response({'erro': result.get('error', 'Falha ao sincronizar logs')}, status=status.HTTP_502_BAD_GATEWAY)

            ProtocoloVM().update_status(vm, mark_offline_on_error=True)
            serializer = VirtualMachineSerializer(vm)
            payload = {'success': True, 'vm': serializer.data}
            for k in ('uploaded', 'failed', 'remaining', 'before'):
                if k in result:
                    payload[k] = result[k]
            return Response(payload)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def vm_logs_upload_function(request):
    """Recebe arquivos .alog enviados pela VM e armazena no disco do orquestrador.
    Esta rota é chamada diretamente pela VM; por isso, não exige autenticação.
    """
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
        
    try:
        machine_id = request.POST.get('machine_id') or request.GET.get('machine_id')
        upload = request.FILES.get('file')
        
        print(f"[VMLogsUpload] Recebendo: machine_id='{machine_id}', arquivo='{upload.name if upload else None}'")
        
        if not machine_id or not upload:
            return JsonResponse({'erro': 'machine_id e file são obrigatórios'}, status=400)

        # Resolver VM
        vm = VirtualMachine.objects.filter(machine_id=machine_id, is_active=True).first()
        if not vm:
            print(f"[VMLogsUpload] ERRO - VM não encontrada para machine_id='{machine_id}'")
            return JsonResponse({'erro': 'VM não encontrada'}, status=404)

        # Diretório destino: media/logs/<vm_id>/
        import os
        from django.conf import settings
        subdir = os.path.join('logs', str(vm.id))
        abs_dir = os.path.join(settings.MEDIA_ROOT, subdir)
        os.makedirs(abs_dir, exist_ok=True)

        # Processar arquivo .alog e extrair apenas a imagem
        try:
            # Ler arquivo .alog diretamente da memória
            alog_data = b''
            for chunk in upload.chunks():
                alog_data += chunk
            
            print(f"[VMLogsUpload] Processando arquivo .alog de {len(alog_data)} bytes")
            
            # Formato: 'ALOG'(4) + version(4) + json_len(8) + img_len(8) + json + img
            if len(alog_data) < 24:  # Tamanho mínimo do header
                raise ValueError('Arquivo .alog muito pequeno')
                
            magic = alog_data[:4]
            if magic != b'ALOG':
                raise ValueError(f'Arquivo não possui assinatura ALOG válida: {magic}')
            
            offset = 4
            _version = int.from_bytes(alog_data[offset:offset+4], 'big', signed=False)
            offset += 4
            
            json_len = int.from_bytes(alog_data[offset:offset+8], 'big', signed=False)
            offset += 8
            
            img_len = int.from_bytes(alog_data[offset:offset+8], 'big', signed=False)
            offset += 8
            
            print(f"[VMLogsUpload] JSON: {json_len} bytes, IMG: {img_len} bytes")
            
            # Extrair JSON
            if json_len > 0 and offset + json_len <= len(alog_data):
                json_bytes = alog_data[offset:offset+json_len]
                json_str = json_bytes.decode('utf-8')
                data = json.loads(json_str)
                offset += json_len
            else:
                data = {}
            
            # Extrair e salvar apenas a imagem
            image_url = None
            image_mime = None
            image_width = None
            image_height = None
            
            if img_len > 0 and offset + img_len <= len(alog_data):
                img_data = alog_data[offset:offset+img_len]
                print(f"[VMLogsUpload] Extraindo imagem de {len(img_data)} bytes")
                
                # Determinar formato da imagem pelos primeiros bytes
                if img_data.startswith(b'\xff\xd8\xff'):
                    image_ext = 'jpg'
                    image_mime = 'image/jpeg'
                elif img_data.startswith(b'\x89PNG\r\n\x1a\n'):
                    image_ext = 'png'
                    image_mime = 'image/png'
                elif img_data.startswith(b'BM'):
                    image_ext = 'bmp'
                    image_mime = 'image/bmp'
                else:
                    image_ext = 'jpg'  # Default
                    image_mime = 'image/jpeg'
                
                # Nome do arquivo de imagem baseado no timestamp ou ID
                timestamp_str = data.get('timestamp', '').replace(':', '-').replace(' ', '_') if data.get('timestamp') else 'unknown'
                cycle_id = data.get('id', 'unknown')
                image_filename = f"{cycle_id}_{timestamp_str}.{image_ext}"
                image_path = os.path.join(abs_dir, image_filename)
                
                # Salvar apenas a imagem
                with open(image_path, 'wb') as img_file:
                    img_file.write(img_data)
                
                # URL pública da imagem
                image_url = settings.MEDIA_URL + os.path.join(subdir, image_filename).replace('\\', '/')
                print(f"[VMLogsUpload] Imagem salva: {image_url}")
                
                # Tentar obter dimensões da imagem
                try:
                    from PIL import Image
                    with Image.open(image_path) as img:
                        image_width, image_height = img.size
                        print(f"[VMLogsUpload] Dimensões da imagem: {image_width}x{image_height}")
                except ImportError:
                    print(f"[VMLogsUpload] PIL não disponível, dimensões não extraídas")
                except Exception as img_err:
                    print(f"[VMLogsUpload] Erro ao obter dimensões: {img_err}")
            else:
                print(f"[VMLogsUpload] Nenhuma imagem encontrada no arquivo .alog")

            # Montar e salvar InspectionResult
            ts = data.get('timestamp')
            try:
                # Normalizar timestamp
                if isinstance(ts, str):
                    dt = timezone.datetime.fromisoformat(ts)
                else:
                    dt = timezone.now()
                    
                if dt.tzinfo is None:
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
            except Exception:
                dt = timezone.now()

            insp_res = InspectionResult(
                vm=vm,
                cycle_id=str(data.get('id') or ''),
                timestamp=dt,
                approved=bool(data.get('approved', False)),
                duration_ms=0,
                frame=0,
                reprovadas=0,
                image_url=image_url,
                image_mime=image_mime,
                image_width=image_width,
                image_height=image_height,
                result_json=data.get('result') if isinstance(data.get('result'), (dict, list)) else {'raw': data}
            )
            
            insp_res.save()
            print(f"[VMLogsUpload] InspectionResult criado: ID={insp_res.id}, cycle_id={insp_res.cycle_id}")
            
        except Exception as parse_err:
            # Não falhar upload por erro de parsing; apenas reportar no payload
            print(f"[VMLogsUpload] Erro ao processar arquivo .alog: {str(parse_err)}")
            return JsonResponse({'success': True, 'parsed': False, 'error': str(parse_err)})

        return JsonResponse({'success': True, 'parsed': True, 'image_url': image_url})
        
    except Exception as e:
        print(f"[VMLogsUpload] Erro geral: {str(e)}")
        return JsonResponse({'erro': str(e)}, status=500)


class InspectionResultsList(APIView):
    """Lista resultados de inspeção com filtros"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Filtros
            vm_id = request.query_params.get('vm_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # Query base
            queryset = InspectionResult.objects.select_related('vm').all()
            
            # Aplicar filtros
            if vm_id:
                queryset = queryset.filter(vm_id=vm_id)
            
            if start_date:
                try:
                    start_dt = timezone.datetime.fromisoformat(start_date)
                    if start_dt.tzinfo is None:
                        start_dt = timezone.make_aware(start_dt)
                    queryset = queryset.filter(timestamp__gte=start_dt)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_dt = timezone.datetime.fromisoformat(end_date)
                    if end_dt.tzinfo is None:
                        end_dt = timezone.make_aware(end_dt)
                    # Adicionar 23:59:59 para incluir o dia inteiro
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    queryset = queryset.filter(timestamp__lte=end_dt)
                except ValueError:
                    pass
            
            # Ordenar por timestamp decrescente (mais recentes primeiro)
            queryset = queryset.order_by('-timestamp')
            
            # Serializar dados
            results = []
            for result in queryset:
                results.append({
                    'id': result.id,
                    'vm_id': result.vm.id,
                    'vm_name': result.vm.name,
                    'vm_status': result.vm.connection_status,
                    'cycle_id': result.cycle_id,
                    'timestamp': result.timestamp.isoformat(),
                    'approved': result.approved,
                    'duration_ms': result.duration_ms,
                    'frame': result.frame,
                    'reprovadas': result.reprovadas,
                    'image_url': result.image_url,
                    'image_mime': result.image_mime,
                    'image_width': result.image_width,
                    'image_height': result.image_height,
                    'result_json': result.result_json
                })
            
            return Response({'data': results})
            
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            # Salvar arquivo em server/media/inspections/<vm_id>/ com nome determinístico por inspeção
            try:
                subdir = os.path.join('inspections', str(vm.id))
                abs_subdir = os.path.join(settings.MEDIA_ROOT, subdir)
                os.makedirs(abs_subdir, exist_ok=True)
                safe_name = slugify(insp.name) or f"inspection_{insp.id or 'new'}"
                # Se já houver uma referência anterior e overwrite for verdadeiro, remover o arquivo antigo
                if overwrite and insp.reference_image_path:
                    old_abs = os.path.join(settings.MEDIA_ROOT, insp.reference_image_path)
                    if os.path.exists(old_abs):
                        try:
                            os.remove(old_abs)
                        except Exception:
                            pass

                if ref_b64:
                    ext = 'jpg'
                    if ref_mime and '/' in ref_mime:
                        ext = ref_mime.split('/')[-1]
                    filename = f"{safe_name}.{ext}"
                    file_path = os.path.join(subdir, filename)
                    abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    # Decodificar base64 (pode vir com prefixo data:)
                    b64_data = ref_b64.split(',')[-1]
                    binary = base64.b64decode(b64_data)
                    with open(abs_path, 'wb') as f:
                        f.write(binary)
                    insp.reference_image_path = file_path
                    insp.reference_image_mime = ref_mime
                    insp.reference_image_width = ref_w
                    insp.reference_image_height = ref_h
                else:
                    # Tentar copiar arquivo existente se referência por URL/path for fornecida
                    src_url = None
                    if isinstance(payload.get('reference_image_path'), str):
                        src_url = payload.get('reference_image_path')
                    elif isinstance(payload.get('reference_image_url'), str):
                        src_url = payload.get('reference_image_url')
                    if src_url:
                        rel = str(src_url)
                        # Remover prefixo MEDIA_URL ou '/media/' para obter caminho relativo
                        if settings.MEDIA_URL and rel.startswith(settings.MEDIA_URL):
                            rel = rel[len(settings.MEDIA_URL):]
                        rel = rel.replace('/media/', '')
                        src_abs = os.path.join(settings.MEDIA_ROOT, rel)
                        if os.path.exists(src_abs):
                            ext = os.path.splitext(src_abs)[1].lstrip('.') or 'jpg'
                            guessed_mime, _ = mimetypes.guess_type(src_abs)
                            filename = f"{safe_name}.{ext}"
                            file_path = os.path.join(subdir, filename)
                            abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
                            shutil.copyfile(src_abs, abs_path)
                            insp.reference_image_path = file_path
                            insp.reference_image_mime = guessed_mime or ref_mime or 'image/jpeg'
                            # Dimensões podem não estar disponíveis; manter as existentes se houver
                
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
                # Inferir shape quando ausente, mas com chaves circle/ellipse/rect
                if isinstance(t_roi, dict) and 'shape' not in t_roi:
                    if 'circle' in t_roi: t_roi['shape'] = 'circle'
                    elif 'ellipse' in t_roi: t_roi['shape'] = 'ellipse'
                    elif 'rect' in t_roi or all(k in t_roi for k in ('x','y','w','h')): t_roi['shape'] = 'rect'
                t_roi = t.get('ROI') or t.get('roi') or {}
                if isinstance(t_roi, dict) and 'shape' not in t_roi:
                    if 'circle' in t_roi: t_roi['shape'] = 'circle'
                    elif 'ellipse' in t_roi: t_roi['shape'] = 'ellipse'
                    elif 'rect' in t_roi or all(k in t_roi for k in ('x','y','w','h')): t_roi['shape'] = 'rect'
                # Normaliza ROI para shape + bbox
                bx = int(t_roi.get('x', 0) or 0)
                by = int(t_roi.get('y', 0) or 0)
                bw = int(t_roi.get('w', 0) or 0)
                bh = int(t_roi.get('h', 0) or 0)
                roi_shape_json = {}
                if isinstance(t_roi, dict) and (t_roi.get('shape') or t_roi.get('rect') or t_roi.get('circle') or t_roi.get('ellipse')):
                    shape = t_roi.get('shape', 'rect')
                    if shape == 'rect':
                        r = t_roi.get('rect', t_roi)
                        bx = int(r.get('x', bx) or bx)
                        by = int(r.get('y', by) or by)
                        bw = int(r.get('w', bw) or bw)
                        bh = int(r.get('h', bh) or bh)
                        roi_shape_json = {'shape': 'rect', 'rect': {'x': bx, 'y': by, 'w': bw, 'h': bh}}
                    elif shape == 'circle':
                        c = t_roi.get('circle', {})
                        cx = int(c.get('cx', 0) or 0)
                        cy = int(c.get('cy', 0) or 0)
                        rr = int(c.get('r', 0) or 0)
                        bx, by, bw, bh = cx - rr, cy - rr, rr * 2, rr * 2
                        roi_shape_json = {'shape': 'circle', 'circle': {'cx': cx, 'cy': cy, 'r': rr}}
                    elif shape == 'ellipse':
                        e = t_roi.get('ellipse', {})
                        cx = int(e.get('cx', 0) or 0)
                        cy = int(e.get('cy', 0) or 0)
                        rx = int(e.get('rx', 0) or 0)
                        ry = int(e.get('ry', 0) or 0)
                        angle = float(e.get('angle', 0.0) or 0.0)
                        bx, by, bw, bh = cx - rx, cy - ry, rx * 2, ry * 2
                        roi_shape_json = {'shape': 'ellipse', 'ellipse': {'cx': cx, 'cy': cy, 'rx': rx, 'ry': ry, 'angle': angle}}
                else:
                    roi_shape_json = {'shape': 'rect', 'rect': {'x': bx, 'y': by, 'w': bw, 'h': bh}}
                tool = InspectionTool(
                    inspection=insp,
                    order_index=idx,
                    name=t_name,
                    type=t_type,
                    roi_x=bx,
                    roi_y=by,
                    roi_w=bw,
                    roi_h=bh,
                    inspec_pass_fail=bool(t.get('inspec_pass_fail', False)),
                    tool_kind_id=kinds.get(t_type)
                )
                try:
                    tool.roi_shape = roi_shape_json
                except Exception:
                    pass
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
            # Preferir ROI com shape salvo; se ausente, usar campos legacy x/y/w/h
            roi_json = {}
            try:
                roi_json = t.roi_shape or {}
            except Exception:
                roi_json = {}
            td = {
                'id': t.id,
                'name': t.name,
                'type': t.type,
                'order_index': t.order_index,
                'ROI': roi_json if isinstance(roi_json, dict) and roi_json.get('shape') else {'x': t.roi_x, 'y': t.roi_y, 'w': t.roi_w, 'h': t.roi_h},
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
            vm_id = body.get('vm_id')
            tools = body.get('tools')

            if isinstance(name, str) and name:
                insp.name = name
            if isinstance(description, str):
                insp.description = description
            # Atualizar associação de VM quando solicitado
            if vm_id is not None:
                try:
                    vm_obj = VirtualMachine.objects.filter(id=int(vm_id)).first() if vm_id else None
                    if vm_obj:
                        insp.vm = vm_obj
                except Exception:
                    pass
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
                    # Normaliza ROI: salva bounding box legacy e JSON completo em roi_shape
                    bx = int(t_roi.get('x', 0) or 0)
                    by = int(t_roi.get('y', 0) or 0)
                    bw = int(t_roi.get('w', 0) or 0)
                    bh = int(t_roi.get('h', 0) or 0)
                    roi_shape_json = {}
                    if isinstance(t_roi, dict) and (t_roi.get('shape') or t_roi.get('rect') or t_roi.get('circle') or t_roi.get('ellipse')):
                        shape = t_roi.get('shape', 'rect')
                        if shape == 'rect':
                            r = t_roi.get('rect', t_roi)
                            bx = int(r.get('x', bx) or bx)
                            by = int(r.get('y', by) or by)
                            bw = int(r.get('w', bw) or bw)
                            bh = int(r.get('h', bh) or bh)
                            roi_shape_json = {'shape': 'rect', 'rect': {'x': bx, 'y': by, 'w': bw, 'h': bh}}
                        elif shape == 'circle':
                            c = t_roi.get('circle', {})
                            cx = int(c.get('cx', 0) or 0)
                            cy = int(c.get('cy', 0) or 0)
                            rr = int(c.get('r', 0) or 0)
                            bx, by, bw, bh = cx - rr, cy - rr, rr * 2, rr * 2
                            roi_shape_json = {'shape': 'circle', 'circle': {'cx': cx, 'cy': cy, 'r': rr}}
                        elif shape == 'ellipse':
                            e = t_roi.get('ellipse', {})
                            cx = int(e.get('cx', 0) or 0)
                            cy = int(e.get('cy', 0) or 0)
                            rx = int(e.get('rx', 0) or 0)
                            ry = int(e.get('ry', 0) or 0)
                            angle = float(e.get('angle', 0.0) or 0.0)
                            bx, by, bw, bh = cx - rx, cy - ry, rx * 2, ry * 2
                            roi_shape_json = {'shape': 'ellipse', 'ellipse': {'cx': cx, 'cy': cy, 'rx': rx, 'ry': ry, 'angle': angle}}
                    else:
                        roi_shape_json = {'shape': 'rect', 'rect': {'x': bx, 'y': by, 'w': bw, 'h': bh}}

                    tool = InspectionTool(
                        inspection=insp,
                        order_index=int(t.get('order_index', idx)),
                        name=t_name,
                        type=t_type,
                        roi_x=bx,
                        roi_y=by,
                        roi_w=bw,
                        roi_h=bh,
                        inspec_pass_fail=bool(t.get('inspec_pass_fail', False)),
                        tool_kind_id=kinds.get(t_type)
                    )
                    try:
                        tool.roi_shape = roi_shape_json
                    except Exception:
                        pass
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
            tools = body.get('tools') if isinstance(body.get('tools'), list) else None
            # Permitir chamadas que apenas atualizam source/trigger sem tools
            if tools is None and not (isinstance(body.get('source_config'), dict) or isinstance(body.get('trigger_config'), dict)):
                return Response({'erro': 'Forneça tools (lista) ou source/trigger para atualizar'}, status=status.HTTP_400_BAD_REQUEST)

            insp = Inspection.objects.select_related('vm').filter(id=insp_id).first()
            if not insp:
                return Response({'erro': 'Inspeção não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            vm = insp.vm
            # Persistir alterações de source/trigger na tabela da VM relacionada
            try:
                vm_updated_fields = []
                # Atualizar source_config → campos diretos e JSON
                if isinstance(body.get('source_config'), dict):
                    src = body.get('source_config')
                    try:
                        stype = str(src.get('type') or vm.source_type)
                        if stype and stype != vm.source_type:
                            vm.source_type = stype
                            vm_updated_fields.append('source_type')
                    except Exception:
                        pass
                    try:
                        cam_id = int(src.get('camera_id')) if src.get('camera_id') is not None else vm.camera_id
                        if cam_id != vm.camera_id:
                            vm.camera_id = cam_id
                            vm_updated_fields.append('camera_id')
                    except Exception:
                        pass
                    try:
                        fps_val = int(src.get('fps')) if src.get('fps') is not None else vm.fps
                        if fps_val != vm.fps:
                            vm.fps = fps_val
                            vm_updated_fields.append('fps')
                    except Exception:
                        pass
                    try:
                        folder = str(src.get('folder_path') or '')
                        if folder != vm.folder_path:
                            vm.folder_path = folder
                            vm_updated_fields.append('folder_path')
                    except Exception:
                        pass
                    try:
                        rtsp = str(src.get('rtsp_url') or '')
                        if rtsp != vm.rtsp_url:
                            vm.rtsp_url = rtsp
                            vm_updated_fields.append('rtsp_url')
                    except Exception:
                        pass
                    try:
                        res = src.get('resolution')
                        if isinstance(res, (list, tuple)) and len(res) == 2:
                            rw = int(res[0]) if res[0] is not None else vm.resolution_width
                            rh = int(res[1]) if res[1] is not None else vm.resolution_height
                            if rw != vm.resolution_width:
                                vm.resolution_width = rw
                                vm_updated_fields.append('resolution_width')
                            if rh != vm.resolution_height:
                                vm.resolution_height = rh
                                vm_updated_fields.append('resolution_height')
                    except Exception:
                        pass

                    # Atualizar inspection_config JSON
                    try:
                        cfg = vm.inspection_config or {}
                        if not isinstance(cfg, dict):
                            cfg = {}
                        cfg['source_config'] = src
                        vm.inspection_config = cfg
                        if 'inspection_config' not in vm_updated_fields:
                            vm_updated_fields.append('inspection_config')
                    except Exception:
                        pass

                # Atualizar trigger_config → campos diretos e JSON
                if isinstance(body.get('trigger_config'), dict):
                    trg = body.get('trigger_config')
                    try:
                        ttype = str(trg.get('type') or vm.trigger_type)
                        if ttype and ttype != vm.trigger_type:
                            vm.trigger_type = ttype
                            vm_updated_fields.append('trigger_type')
                    except Exception:
                        pass
                    try:
                        interval = int(trg.get('interval_ms')) if trg.get('interval_ms') is not None else vm.trigger_interval_ms
                        if interval != vm.trigger_interval_ms:
                            vm.trigger_interval_ms = interval
                            vm_updated_fields.append('trigger_interval_ms')
                    except Exception:
                        pass

                    # Atualizar inspection_config JSON
                    try:
                        cfg = vm.inspection_config or {}
                        if not isinstance(cfg, dict):
                            cfg = {}
                        cfg['trigger_config'] = trg
                        vm.inspection_config = cfg
                        if 'inspection_config' not in vm_updated_fields:
                            vm_updated_fields.append('inspection_config')
                    except Exception:
                        pass

                if vm_updated_fields:
                    # Sempre atualiza updated_at
                    vm.save(update_fields=list(set(vm_updated_fields + ['updated_at'])))
            except Exception:
                # Não bloquear fluxo por erro de persistência local
                pass
            # Montar payload de configuração de inspeção conforme VM espera (quando houver tools)
            config_payload = None
            if tools is not None:
                config_payload = {
                    'config': {
                        'tools': tools
                    }
                }
            # Encaminhar source_config e trigger_config quando fornecidos
            if isinstance(body.get('source_config'), dict):
                # A VM expõe endpoints separados para source/trigger, mas também mantém em inspection_config
                try:
                    ProtocoloVM().send_command(vm, 'update_source_config', params=body.get('source_config'))
                except Exception:
                    pass
                # incluir na config principal também (para consistência visual)
                if config_payload is not None:
                    config_payload['config']['source_config'] = body.get('source_config')
            if isinstance(body.get('trigger_config'), dict):
                try:
                    ProtocoloVM().send_command(vm, 'update_trigger_config', params=body.get('trigger_config'))
                except Exception:
                    pass
                if config_payload is not None:
                    config_payload['config']['trigger_config'] = body.get('trigger_config')

            # Enviar para VM via protocolo quando houver tools
            if config_payload is not None:
                protocolo = ProtocoloVM()
                result = protocolo.send_command(vm, 'update_inspection_config', params=config_payload)
                if not result.get('ok', False):
                    return Response({'erro': result.get('error', 'Falha ao atualizar VM')}, status=status.HTTP_502_BAD_GATEWAY)

            return Response({'success': True})
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
