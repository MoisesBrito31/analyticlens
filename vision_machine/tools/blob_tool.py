import time
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from .base_tool import BaseTool

class BlobTool(BaseTool):
    """Ferramenta para detecção e análise de blobs"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.th_min = config.get('th_min', 0)
        self.th_max = config.get('th_max', 255)
        self.area_min = config.get('area_min', 0)
        self.area_max = config.get('area_max', float('inf'))
        self.test_total_area_max = config.get('test_total_area_max', float('inf'))
        self.test_total_area_min = config.get('test_total_area_min', 0)
        self.test_blob_count_max = config.get('test_blob_count_max', float('inf'))
        self.test_blob_count_min = config.get('test_blob_count_min', 0)
        self.total_area_test = config.get('total_area_test', False)
        self.blob_count_test = config.get('blob_count_test', False)
    
    def process(self, image: np.ndarray, roi_image: np.ndarray, 
                previous_results: Dict[int, Dict] = None) -> Dict[str, Any]:
        """Processa imagem e retorna resultados de análise"""
        start_time = time.time()
        
        try:
            # A imagem já deve vir em grayscale da ferramenta grayscale
            # Se não estiver, converter (mas isso não deve acontecer no pipeline correto)
            if len(roi_image.shape) == 3:
                print(f"    ⚠️ {self.name}: Imagem recebida em RGB/BGR, convertendo para grayscale")
                gray_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = roi_image
                print(f"    ✅ {self.name}: Imagem recebida em grayscale (otimizado)")
            
            # Aplicar threshold
            _, binary = cv2.threshold(gray_image, self.th_min, self.th_max, cv2.THRESH_BINARY)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar por área
            valid_blobs = []
            total_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if self.area_min <= area <= self.area_max:
                    # Informações simplificadas para WebSocket (sem arrays numpy)
                    valid_blobs.append({
                        'area': float(area),  # Converter para float padrão
                        'centroid': self._calculate_centroid(contour),
                        'bounding_box': list(cv2.boundingRect(contour))  # Converter para lista
                    })
                    total_area += area
            
            # Calcular área do ROI para referência
            roi_area = roi_image.shape[0] * roi_image.shape[1]
            
            # Executar testes internos
            test_results = self._run_internal_tests(valid_blobs, total_area)
            
            processing_time = (time.time() - start_time) * 1000  # em milissegundos
            
            return {
                'tool_id': self.id,
                'tool_name': self.name,
                'tool_type': self.type,
                'processing_time_ms': processing_time,
                'blobs': valid_blobs,
                'blob_count': len(valid_blobs),
                'total_area': float(total_area),  # Garantir que seja float
                'roi_area': float(roi_area),      # Garantir que seja float
                'test_results': test_results,
                'pass_fail': test_results['overall_pass'] if self.inspec_pass_fail else None
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            print(f"❌ Erro na ferramenta Blob {self.name}: {str(e)}")
            return {
                'tool_id': self.id,
                'tool_name': self.name,
                'tool_type': self.type,
                'processing_time_ms': processing_time,
                'status': 'error',
                'error': str(e),
                'pass_fail': False if self.inspec_pass_fail else None
            }
    
    def _run_internal_tests(self, blobs: List, total_area: float) -> Dict[str, Any]:
        """Executa testes internos da ferramenta"""
        results = {}
        
        # Teste de área total
        if self.total_area_test:
            area_pass = self.test_total_area_min <= total_area <= self.test_total_area_max
            results['total_area_test'] = {
                'passed': area_pass,
                'min': float(self.test_total_area_min),
                'max': float(self.test_total_area_max),
                'actual': float(total_area)
            }
        
        # Teste de contagem de blobs
        if self.blob_count_test:
            count_pass = self.test_blob_count_min <= len(blobs) <= self.test_blob_count_max
            results['blob_count_test'] = {
                'passed': count_pass,
                'min': int(self.test_blob_count_min),
                'max': int(self.test_blob_count_max),
                'actual': int(len(blobs))
            }
        
        # Resultado geral dos testes
        if results:
            results['overall_pass'] = all(
                test_result['passed'] for test_result in results.values() 
                if isinstance(test_result, dict) and 'passed' in test_result
            )
        
        return results
    
    def _calculate_centroid(self, contour) -> Tuple[int, int]:
        """Calcula o centroide do contorno"""
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = 0, 0
        return (cx, cy)
    
    def validate_config(self) -> bool:
        """Valida a configuração da ferramenta"""
        required_fields = ['th_min', 'th_max', 'area_min', 'area_max']
        if not all(field in self.config for field in required_fields):
            print(f"❌ Campos obrigatórios ausentes para BlobTool: {required_fields}")
            return False
        
        if self.th_min >= self.th_max:
            print(f"❌ th_min deve ser menor que th_max")
            return False
        
        if self.area_min >= self.area_max:
            print(f"❌ area_min deve ser menor que area_max")
            return False
        
        return True
