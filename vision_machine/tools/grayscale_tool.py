import time
import cv2
import numpy as np
from typing import Dict, Any
from .base_tool import BaseTool

class GrayscaleTool(BaseTool):
    """Ferramenta para conversão de imagem para escala de cinza"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.method = config.get('method', 'luminance')
        self.normalize = config.get('normalize', True)
    
    def process(self, image: np.ndarray, roi_image: np.ndarray, 
                previous_results: Dict[int, Dict] = None) -> np.ndarray:
        """Converte para grayscale e retorna imagem processada"""
        start_time = time.time()
        
        try:
            # Garantir que a imagem de entrada seja RGB/BGR
            if len(roi_image.shape) == 3:  # RGB/BGR
                if self.method == 'luminance':
                    # Fórmula de luminância: 0.299*R + 0.587*G + 0.114*B
                    gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
                elif self.method == 'average':
                    gray = np.mean(roi_image, axis=2).astype(np.uint8)
                elif self.method == 'weighted':
                    # Peso personalizado para cada canal
                    weights = [0.3, 0.5, 0.2]  # B, G, R
                    gray = np.average(roi_image, axis=2, weights=weights).astype(np.uint8)
                else:
                    gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            else:
                # Se já for grayscale, converter para 3 canais primeiro
                if len(roi_image.shape) == 2:
                    roi_image = cv2.cvtColor(roi_image, cv2.COLOR_GRAY2BGR)
                gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            
            # Normalização se solicitado
            if self.normalize:
                gray = cv2.equalizeHist(gray)
            
            processing_time = (time.time() - start_time) * 1000  # em milissegundos
            
            # Armazenar tempo de processamento (será usado pelo processador)
            self.last_processing_time = processing_time
            
            return gray
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.last_processing_time = processing_time
            print(f"❌ Erro na ferramenta Grayscale {self.name}: {str(e)}")
            return roi_image
    
    def validate_config(self) -> bool:
        """Valida a configuração da ferramenta"""
        valid_methods = ['luminance', 'average', 'weighted']
        if self.method not in valid_methods:
            print(f"❌ Método inválido para GrayscaleTool: {self.method}")
            return False
        return True
