import time
import math
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np

from .base_tool import BaseTool


class LocateTool(BaseTool):
    """Ferramenta de localização por borda ao longo de uma seta (linha dirigida).

    Parâmetros esperados no config:
      - arrow: { p0: {x,y}, p1: {x,y} }  (coordenadas globais da imagem)
        (alternativamente em ROI.arrow)
      - threshold_mode: 'fixed' | 'adaptive' (padrão: 'fixed')
      - th_min: int (para 'fixed', mínimo de |grad| ou grad conforme polaridade)
      - th_max: int (reservado, não usado neste algoritmo)
      - adaptive_k: float (padrão 1.0), fator para mean + k*std no modo 'adaptive'
      - polaridade: 'dark_to_light' | 'light_to_dark' | 'any' (padrão: 'any')
      - edge_select: 'first' | 'strongest' | 'closest_to_mid' (padrão 'strongest')
      - smooth_ksize: int (ímpar, padrão 5) suavização 1D do perfil
      - grad_kernel: int (1,3,5; padrão 3) janela para Sobel no cálculo de ângulo 2D
      - reference: { x: float, y: float, angle | angle_deg: float }  (opcional)
      - rotate: bool (opcional; se true, offset inclui rotação; senão mantém ângulo da referência)
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.threshold_mode = str(config.get('threshold_mode', 'fixed')).lower()
        # Novo: limiar único
        self.threshold = float(config.get('threshold', config.get('th_min', 20.0)))
        self.adaptive_k = float(config.get('adaptive_k', 1.0))
        self.polaridade = str(config.get('polaridade', 'any')).lower()
        self.edge_select = str(config.get('edge_select', 'strongest')).lower()
        self.smooth_ksize = int(config.get('smooth_ksize', 5))
        self.grad_kernel = int(config.get('grad_kernel', 3))
        # Echo de apply_transform no result (valor de config)
        try:
            self.apply_transform = bool(config.get('apply_transform', False))
        except Exception:
            self.apply_transform = False
        # Referência opcional para cálculo de offset (x, y, angle_deg)
        self.reference = self._parse_reference(config.get('reference'))
        # Controle de rotação no offset
        try:
            self.rotate = bool(config.get('rotate', False))
        except Exception:
            self.rotate = False

    def process(self, image: np.ndarray, roi_image: np.ndarray,
                previous_results: Dict[int, Dict] = None) -> Dict[str, Any]:
        start_time = time.time()

        try:
            # Garantir grayscale para análise
            if len(roi_image.shape) == 3:
                gray_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_roi = roi_image

            # Obter seta (p0, p1) em coordenadas globais e convertê-las para locais do ROI
            p0_g, p1_g = self._get_arrow_points_global(image.shape)
            x_off, y_off, w_roi, h_roi = getattr(self, '_last_roi_bbox', (0, 0, image.shape[1], image.shape[0]))
            p0 = (float(p0_g[0] - x_off), float(p0_g[1] - y_off))
            p1 = (float(p1_g[0] - x_off), float(p1_g[1] - y_off))

            # Amostrar intensidades ao longo da seta
            samples_xy, intens = self._sample_along_line(gray_roi, p0, p1)

            # Suavizar sinal 1D
            intens_s = self._smooth_1d(intens, self.smooth_ksize)

            # Gradiente 1D ao longo da seta
            grad_1d = np.gradient(intens_s)

            # 1) Primeira estratégia: cruzamento de nível de intensidade no valor 'threshold'
            #    Isso permite escolher explicitamente a borda próxima a um tom desejado
            level_T = float(max(0.0, min(255.0, self.threshold)))
            lvl_peaks = self._find_level_crossings(intens_s, level_T)

            # 2) Estratégia de gradiente (magnitude do bordo)
            #    Usada para ranking e fallback quando não há cruzamentos de nível
            th = self._compute_threshold(grad_1d)
            try:
                max_grad = float(np.max(np.abs(grad_1d))) if grad_1d.size else 0.0
            except Exception:
                max_grad = 0.0
            # Ajuste de segurança: se threshold > max_grad, reduza para fração do pico
            if max_grad > 0 and th > max_grad:
                th = max(1.0, 0.5 * max_grad)

            # Detectar picos (bordas) por gradiente
            grad_peaks = self._find_peaks(grad_1d, th)
            # Fallback: se nada encontrado e modo fixo, tente adaptativo
            if not grad_peaks and self.threshold_mode != 'adaptive':
                th_adapt = self._compute_threshold(grad_1d.astype(np.float32)) if True else th
                grad_peaks = self._find_peaks(grad_1d, th_adapt)
                if grad_peaks:
                    th = th_adapt

            # Escolher base inicial para seleção: priorizar cruzamentos de nível, se existirem
            base_candidates = lvl_peaks if len(lvl_peaks) > 0 else grad_peaks
            # Selecionar UM índice conforme política
            selected_idx = self._select_single_edge(base_candidates, grad_1d, len(intens_s))
            selected = [selected_idx] if selected_idx is not None else []

            # Calcular ângulo local pela orientação do gradiente 2D (Sobel)
            gx, gy = self._sobel_gradients(gray_roi)

            edges: List[Dict[str, Any]] = []
            for idx in selected:
                px, py = samples_xy[idx]
                # Coordenadas globais
                gx_i = int(round(px))
                gy_i = int(round(py))
                gx_i = max(0, min(gx.shape[1] - 1, gx_i))
                gy_i = max(0, min(gx.shape[0] - 1, gy_i))
                gxi = float(gx[gy_i, gx_i])
                gyi = float(gy[gy_i, gx_i])

                # Ângulo do gradiente e do bordo (gradiente ⟂ bordo)
                grad_ang = math.degrees(math.atan2(gyi, gxi))
                edge_ang = self._normalize_angle(grad_ang + 90.0)

                # Força do pico
                strength = float(abs(grad_1d[idx]))

                edges.append({
                    'x': float(px + x_off),
                    'y': float(py + y_off),
                    'angle_deg': float(edge_ang),
                    'polarity': self._infer_polarity_at(grad_1d[idx]),
                    'strength': strength,
                    't': float(idx) / max(1.0, float(len(intens_s) - 1))
                })

            # Escolha primária (resultado atual)
            primary = edges[0] if edges else None

            processing_time = (time.time() - start_time) * 1000.0
            # Preparar seções padronizadas
            reference_out = None
            offset_out = None
            result_out = None

            if primary is not None:
                result_out = {
                    'x': float(primary['x']),
                    'y': float(primary['y']),
                    'angle_deg': float(primary['angle_deg'])
                }
                if self.reference is not None:
                    reference_out = {
                        'x': float(self.reference['x']),
                        'y': float(self.reference['y']),
                        'angle_deg': float(self.reference['angle_deg'])
                    }
                    dx = float(result_out['x']) - float(reference_out['x'])
                    dy = float(result_out['y']) - float(reference_out['y'])
                    dA = self._normalize_angle(float(result_out['angle_deg']) - float(reference_out['angle_deg']))
                    offset_out = {
                        'x': float(dx),
                        'y': float(dy),
                        'angle_deg': float(dA) if bool(self.rotate) else float(reference_out['angle_deg'])
                    }

            return {
                'tool_id': self.id,
                'tool_name': self.name,
                'tool_type': self.type,
                'processing_time_ms': processing_time,
                'edges': edges,
                'edge_count': len(edges),
                # Compatibilidade anterior
                'primary_point': {'x': primary['x'], 'y': primary['y']} if primary else None,
                'primary_angle_deg': primary['angle_deg'] if primary else None,
                # Novos blocos padronizados
                'reference': reference_out,
                'result': result_out,
                'offset': offset_out,
                'rotate': bool(self.rotate),
                'apply_transform': bool(self.apply_transform),
                'arrow': {
                    'p0': {'x': float(p0_g[0]), 'y': float(p0_g[1])},
                    'p1': {'x': float(p1_g[0]), 'y': float(p1_g[1])}
                },
                'pass_fail': None if not self.inspec_pass_fail else True
            }

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000.0
            return {
                'tool_id': self.id,
                'tool_name': self.name,
                'tool_type': self.type,
                'processing_time_ms': processing_time,
                'status': 'error',
                'error': str(e),
                'pass_fail': False if self.inspec_pass_fail else None
            }

    # ----------------------
    # Utilidades internas
    # ----------------------
    def _get_arrow_points_global(self, img_shape: Tuple[int, int, int]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        h, w = img_shape[0], img_shape[1]
        arrow = self.config.get('arrow') or self.roi.get('arrow') or {}
        def _pt(key: str, default_xy: Tuple[float, float]):
            p = arrow.get(key) or {}
            x = float(p.get('x', default_xy[0]))
            y = float(p.get('y', default_xy[1]))
            return (max(0.0, min(float(w - 1), x)), max(0.0, min(float(h - 1), y)))

        # Fallback: seta horizontal no centro do ROI/bbox
        x_off, y_off, bw, bh = getattr(self, '_last_roi_bbox', (0, 0, w, h))
        default_p0 = (x_off + 0.1 * bw, y_off + 0.5 * bh)
        default_p1 = (x_off + 0.9 * bw, y_off + 0.5 * bh)

        p0 = _pt('p0', default_p0)
        p1 = _pt('p1', default_p1)
        return p0, p1

    def _sample_along_line(self, gray: np.ndarray, p0: Tuple[float, float], p1: Tuple[float, float]) -> Tuple[List[Tuple[float, float]], np.ndarray]:
        x0, y0 = p0
        x1, y1 = p1
        dx = x1 - x0
        dy = y1 - y0
        length = max(1.0, float(math.hypot(dx, dy)))
        num = max(10, int(round(length)))
        ts = np.linspace(0.0, 1.0, num=num, dtype=np.float32)
        xs = x0 + ts * dx
        ys = y0 + ts * dy

        # Amostragem por vizinho mais próximo (rápido e suficiente para V1)
        xi = np.clip(np.round(xs).astype(np.int32), 0, gray.shape[1] - 1)
        yi = np.clip(np.round(ys).astype(np.int32), 0, gray.shape[0] - 1)
        intens = gray[yi, xi].astype(np.float32)
        samples_xy = list(zip(xs.tolist(), ys.tolist()))
        return samples_xy, intens

    def _smooth_1d(self, signal: np.ndarray, ksize: int) -> np.ndarray:
        try:
            k = int(ksize) if int(ksize) % 2 == 1 else int(ksize) + 1
            k = max(1, k)
            arr = signal.reshape(1, -1).astype(np.float32)
            if k >= 3:
                out = cv2.GaussianBlur(arr, (k, 1), 0)
            else:
                out = arr
            return out.reshape(-1)
        except Exception:
            return signal

    def _compute_threshold(self, grad_1d: np.ndarray) -> float:
        if self.threshold_mode == 'adaptive':
            g = grad_1d.astype(np.float32)
            if self.polaridade == 'dark_to_light':
                g = np.maximum(g, 0.0)
            elif self.polaridade == 'light_to_dark':
                g = np.maximum(-g, 0.0)
            else:
                g = np.abs(g)
            mean = float(np.mean(g))
            std = float(np.std(g))
            return max(1.0, mean + float(self.adaptive_k) * std)
        else:
            return float(max(1.0, self.threshold))

    def _find_peaks(self, grad_1d: np.ndarray, th: float) -> List[int]:
        g = grad_1d
        if self.polaridade == 'dark_to_light':
            mask = g >= th
        elif self.polaridade == 'light_to_dark':
            mask = (-g) >= th
        else:
            mask = np.abs(g) >= th

        idxs = np.where(mask)[0].tolist()
        if not idxs:
            return []
        # Reduzir para picos locais simples: manter índices que são maiores (em magnitude) que vizinhos imediatos
        peaks = []
        for i in idxs:
            left = abs(g[i - 1]) if i - 1 >= 0 else -1e9
            right = abs(g[i + 1]) if i + 1 < g.shape[0] else -1e9
            if abs(g[i]) >= left and abs(g[i]) >= right:
                peaks.append(i)
        # Remover picos muito próximos (janela mínima de 2 px)
        dedup = []
        last = -10
        for i in peaks:
            if i - last >= 2:
                dedup.append(i)
                last = i
        return dedup

    def _select_single_edge(self, peaks: List[int], grad_1d: np.ndarray, n: int) -> int | None:
        if not peaks:
            return None
        if self.edge_select == 'first':
            return sorted(peaks)[0]
        if self.edge_select == 'closest_to_mid':
            mid = (n - 1) / 2.0
            return sorted(peaks, key=lambda i: abs(i - mid))[0]
        # strongest (default)
        return sorted(peaks, key=lambda i: abs(float(grad_1d[i])), reverse=True)[0]

    def _find_level_crossings(self, intens: np.ndarray, T: float) -> List[int]:
        if intens is None or intens.size < 2:
            return []
        vals = intens.astype(np.float32)
        # Sinais de comparação
        below = vals[:-1] < T
        above_or_eq = vals[1:] >= T
        above = vals[:-1] > T
        below_or_eq = vals[1:] <= T
        # Polarity masks
        if self.polaridade == 'dark_to_light':
            mask = np.logical_and(below, above_or_eq)
        elif self.polaridade == 'light_to_dark':
            mask = np.logical_and(above, below_or_eq)
        else:
            mask = np.logical_or(
                np.logical_and(below, above_or_eq),
                np.logical_and(above, below_or_eq)
            )
        idxs = np.where(mask)[0] + 1  # escolhe o índice da amostra "superior" do cruzamento
        return idxs.tolist()

    def _sobel_gradients(self, gray: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        k = 1 if self.grad_kernel not in (3, 5, 7) else self.grad_kernel
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=k)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=k)
        return gx, gy

    def _infer_polarity_at(self, grad_value: float) -> str:
        if self.polaridade == 'any':
            return 'dark_to_light' if grad_value >= 0 else 'light_to_dark'
        return self.polaridade

    def _normalize_angle(self, ang: float) -> float:
        a = float(ang)
        while a <= -180.0:
            a += 360.0
        while a > 180.0:
            a -= 360.0
        return a

    def _parse_reference(self, ref_like: Any) -> Dict[str, float] | None:
        try:
            if not isinstance(ref_like, dict):
                return None
            x = float(ref_like.get('x')) if ref_like.get('x') is not None else None
            y = float(ref_like.get('y')) if ref_like.get('y') is not None else None
            # aceitar 'angle' ou 'angle_deg'
            ang_raw = ref_like.get('angle_deg')
            if ang_raw is None:
                ang_raw = ref_like.get('angle')
            ang = float(ang_raw) if ang_raw is not None else None
            if x is None or y is None or ang is None:
                return None
            # normalizar ângulo para [-180, 180]
            ang = self._normalize_angle(float(ang))
            return {'x': x, 'y': y, 'angle_deg': ang}
        except Exception:
            return None


