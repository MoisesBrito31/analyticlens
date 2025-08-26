from django.urls import path
from .views import (
    home_view, 
    health_check,
    # DRF VM API Views
    VMListCreate,
    VMDetail,
    VMAction,
    VMStatusSummary,
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


