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
        """Extrai região de interesse (ROI). Suporta rect (legacy), circle e ellipse via máscara."""
        if not self.roi:
            # Nenhum ROI: a ferramenta trabalha a imagem inteira
            self._last_roi_bbox = (0, 0, image.shape[1], image.shape[0])
            self._last_roi_mask = None
            return image

        img_height, img_width = image.shape[:2]

        # Back-compat: se vier no formato antigo, tratar como retângulo
        is_legacy_rect = all(k in self.roi for k in ('x', 'y', 'w', 'h')) and 'shape' not in self.roi
        shape = self.roi.get('shape', 'rect' if is_legacy_rect else self.roi.get('shape', 'rect'))

        # Funções auxiliares
        def clamp_bbox(x: int, y: int, w: int, h: int):
            x = max(0, min(x, img_width - 1))
            y = max(0, min(y, img_height - 1))
            w = max(0, min(w, img_width - x))
            h = max(0, min(h, img_height - y))
            return x, y, w, h

        mask = None
        if shape == 'rect':
            # Pode vir como ROI antigo ({x,y,w,h}) ou aninhado em roi['rect']
            r = self.roi.get('rect', self.roi)
            x, y = int(r.get('x', 0)), int(r.get('y', 0))
            w, h = int(r.get('w', img_width)), int(r.get('h', img_height))
            x, y, w, h = clamp_bbox(x, y, w, h)
            if w <= 0 or h <= 0:
                print(f"⚠️ ROI inválido para {self.name}: ({x},{y},{w},{h}) em imagem {img_width}x{img_height}")
                self._last_roi_bbox = (0, 0, 0, 0)
                self._last_roi_mask = None
                return image
            roi_image = image[y:y+h, x:x+w]
            mask = np.ones((h, w), dtype=np.uint8) * 255

        elif shape == 'circle':
            c = self.roi.get('circle', {})
            cx, cy = int(c.get('cx', 0)), int(c.get('cy', 0))
            r = int(c.get('r', 0))
            if r <= 0:
                print(f"⚠️ ROI círculo inválido para {self.name}: (cx={cx}, cy={cy}, r={r})")
                self._last_roi_bbox = (0, 0, 0, 0)
                self._last_roi_mask = None
                return image
            x, y = cx - r, cy - r
            w, h = 2 * r, 2 * r
            x, y, w, h = clamp_bbox(x, y, w, h)
            if w <= 0 or h <= 0:
                print(f"⚠️ ROI círculo fora dos limites para {self.name}")
                self._last_roi_bbox = (0, 0, 0, 0)
                self._last_roi_mask = None
                return image
            roi_image = image[y:y+h, x:x+w]
            mask = np.zeros((h, w), dtype=np.uint8)
            # centro relativo após clamp
            rel_cx = min(max(r, 0), w - 1)
            rel_cy = min(max(r, 0), h - 1)
            cv2.circle(mask, (rel_cx, rel_cy), min(r, w - 1, h - 1), 255, -1)

        elif shape == 'ellipse':
            e = self.roi.get('ellipse', {})
            cx, cy = int(e.get('cx', 0)), int(e.get('cy', 0))
            rx, ry = int(e.get('rx', 0)), int(e.get('ry', 0))
            angle = float(e.get('angle', 0.0))
            if rx <= 0 or ry <= 0:
                print(f"⚠️ ROI elipse inválido para {self.name}: (cx={cx}, cy={cy}, rx={rx}, ry={ry})")
                self._last_roi_bbox = (0, 0, 0, 0)
                self._last_roi_mask = None
                return image
            x, y = cx - rx, cy - ry
            w, h = 2 * rx, 2 * ry
            x, y, w, h = clamp_bbox(x, y, w, h)
            if w <= 0 or h <= 0:
                print(f"⚠️ ROI elipse fora dos limites para {self.name}")
                self._last_roi_bbox = (0, 0, 0, 0)
                self._last_roi_mask = None
                return image
            roi_image = image[y:y+h, x:x+w]
            mask = np.zeros((h, w), dtype=np.uint8)
            # centro relativo após clamp
            rel_cx = min(max(rx, 0), w - 1)
            rel_cy = min(max(ry, 0), h - 1)
            cv2.ellipse(mask, (rel_cx, rel_cy), (min(rx, w - 1), min(ry, h - 1)), angle, 0, 360, 255, -1)

        else:
            # Desconhecido: cai no comportamento antigo, evitando quebra
            x, y = int(self.roi.get('x', 0)), int(self.roi.get('y', 0))
            w, h = int(self.roi.get('w', img_width)), int(self.roi.get('h', img_height))
            x, y, w, h = clamp_bbox(x, y, w, h)
            roi_image = image[y:y+h, x:x+w]
            mask = np.ones((h, w), dtype=np.uint8) * 255

        self._last_roi_bbox = (x, y, w, h)
        self._last_roi_mask = mask
        print(f"🔍 {self.name}: ROI extraído shape={shape} bbox=({x},{y},{w},{h}) -> {roi_image.shape}")
        return roi_image
    
    def is_filter_tool(self) -> bool:
        """Verifica se é ferramenta de filtro (modifica imagem)"""
        return self.type in ['grayscale', 'blur', 'sharpen', 'threshold', 'morphology']
    
    def is_analysis_tool(self) -> bool:
        """Verifica se é ferramenta de análise (gera resultados)"""
        return self.type in ['blob', 'edge', 'corner', 'template']
    
    def is_math_tool(self) -> bool:
        """Verifica se é ferramenta matemática (usa resultados de outras)"""
        return self.type in ['math', 'statistics', 'comparison']
    
    def validate_config(self) -> bool:
        """Valida a configuração da ferramenta (implementação base)"""
        return True
