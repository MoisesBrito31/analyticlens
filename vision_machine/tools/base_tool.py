import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Union, Optional
import cv2
import numpy as np

class BaseTool(ABC):
    """Classe base para todas as ferramentas de inspeção"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.id = config.get('id')
        self.name = config.get('name')
        self.type = config.get('type')
        self.roi = config.get('ROI', {})
        self.inspec_pass_fail = config.get('inspec_pass_fail', False)
        self.reference_tool_id = config.get('reference_tool_id', None)
        
    @abstractmethod
    def process(self, image: np.ndarray, roi_image: np.ndarray, 
                previous_results: Dict[int, Dict] = None) -> Union[Dict[str, Any], np.ndarray]:
        """Processa a imagem e retorna resultados ou imagem processada"""
        pass
    
    def get_reference_result(self, previous_results: Dict[int, Dict], tool_id: int) -> Optional[Dict]:
        """Obtém resultado de uma ferramenta de referência"""
        if tool_id in previous_results:
            return previous_results[tool_id]
        else:
            print(f"⚠️ Ferramenta de referência {tool_id} não encontrada para {self.name}")
            return None
    
    def extract_roi(self, image: np.ndarray) -> np.ndarray:
        """Extrai região de interesse"""
        if not self.roi:
            return image
        
        # Obter dimensões da imagem
        img_height, img_width = image.shape[:2]
        
        x, y = self.roi.get('x', 0), self.roi.get('y', 0)
        w, h = self.roi.get('w', img_width), self.roi.get('h', img_height)
        
        # Validação e correção de ROI
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        w = min(w, img_width - x)
        h = min(h, img_height - y)
        
        # Verificar se o ROI é válido
        if w <= 0 or h <= 0:
            print(f"⚠️ ROI inválido para {self.name}: ({x},{y},{w},{h}) em imagem {img_width}x{img_height}")
            return image
        
        # Extrair ROI
        roi_image = image[y:y+h, x:x+w]
        
        print(f"🔍 {self.name}: ROI extraído ({x},{y},{w},{h}) -> {roi_image.shape}")
        
        return roi_image
    
    def is_filter_tool(self) -> bool:
        """Verifica se é ferramenta de filtro (modifica imagem)"""
        return self.type in ['grayscale', 'blur', 'sharpen', 'threshold']
    
    def is_analysis_tool(self) -> bool:
        """Verifica se é ferramenta de análise (gera resultados)"""
        return self.type in ['blob', 'edge', 'corner', 'template']
    
    def is_math_tool(self) -> bool:
        """Verifica se é ferramenta matemática (usa resultados de outras)"""
        return self.type in ['math', 'statistics', 'comparison']
    
    def validate_config(self) -> bool:
        """Valida a configuração da ferramenta (implementação base)"""
        return True
