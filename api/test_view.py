"""
Testes para as views da API de VMs
Testa todas as funcionalidades: listagem, criação, detalhes, ações e resumo de status
"""

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import json

from .models import VirtualMachine
from user.models import User  # Usar o modelo de usuário customizado do projeto


class VirtualMachineViewsTestCase(TestCase):
    """Testes para todas as views de VirtualMachine"""
    
    def setUp(self):
        """Configuração inicial para todos os testes"""
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar VMs de teste
        self.vm1 = VirtualMachine.objects.create(
            machine_id='VM001',
            name='VM de Teste 1',
            description='Primeira VM para testes',
            status='running',
            mode='TESTE',
            connection_status='connected',
            ip_address='192.168.1.100',
            port=5000,
            source_type='camera',
            camera_id=1,
            resolution_width=752,
            resolution_height=480,
            fps=30,
            trigger_type='continuous',
            trigger_interval_ms=1000,
            inspection_config={'test': True},
            owner=self.user
        )
        
        self.vm2 = VirtualMachine.objects.create(
            machine_id='VM002',
            name='VM de Teste 2',
            description='Segunda VM para testes',
            status='stopped',
            mode='PRODUCAO',
            connection_status='disconnected',
            ip_address='192.168.1.101',
            port=5001,
            source_type='pasta',
            camera_id=2,
            resolution_width=1280,
            resolution_height=720,
            fps=25,
            trigger_type='manual',
            trigger_interval_ms=2000,
            inspection_config={'production': True},
            owner=self.user
        )
        
        # Configurar cliente de teste
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_home_view(self):
        """Testa a view da página inicial da API"""
        url = reverse('home')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('endpoints', data)
        self.assertIn('vms', data['endpoints'])
    
    def test_health_check(self):
        """Testa o health check da API"""
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_vm_list_get(self):
        """Testa a listagem de VMs (GET)"""
        url = reverse('vm_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('vms', data)
        self.assertIn('total_count', data)
        self.assertEqual(data['total_count'], 2)
        self.assertEqual(len(data['vms']), 2)
        
        # Verificar se os campos estão presentes
        vm_data = data['vms'][0]
        expected_fields = [
            'id', 'machine_id', 'name', 'description', 'status', 'mode',
            'connection_status', 'ip_address', 'port', 'source_type',
            'resolution', 'fps', 'trigger_type', 'last_heartbeat',
            'error_message', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, vm_data)
    
    def test_vm_list_get_with_filters(self):
        """Testa a listagem de VMs com filtros"""
        url = reverse('vm_list_create')
        
        # Filtro por status
        response = self.client.get(url, {'status': 'running'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['vms'][0]['status'], 'running')
        
        # Filtro por modo
        response = self.client.get(url, {'mode': 'PRODUCAO'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['vms'][0]['mode'], 'PRODUCAO')
        
        # Filtro por conexão
        response = self.client.get(url, {'connection_status': 'connected'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['vms'][0]['connection_status'], 'connected')
        
        # Filtro de busca
        response = self.client.get(url, {'search': 'Teste 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_count'], 1)
        self.assertIn('Teste 1', data['vms'][0]['name'])
    
    def test_vm_list_get_with_multiple_filters(self):
        """Testa a listagem de VMs com múltiplos filtros combinados"""
        url = reverse('vm_list_create')
        
        # Filtro combinado: status + modo
        response = self.client.get(url, {
            'status': 'running',
            'mode': 'TESTE'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['vms'][0]['status'], 'running')
        self.assertEqual(data['vms'][0]['mode'], 'TESTE')
        
        # Filtro combinado: status + connection_status
        response = self.client.get(url, {
            'status': 'stopped',
            'connection_status': 'disconnected'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['vms'][0]['status'], 'stopped')
        self.assertEqual(data['vms'][0]['connection_status'], 'disconnected')
    
    def test_vm_list_get_with_empty_filters(self):
        """Testa a listagem de VMs com filtros vazios"""
        url = reverse('vm_list_create')
        
        # Filtros vazios devem retornar todas as VMs
        response = self.client.get(url, {
            'status': '',
            'mode': '',
            'connection_status': '',
            'search': ''
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_count'], 2)
    
    def test_vm_create_post(self):
        """Testa a criação de VMs (POST)"""
        url = reverse('vm_list_create')
        vm_data = {
            'machine_id': 'VM003',
            'name': 'Nova VM de Teste',
            'description': 'VM criada via teste',
            'status': 'stopped',
            'mode': 'TESTE',
            'connection_status': 'disconnected',
            'ip_address': '192.168.1.102',
            'port': 5002,
            'source_type': 'rtsp',
            'camera_id': 3,
            'resolution_width': 1920,
            'resolution_height': 1080,
            'fps': 60,
            'trigger_type': 'interval',
            'trigger_interval_ms': 1500,
            'inspection_config': {'new_test': True}
        }
        
        response = self.client.post(url, vm_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('vm_id', data)
        self.assertIn('machine_id', data)
        
        # Verificar se a VM foi criada no banco
        vm = VirtualMachine.objects.get(machine_id='VM003')
        self.assertEqual(vm.name, 'Nova VM de Teste')
        self.assertEqual(vm.owner, self.user)
    
    def test_vm_create_post_minimal_data(self):
        """Testa a criação de VMs com dados mínimos"""
        url = reverse('vm_list_create')
        vm_data = {
            'machine_id': 'VM_MINIMAL',
            'name': 'VM Mínima',
            'mode': 'TESTE'
        }
        
        response = self.client.post(url, vm_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('vm_id', data)
        
        # Verificar se a VM foi criada com valores padrão
        vm = VirtualMachine.objects.get(machine_id='VM_MINIMAL')
        self.assertEqual(vm.status, 'stopped')  # valor padrão
        self.assertEqual(vm.connection_status, 'disconnected')  # valor padrão
        self.assertEqual(vm.source_type, 'camera')  # valor padrão
    
    def test_vm_create_post_invalid_data(self):
        """Testa criação de VM com dados inválidos"""
        url = reverse('vm_list_create')
        
        # Testar com dados inválidos
        invalid_data = {
            'machine_id': 'VM_INVALID',
            'name': '',  # nome vazio
            'mode': 'INVALID_MODE'  # modo inválido
        }
        
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('erro', data)
    
    def test_vm_detail_get(self):
        """Testa a obtenção de detalhes de uma VM (GET)"""
        url = reverse('vm_detail', kwargs={'vm_id': self.vm1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['machine_id'], 'VM001')
        self.assertEqual(data['name'], 'VM de Teste 1')
        self.assertEqual(data['status'], 'running')
        
        # Verificar campos adicionais do serializer completo
        self.assertIn('django_url', data)
        self.assertIn('rtsp_url', data)
        self.assertIn('resolution_width', data)
        self.assertIn('resolution_height', data)
        self.assertIn('trigger_interval_ms', data)
    
    def test_vm_detail_get_not_found(self):
        """Testa obtenção de VM inexistente"""
        url = reverse('vm_detail', kwargs={'vm_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('erro', data)
    
    def test_vm_detail_put(self):
        """Testa a atualização de uma VM (PUT)"""
        url = reverse('vm_detail', kwargs={'vm_id': self.vm1.id})
        update_data = {
            'name': 'VM Atualizada',
            'description': 'Descrição atualizada',
            'fps': 60
        }
        
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        
        # Verificar se foi atualizada no banco
        self.vm1.refresh_from_db()
        self.assertEqual(self.vm1.name, 'VM Atualizada')
        self.assertEqual(self.vm1.fps, 60)
    
    def test_vm_detail_put_partial(self):
        """Testa a atualização parcial de uma VM (PUT)"""
        url = reverse('vm_detail', kwargs={'vm_id': self.vm1.id})
        update_data = {
            'name': 'VM Atualizada Parcialmente'
        }
        
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se apenas o nome foi atualizado
        self.vm1.refresh_from_db()
        self.assertEqual(self.vm1.name, 'VM Atualizada Parcialmente')
        self.assertEqual(self.vm1.description, 'Primeira VM para testes')  # não alterado
        self.assertEqual(self.vm1.fps, 30)  # não alterado
    
    def test_vm_detail_delete(self):
        """Testa a remoção (hard delete) de uma VM (DELETE)"""
        url = reverse('vm_detail', kwargs={'vm_id': self.vm1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        
        # Verificar se foi removida do banco (hard delete)
        self.assertFalse(VirtualMachine.objects.filter(id=self.vm1.id).exists())
    
    def test_vm_action_start(self):
        """Testa a ação de iniciar VM"""
        url = reverse('vm_action', kwargs={'vm_id': self.vm2.id})
        action_data = {'action': 'start'}
        
        response = self.client.post(url, action_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('status', data)
        
        # Verificar se o status foi alterado
        self.vm2.refresh_from_db()
        self.assertEqual(self.vm2.status, 'running')
    
    def test_vm_action_stop(self):
        """Testa a ação de parar VM"""
        url = reverse('vm_action', kwargs={'vm_id': self.vm1.id})
        action_data = {'action': 'stop'}
        
        response = self.client.post(url, action_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('status', data)
        
        # Verificar se o status foi alterado
        self.vm1.refresh_from_db()
        self.assertEqual(self.vm1.status, 'stopped')
    
    def test_vm_action_restart(self):
        """Testa a ação de reiniciar VM"""
        url = reverse('vm_action', kwargs={'vm_id': self.vm1.id})
        action_data = {'action': 'restart'}
        
        response = self.client.post(url, action_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('status', data)
        
        # Verificar se o status foi alterado
        self.vm1.refresh_from_db()
        self.assertEqual(self.vm1.status, 'running')
    
    def test_vm_action_trigger(self):
        """Testa a ação de trigger manual"""
        url = reverse('vm_action', kwargs={'vm_id': self.vm1.id})
        action_data = {'action': 'trigger'}
        
        response = self.client.post(url, action_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
    
    def test_vm_action_invalid_action(self):
        """Testa ação inválida"""
        url = reverse('vm_action', kwargs={'vm_id': self.vm1.id})
        action_data = {'action': 'invalid_action'}
        
        response = self.client.post(url, action_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('erro', data)
    
    def test_vm_action_missing_action(self):
        """Testa ação sem especificar o campo action"""
        url = reverse('vm_action', kwargs={'vm_id': self.vm1.id})
        action_data = {}
        
        response = self.client.post(url, action_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('erro', data)
    
    def test_vm_action_vm_not_found(self):
        """Testa ação em VM inexistente"""
        url = reverse('vm_action', kwargs={'vm_id': 99999})
        action_data = {'action': 'start'}
        
        response = self.client.post(url, action_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('erro', data)
    
    def test_vm_status_summary(self):
        """Testa o resumo de status das VMs"""
        url = reverse('vm_status_summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verificar campos obrigatórios
        expected_fields = [
            'total_vms', 'status_counts', 'connection_counts', 'mode_counts',
            'error_vms', 'offline_vms', 'timestamp'
        ]
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Verificar contadores
        self.assertEqual(data['total_vms'], 2)
        self.assertEqual(data['status_counts']['running'], 1)
        self.assertEqual(data['status_counts']['stopped'], 1)
        self.assertEqual(data['connection_counts']['connected'], 1)
        self.assertEqual(data['connection_counts']['disconnected'], 1)
        self.assertEqual(data['mode_counts']['TESTE'], 1)
        self.assertEqual(data['mode_counts']['PRODUCAO'], 1)
    
    def test_vm_status_summary_with_heartbeat(self):
        """Testa resumo com VMs com heartbeat antigo"""
        # Atualizar last_heartbeat para uma VM (simular VM offline)
        old_time = timezone.now() - timedelta(hours=2)
        self.vm2.last_heartbeat = old_time
        self.vm2.save()
        
        url = reverse('vm_status_summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verificar se há VMs offline
        self.assertIn('offline_vms', data)
        if data['offline_vms']:
            offline_vm = data['offline_vms'][0]
            self.assertIn('id', offline_vm)
            self.assertIn('name', offline_vm)
            self.assertIn('last_heartbeat', offline_vm)
    
    def test_vm_status_summary_with_error_vms(self):
        """Testa resumo com VMs com erro"""
        # Criar uma VM com erro
        error_vm = VirtualMachine.objects.create(
            machine_id='VM_ERROR',
            name='VM com Erro',
            status='error',
            mode='TESTE',
            connection_status='disconnected',
            error_message='Erro de teste',
            owner=self.user
        )
        
        url = reverse('vm_status_summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verificar se há VMs com erro
        self.assertIn('error_vms', data)
        if data['error_vms']:
            error_vm_data = data['error_vms'][0]
            self.assertIn('id', error_vm_data)
            self.assertIn('name', error_vm_data)
            self.assertIn('error_message', error_vm_data)
            self.assertIn('last_heartbeat', error_vm_data)
    
    def test_vm_status_summary_empty_database(self):
        """Testa resumo com banco de dados vazio"""
        # Remover todas as VMs
        VirtualMachine.objects.all().delete()
        
        url = reverse('vm_status_summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verificar contadores vazios
        self.assertEqual(data['total_vms'], 0)
        self.assertEqual(data['status_counts'], {})
        self.assertEqual(data['connection_counts'], {})
        self.assertEqual(data['mode_counts'], {})
        self.assertEqual(data['error_vms'], [])
        self.assertEqual(data['offline_vms'], [])
    
    def test_authentication_required(self):
        """Testa se autenticação é obrigatória"""
        # Cliente sem autenticação
        unauthenticated_client = APIClient()
        
        # Testar todas as views
        urls_to_test = [
            reverse('vm_list_create'),
            reverse('vm_detail', kwargs={'vm_id': self.vm1.id}),
            reverse('vm_action', kwargs={'vm_id': self.vm1.id}),
            reverse('vm_status_summary')
        ]
        
        for url in urls_to_test:
            response = unauthenticated_client.get(url)
            # Django REST Framework retorna 403 Forbidden para usuários não autenticados
            # quando IsAuthenticated permission class é usada
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_serializer_fields(self):
        """Testa se todos os campos do serializer estão funcionando"""
        url = reverse('vm_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        if data['vms']:
            vm_data = data['vms'][0]
            
            # Verificar campos específicos
            self.assertIn('resolution', vm_data)
            self.assertIsInstance(vm_data['resolution'], str)
            self.assertIn('x', vm_data['resolution'])
            
            self.assertIn('created_at', vm_data)
            self.assertIn('updated_at', vm_data)
            
            self.assertIn('last_heartbeat', vm_data)
            # last_heartbeat pode ser None
    
    def test_pagination_removed(self):
        """Testa se a paginação foi removida corretamente"""
        url = reverse('vm_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verificar que não há campos de paginação
        self.assertNotIn('next', data)
        self.assertNotIn('previous', data)
        self.assertNotIn('count', data)
        self.assertNotIn('results', data)
        
        # Verificar que há campos corretos
        self.assertIn('vms', data)
        self.assertIn('total_count', data)
    
    def test_error_handling(self):
        """Testa o tratamento de erros"""
        # Testar com dados inválidos
        url = reverse('vm_list_create')
        invalid_data = {'invalid_field': 'invalid_value'}
        
        response = self.client.post(url, invalid_data, format='json')
        
        # Deve retornar erro 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('erro', data)
    
    def test_vm_list_get_with_invalid_filters(self):
        """Testa a listagem de VMs com filtros inválidos"""
        url = reverse('vm_list_create')
        
        # Filtros inválidos devem retornar erro 400
        response = self.client.get(url, {
            'status': 'invalid_status',
            'mode': 'invalid_mode'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('erro', data)
    
    def tearDown(self):
        """Limpeza após os testes"""
        # Remover todas as VMs criadas
        VirtualMachine.objects.all().delete()
        # Remover usuário de teste
        User.objects.all().delete()


class VirtualMachineModelTestCase(TestCase):
    """Testes específicos para o modelo VirtualMachine"""
    
    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='modeltestuser',
            email='modeltest@example.com',
            password='testpass123'
        )
    
    def test_vm_creation(self):
        """Testa criação básica de VM"""
        vm = VirtualMachine.objects.create(
            machine_id='TEST001',
            name='VM Teste',
            status='stopped',
            mode='TESTE',
            connection_status='disconnected',
            owner=self.user
        )
        
        self.assertEqual(vm.machine_id, 'TEST001')
        self.assertEqual(vm.name, 'VM Teste')
        self.assertEqual(vm.status, 'stopped')
        self.assertEqual(vm.mode, 'TESTE')
        self.assertTrue(vm.is_active)
        self.assertEqual(vm.owner, self.user)
    
    def test_vm_resolution_display(self):
        """Testa o método get_resolution_display"""
        vm = VirtualMachine.objects.create(
            machine_id='TEST002',
            name='VM Resolução',
            resolution_width=1920,
            resolution_height=1080,
            owner=self.user
        )
        
        resolution = vm.get_resolution_display()
        self.assertEqual(resolution, '1920x1080')
    
    def test_vm_default_values(self):
        """Testa valores padrão dos campos"""
        vm = VirtualMachine.objects.create(
            machine_id='TEST003',
            name='VM Defaults',
            owner=self.user
        )
        
        self.assertEqual(vm.port, 5000)
        self.assertEqual(vm.fps, 30)
        self.assertEqual(vm.trigger_interval_ms, 1000)
        self.assertEqual(vm.source_type, 'camera')
        self.assertEqual(vm.trigger_type, 'continuous')
        self.assertEqual(vm.inspection_config, {})
    
    def test_vm_string_representation(self):
        """Testa a representação string da VM"""
        vm = VirtualMachine.objects.create(
            machine_id='TEST004',
            name='VM String',
            owner=self.user
        )
        
        string_repr = str(vm)
        self.assertIn('VM String', string_repr)
        self.assertIn('TEST004', string_repr)
    
    def test_vm_choices_validation(self):
        """Testa validação dos campos de choice"""
        # Testar status válido
        vm = VirtualMachine.objects.create(
            machine_id='TEST005',
            name='VM Choices',
            status='running',
            mode='PRODUCAO',
            connection_status='connected',
            source_type='rtsp',
            trigger_type='interval',
            owner=self.user
        )
        
        self.assertEqual(vm.status, 'running')
        self.assertEqual(vm.mode, 'PRODUCAO')
        self.assertEqual(vm.connection_status, 'connected')
        self.assertEqual(vm.source_type, 'rtsp')
        self.assertEqual(vm.trigger_type, 'interval')
    
    def test_vm_field_constraints(self):
        """Testa restrições dos campos"""
        vm = VirtualMachine.objects.create(
            machine_id='TEST006',
            name='VM Constraints',
            port=8080,
            fps=60,
            trigger_interval_ms=500,
            owner=self.user
        )
        
        # Verificar que os valores estão dentro dos limites
        self.assertGreaterEqual(vm.port, 1)
        self.assertLessEqual(vm.port, 65535)
        self.assertGreaterEqual(vm.fps, 1)
        self.assertLessEqual(vm.fps, 120)
        self.assertGreaterEqual(vm.trigger_interval_ms, 100)
    
    def tearDown(self):
        """Limpeza"""
        VirtualMachine.objects.all().delete()
        User.objects.all().delete()
