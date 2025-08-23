import time
import cv2
import numpy as np
from typing import Dict, Any
from .base_tool import BaseTool


class MorphologyFilterTool(BaseTool):
    """Filtro morfológico (abertura/fechamento) que altera a imagem do pipeline."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.kernel = int(config.get('kernel', 3))  # ímpar >= 3
        self.open = int(config.get('open', 0))
        self.close = int(config.get('close', 0))
        self.shape = str(config.get('shape', 'ellipse')).lower()  # 'ellipse' | 'rect' | 'cross'

    def process(self, image: np.ndarray, roi_image: np.ndarray,
                previous_results: Dict[int, Dict] = None) -> np.ndarray:
        start_time = time.time()
        try:
            k = max(3, self.kernel | 1)
            if self.shape == 'rect':
                ks = cv2.MORPH_RECT
            elif self.shape == 'cross':
                ks = cv2.MORPH_CROSS
            else:
                ks = cv2.MORPH_ELLIPSE
            se = cv2.getStructuringElement(ks, (k, k))
            out = roi_image
            if self.open > 0:
                out = cv2.morphologyEx(out, cv2.MORPH_OPEN, se, iterations=self.open)
            if self.close > 0:
                out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, se, iterations=self.close)
            self.last_processing_time = (time.time() - start_time) * 1000
            return out
        except Exception:
            self.last_processing_time = (time.time() - start_time) * 1000
            return roi_image

    def validate_config(self) -> bool:
        return True


