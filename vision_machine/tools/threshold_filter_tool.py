import time
import cv2
import numpy as np
from typing import Dict, Any
from .base_tool import BaseTool


class ThresholdFilterTool(BaseTool):
    """Filtro de threshold (binário / faixa / Otsu) que altera a imagem do pipeline."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mode = str(config.get('mode', 'binary')).lower()  # 'binary' | 'range' | 'otsu'
        self.th_min = int(config.get('th_min', 128))
        self.th_max = int(config.get('th_max', 255))

    def process(self, image: np.ndarray, roi_image: np.ndarray,
                previous_results: Dict[int, Dict] = None) -> np.ndarray:
        start_time = time.time()
        try:
            # Garantir grayscale para limiarização
            if len(roi_image.shape) == 3:
                gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = roi_image

            if self.mode == 'range':
                lo = int(max(0, min(255, self.th_min)))
                hi = int(max(lo, min(255, self.th_max)))
                out = cv2.inRange(gray, lo, hi)
            elif self.mode == 'otsu':
                _, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            else:
                # binary
                _, out = cv2.threshold(gray, int(self.th_min), int(self.th_max), cv2.THRESH_BINARY)

            self.last_processing_time = (time.time() - start_time) * 1000
            return out
        except Exception:
            self.last_processing_time = (time.time() - start_time) * 1000
            return roi_image

    def validate_config(self) -> bool:
        return True


