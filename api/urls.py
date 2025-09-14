from django.urls import path
from .views import (
    home_view, 
    health_check,
    # DRF VM API Views
    VMListCreate,
    VMDetail,
    VMAction,
    VMStatusSummary,
    VMLoggingConfig,
    VMClearLogs,
    VMSyncLogs,
    vm_logs_upload_function,
    InspectionResultsList,
    SaveInspection,
    InspectionsList,
    InspectionDetail,
    InspectionUpdateVM,
)

urlpatterns = [
    path('', health_check, name='health_check'),  # Rota raiz da API
    path('home', home_view, name='home'),
    
    # ============================================================================
    # VISION MACHINE (VM) API ROUTES - DRF
    # ============================================================================
    
    # VMs - Lista e criação
    path('vms', VMListCreate.as_view(), name='vm_list_create'),
    
    # VM específica - Detalhes, atualização e remoção
    path('vms/<int:vm_id>', VMDetail.as_view(), name='vm_detail'),
    
    # Ações da VM - Start, stop, restart, trigger
    path('vms/<int:vm_id>/action', VMAction.as_view(), name='vm_action'),

    # Logging da VM via protocolo
    path('vms/<int:vm_id>/logging_config', VMLoggingConfig.as_view(), name='vm_logging_config'),
    path('vms/<int:vm_id>/clear_logs', VMClearLogs.as_view(), name='vm_clear_logs'),
    path('vms/<int:vm_id>/sync_logs', VMSyncLogs.as_view(), name='vm_sync_logs'),
    # Upload direto da VM (sem auth) - usado por /api/logs/sync
    path('logs/upload', vm_logs_upload_function, name='vm_logs_upload'),
    
    # Resultados de inspeção
    path('inspection-results', InspectionResultsList.as_view(), name='inspection_results_list'),
    
    # Resumo do status de todas as VMs
    path('vms/status/summary', VMStatusSummary.as_view(), name='vm_status_summary'),
    
    # Salvar inspeção a partir da VM
    path('vms/<int:vm_id>/inspections/save', SaveInspection.as_view(), name='save_inspection'),
    # Listagem de inspeções
    path('inspections', InspectionsList.as_view(), name='inspections_list'),
    # Detalhe/edição offline de inspeção
    path('inspections/<int:insp_id>', InspectionDetail.as_view(), name='inspection_detail'),
    # Atualizar inspeção na VM (online) a partir de JSON enviado
    path('inspections/<int:insp_id>/update_vm', InspectionUpdateVM.as_view(), name='inspection_update_vm'),
    
    # Outras rotas da API serão adicionadas gradualmente
]


