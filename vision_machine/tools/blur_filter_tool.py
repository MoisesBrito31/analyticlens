import time
import cv2
import numpy as np
from typing import Dict, Any
from .base_tool import BaseTool


class BlurFilterTool(BaseTool):
    """Filtro de suavização (Gaussian/Median) que altera a imagem do pipeline."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.method = config.get('method', 'gaussian')  # 'gaussian' | 'median'
        self.ksize = int(config.get('ksize', 3))  # ímpar >= 3
        self.sigma = float(config.get('sigma', 0))  # usado no gaussian

    def process(self, image: np.ndarray, roi_image: np.ndarray,
                previous_results: Dict[int, Dict] = None) -> np.ndarray:
        start_time = time.time()
        try:
            out = roi_image
            k = max(3, self.ksize | 1)
            if self.method == 'median':
                # Median blur requer imagem de 1 ou 3 canais
                if len(roi_image.shape) == 2:
                    out = cv2.medianBlur(roi_image, k)
                else:
                    out = cv2.medianBlur(roi_image, k)
            else:
                # Gaussian por padrão
                out = cv2.GaussianBlur(roi_image, (k, k), self.sigma)

            self.last_processing_time = (time.time() - start_time) * 1000
            return out
        except Exception:
            self.last_processing_time = (time.time() - start_time) * 1000
            return roi_image

    def validate_config(self) -> bool:
        return True


