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

        # Controle de extração e aproximação de contorno
        self.contour_chain = str(config.get('contour_chain', 'SIMPLE')).upper()  # SIMPLE | NONE | TC89_L1 | TC89_KCOS
        self.approx_epsilon_ratio = float(config.get('approx_epsilon_ratio', 0.01))  # fração do perímetro; 0 desabilita
        self.polygon_max_points = int(config.get('polygon_max_points', 0))  # 0 = sem limite
    
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
            
            # Aplicar threshold simples (análise interna, não altera imagem base do pipeline)
            _, binary = cv2.threshold(gray_image, self.th_min, self.th_max, cv2.THRESH_BINARY)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, self._chain_mode())
            
            # Filtrar por área
            valid_blobs = []
            total_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if self.area_min <= area <= self.area_max:
                    # Calcular centróide e bounding box
                    centroid = self._calculate_centroid(contour)
                    bbox = list(cv2.boundingRect(contour))

                    # Contorno com controle de fidelidade
                    poly = self._build_polygon_from_contour(contour)

                    # Informações para WebSocket (sem numpy)
                    valid_blobs.append({
                        'area': float(area),
                        'centroid': centroid,
                        'bounding_box': bbox,
                        'contour': poly  # Coordenadas no espaço do ROI
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

    # ----------------------
    # Métodos auxiliares
    # ----------------------

    def _chain_mode(self) -> int:
        """Mapeia configuração de cadeia de contorno para constante do OpenCV."""
        mode = self.contour_chain
        if mode == 'NONE':
            return cv2.CHAIN_APPROX_NONE
        if mode == 'TC89_L1':
            return cv2.CHAIN_APPROX_TC89_L1
        if mode == 'TC89_KCOS':
            return cv2.CHAIN_APPROX_TC89_KCOS
        return cv2.CHAIN_APPROX_SIMPLE

    def _build_polygon_from_contour(self, contour) -> List[List[int]]:
        """Gera polígono a partir do contorno com aproximação e amostragem opcional."""
        try:
            pts = contour
            # Aproximação controlada por epsilon (0 desabilita)
            if self.approx_epsilon_ratio and self.approx_epsilon_ratio > 0:
                peri = max(1e-6, cv2.arcLength(contour, True))
                epsilon = max(0.5, float(self.approx_epsilon_ratio) * peri)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                pts = approx
            # Converter para lista de pontos inteiros (x, y)
            pts_xy = pts.reshape(-1, 2).astype('int32')
            # Limitar número de pontos para performance, se configurado
            if self.polygon_max_points and self.polygon_max_points > 0 and len(pts_xy) > self.polygon_max_points:
                step = int(np.ceil(len(pts_xy) / float(self.polygon_max_points)))
                pts_xy = pts_xy[::max(1, step)]
            poly = pts_xy.tolist()
            # Garantir fechamento do polígono
            if len(poly) > 0 and (poly[0][0] != poly[-1][0] or poly[0][1] != poly[-1][1]):
                poly.append(poly[0])
            return poly
        except Exception:
            return []
