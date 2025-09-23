import time
from typing import Dict, Any, List
import cv2
import numpy as np
from tools import (
    BlobTool,
    GrayscaleTool,
    MathTool,
    BlurFilterTool,
    ThresholdFilterTool,
    MorphologyFilterTool,
    LocateTool,
)

class InspectionProcessor:
    """Processador principal para coordenação das ferramentas de inspeção"""
    
    def __init__(self, inspection_config: Dict[str, Any]):
        self.config = inspection_config
        self.tools = []
        self.results = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Inicializa todas as ferramentas baseado na configuração"""
        tools_config = self.config.get('tools', [])
        if not tools_config:
            print("⚠️ Nenhuma ferramenta configurada para inspeção")
            return
            
        for tool_config in tools_config:
            tool = self._create_tool(tool_config)
            if tool:
                self.tools.append(tool)
                print(f"✅ Ferramenta {tool.name} (ID: {tool.id}, Tipo: {tool.type}) inicializada")
    
    def _create_tool(self, config: Dict[str, Any]):
        """Factory para criar ferramentas baseado no tipo"""
        tool_type = config.get('type')
        
        try:
            if tool_type == 'blob':
                return BlobTool(config)
            elif tool_type == 'grayscale':
                return GrayscaleTool(config)
            elif tool_type == 'blur':
                return BlurFilterTool(config)
            elif tool_type == 'threshold':
                return ThresholdFilterTool(config)
            elif tool_type == 'morphology':
                return MorphologyFilterTool(config)
            elif tool_type == 'locate':
                return LocateTool(config)
            elif tool_type == 'math':
                return MathTool(config)
            else:
                print(f"⚠️ Tipo de ferramenta não reconhecido: {tool_type}")
                return None
        except Exception as e:
            print(f"❌ Erro ao criar ferramenta {config.get('name', 'unknown')}: {str(e)}")
            return None
    
    def process_inspection(self, image: np.ndarray) -> Dict[str, Any]:
        """Executa o ciclo completo de inspeção seguindo a sequência da lista"""
        if not self.tools:
            print("⚠️ Nenhuma ferramenta disponível para processamento")
            return {
                'inspection_summary': {
                    'total_tools': 0,
                    'overall_pass': True,
                    'error': 'Nenhuma ferramenta configurada'
                },
                'tool_results': [],
                'final_image': image,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        self.results = {}
        current_image = image.copy()
        processed_images = {}  # Cache de imagens processadas por tipo
        total_start_time = time.time()
        
        print(f" Iniciando inspeção com {len(self.tools)} ferramentas...")
        
        for i, tool in enumerate(self.tools):
            print(f"  [{i+1}/{len(self.tools)}] Processando {tool.name} (ID: {tool.id}, Tipo: {tool.type})")
            
            try:
                # Extrair ROI (retorna também bbox/máscara através de atributos internos do tool)
                roi_image = tool.extract_roi(current_image)
                
                # Verificar se já temos uma imagem processada do tipo necessário
                if tool.type == 'blob' and 'grayscale' in processed_images:
                    print(f"    🔄 Usando imagem grayscale já processada para {tool.name}")
                    roi_image = tool.extract_roi(processed_images['grayscale'])
                
                # Processar com a ferramenta
                if tool.is_filter_tool():
                    # Ferramentas de filtro modificam a imagem
                    processed_image = tool.process(current_image, roi_image, self.results)
                    
                    # Armazenar imagem processada por tipo para reutilização
                    if tool.type == 'grayscale':
                        processed_images['grayscale'] = processed_image.copy()
                        print(f"    💾 Imagem grayscale armazenada para reutilização")
                    
                    # Aplica resultado de volta considerando shape/máscara
                    current_image = self._apply_roi_result(current_image, processed_image, getattr(tool, '_last_roi_bbox', None), getattr(tool, '_last_roi_mask', None))
                    
                    # Adicionar tempo de processamento
                    result = {
                        'tool_id': tool.id,
                        'tool_name': tool.name,
                        'tool_type': tool.type,
                        'status': 'success',
                        'image_modified': True,
                        'pass_fail': None,
                        'processing_time_ms': getattr(tool, 'last_processing_time', 0)
                    }
                    
                else:
                    # Ferramentas de análise/math geram resultados
                    result = tool.process(current_image, roi_image, self.results)
                    result['status'] = 'success'
                    result['image_modified'] = False
                
                # Armazenar resultado por chave estável (fallback para índice quando não houver ID)
                result_key = tool.id if tool.id is not None else f"idx_{i}"
                # Garantir que tool_id esteja preenchido no resultado para consumo do frontend
                if result.get('tool_id') is None:
                    result['tool_id'] = tool.id if tool.id is not None else i
                self.results[result_key] = result
                print(f"    ✅ {tool.name} processado em {result.get('processing_time_ms', 0):.2f}ms")
                
            except Exception as e:
                error_result = {
                    'tool_id': tool.id,
                    'tool_name': tool.name,
                    'tool_type': tool.type,
                    'status': 'error',
                    'error': str(e),
                    'pass_fail': False if tool.inspec_pass_fail else None,
                    'processing_time_ms': 0
                }
                self.results[tool.id] = error_result
                print(f"    ❌ Erro em {tool.name}: {str(e)}")
        
        total_processing_time = (time.time() - total_start_time) * 1000
        
        # Resultado final da inspeção
        return self._generate_final_result(current_image, total_processing_time)
    
    def _apply_roi_result(self, original_image: np.ndarray, roi_result: np.ndarray, bbox, mask) -> np.ndarray:
        """Aplica o resultado do ROI de volta à imagem original respeitando máscara (para circle/ellipse)."""
        if bbox is None:
            return roi_result

        x, y, w, h = bbox
        if w <= 0 or h <= 0:
            return original_image

        result_image = original_image.copy()

        # Compatibiliza canais
        if len(original_image.shape) == 3 and len(roi_result.shape) == 2:
            roi_result = cv2.cvtColor(roi_result, cv2.COLOR_GRAY2BGR)
        elif len(original_image.shape) == 2 and len(roi_result.shape) == 3:
            roi_result = cv2.cvtColor(roi_result, cv2.COLOR_BGR2GRAY)

        if x + w <= original_image.shape[1] and y + h <= original_image.shape[0]:
            if mask is None:
                # retângulo puro
                result_image[y:y+h, x:x+w] = roi_result
            else:
                # aplica somente onde mask > 0
                sub = result_image[y:y+h, x:x+w]
                if len(sub.shape) == 3:
                    mask3 = cv2.merge([mask, mask, mask])
                    np.copyto(sub, roi_result, where=mask3.astype(bool))
                else:
                    np.copyto(sub, roi_result, where=mask.astype(bool))
                result_image[y:y+h, x:x+w] = sub
        else:
            print(f"⚠️ ROI result ({w}x{h}) não cabe na posição ({x},{y}) da imagem original {original_image.shape}")

        return result_image
    
    def _generate_final_result(self, final_image: np.ndarray, total_time: float) -> Dict[str, Any]:
        """Gera resultado final da inspeção"""
        # Contar ferramentas com pass/fail
        pass_fail_tools = [r for r in self.results.values() if r.get('pass_fail') is not None]
        passed_tools = [r for r in pass_fail_tools if r['pass_fail']]
        
        # Calcular tempo total de processamento das ferramentas
        tools_processing_time = sum(
            r.get('processing_time_ms', 0) for r in self.results.values()
        )
        
        overall_result = {
            'inspection_summary': {
                'total_tools': len(self.tools),
                'successful_tools': len([r for r in self.results.values() if r['status'] == 'success']),
                'failed_tools': len([r for r in self.results.values() if r['status'] == 'error']),
                'pass_fail_tools': len(pass_fail_tools),
                'passed_tests': len(passed_tools),
                'overall_pass': len(pass_fail_tools) == 0 or len(passed_tools) == len(pass_fail_tools),
                'total_processing_time_ms': total_time,
                'tools_processing_time_ms': tools_processing_time,
                'overhead_time_ms': total_time - tools_processing_time
            },
            'tool_results': list(self.results.values()),  # Lista para manter ordem
            'final_image': final_image,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return overall_result
    
    def get_tool_by_id(self, tool_id: int):
        """Retorna uma ferramenta pelo ID"""
        for tool in self.tools:
            if tool.id == tool_id:
                return tool
        return None
    
    def get_tools_by_type(self, tool_type: str) -> List:
        """Retorna todas as ferramentas de um tipo específico"""
        return [tool for tool in self.tools if tool.type == tool_type]
    
    def validate_all_tools(self) -> bool:
        """Valida todas as ferramentas configuradas"""
        all_valid = True
        for tool in self.tools:
            if not tool.validate_config():
                print(f"❌ Ferramenta {tool.name} (ID: {tool.id}) falhou na validação")
                all_valid = False
        return all_valid
