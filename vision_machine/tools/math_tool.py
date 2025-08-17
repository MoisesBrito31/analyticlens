import time
import numpy as np
from typing import Dict, Any, Union
from .base_tool import BaseTool

class MathTool(BaseTool):
    """Ferramenta para operações matemáticas baseadas em resultados de outras ferramentas"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.operation = config.get('operation', '')
        self.formula = config.get('formula', '')
        self.reference_tool_id = config.get('reference_tool_id')
        
        if not self.reference_tool_id:
            raise ValueError(f"MathTool {self.name} deve ter reference_tool_id definido")
    
    def process(self, image: np.ndarray, roi_image: np.ndarray, 
                previous_results: Dict[int, Dict] = None) -> Dict[str, Any]:
        """Executa operação matemática baseada em resultado de outra ferramenta"""
        start_time = time.time()
        
        try:
            # Obter resultado da ferramenta de referência
            reference_result = self.get_reference_result(previous_results, self.reference_tool_id)
            if not reference_result:
                raise ValueError(f"Resultado da ferramenta {self.reference_tool_id} não encontrado")
            
            # Executar operação matemática
            math_result = self._execute_operation(reference_result)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'tool_id': self.id,
                'tool_name': self.name,
                'tool_type': self.type,
                'processing_time_ms': processing_time,
                'reference_tool_id': self.reference_tool_id,
                'operation': self.operation,
                'formula': self.formula,
                'result': math_result,
                'pass_fail': self._evaluate_result(math_result) if self.inspec_pass_fail else None
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            print(f"❌ Erro na ferramenta Math {self.name}: {str(e)}")
            return {
                'tool_id': self.id,
                'tool_name': self.name,
                'tool_type': self.type,
                'processing_time_ms': processing_time,
                'status': 'error',
                'error': str(e),
                'pass_fail': False if self.inspec_pass_fail else None
            }
    
    def _execute_operation(self, reference_result: Dict) -> float:
        """Executa a operação matemática definida"""
        if self.operation == 'area_ratio':
            # Exemplo: área total / área do ROI
            total_area = reference_result.get('total_area', 0)
            roi_area = reference_result.get('roi_area', 1)
            return total_area / roi_area if roi_area > 0 else 0
            
        elif self.operation == 'blob_density':
            # Exemplo: número de blobs / área do ROI
            blob_count = reference_result.get('blob_count', 0)
            roi_area = reference_result.get('roi_area', 1)
            return blob_count / roi_area if roi_area > 0 else 0
            
        elif self.operation == 'custom_formula':
            # Executar fórmula customizada (implementação básica)
            return self._evaluate_custom_formula(reference_result)
        
        else:
            raise ValueError(f"Operação {self.operation} não suportada")
    
    def _evaluate_custom_formula(self, reference_result: Dict) -> float:
        """Avalia fórmula customizada (implementação básica)"""
        # Substituir variáveis na fórmula
        formula = self.formula
        for key, value in reference_result.items():
            if isinstance(value, (int, float)):
                formula = formula.replace(key, str(value))
        
        try:
            # Avaliar fórmula (cuidado com segurança!)
            return eval(formula)
        except Exception as e:
            raise ValueError(f"Erro ao avaliar fórmula: {str(e)}")
    
    def _evaluate_result(self, result: float) -> bool:
        """Avalia se o resultado matemático passa nos critérios"""
        # Implementar lógica de avaliação baseada na operação
        if self.operation == 'area_ratio':
            return 0.1 <= result <= 0.9  # Exemplo: razão entre 10% e 90%
        elif self.operation == 'blob_density':
            return 0.01 <= result <= 0.1  # Exemplo: densidade entre 1% e 10%
        return True  # Por padrão, passa
    
    def validate_config(self) -> bool:
        """Valida a configuração da ferramenta"""
        if not self.reference_tool_id:
            print(f"❌ reference_tool_id é obrigatório para MathTool")
            return False
        
        if not self.operation:
            print(f"❌ operation é obrigatório para MathTool")
            return False
        
        valid_operations = ['area_ratio', 'blob_density', 'custom_formula']
        if self.operation not in valid_operations:
            print(f"❌ Operação {self.operation} não suportada")
            return False
        
        if self.operation == 'custom_formula' and not self.formula:
            print(f"❌ formula é obrigatório para operação custom_formula")
            return False
        
        return True
