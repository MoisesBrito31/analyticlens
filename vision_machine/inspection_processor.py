import time
from typing import Dict, Any, List
import cv2
import numpy as np
from tools import (
    BlobTool,
    GrayscaleTool,
    MathTool,
    BlurFilterTool,
    ThresholdFilterTool,
    MorphologyFilterTool,
    LocateTool,
)

class InspectionProcessor:
    """Processador principal para coordenação das ferramentas de inspeção"""
    
    def __init__(self, inspection_config: Dict[str, Any]):
        self.config = inspection_config
        self.tools = []
        self.results = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Inicializa todas as ferramentas baseado na configuração"""
        tools_config = self.config.get('tools', [])
        if not tools_config:
            print("⚠️ Nenhuma ferramenta configurada para inspeção")
            return
            
        for tool_config in tools_config:
            tool = self._create_tool(tool_config)
            if tool:
                self.tools.append(tool)
                print(f"✅ Ferramenta {tool.name} (ID: {tool.id}, Tipo: {tool.type}) inicializada")
    
    def _create_tool(self, config: Dict[str, Any]):
        """Factory para criar ferramentas baseado no tipo"""
        tool_type = config.get('type')
        
        try:
            if tool_type == 'blob':
                return BlobTool(config)
            elif tool_type == 'grayscale':
                return GrayscaleTool(config)
            elif tool_type == 'blur':
                return BlurFilterTool(config)
            elif tool_type == 'threshold':
                return ThresholdFilterTool(config)
            elif tool_type == 'morphology':
                return MorphologyFilterTool(config)
            elif tool_type == 'locate':
                return LocateTool(config)
            elif tool_type == 'math':
                return MathTool(config)
            else:
                print(f"⚠️ Tipo de ferramenta não reconhecido: {tool_type}")
                return None
        except Exception as e:
            print(f"❌ Erro ao criar ferramenta {config.get('name', 'unknown')}: {str(e)}")
            return None
    
    def process_inspection(self, image: np.ndarray) -> Dict[str, Any]:
        """Executa o ciclo completo de inspeção seguindo a sequência da lista"""
        if not self.tools:
            print("⚠️ Nenhuma ferramenta disponível para processamento")
            return {
                'inspection_summary': {
                    'total_tools': 0,
                    'overall_pass': True,
                    'error': 'Nenhuma ferramenta configurada'
                },
                'tool_results': [],
                'final_image': image,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        self.results = {}
        current_image = image.copy()
        processed_images = {}  # Cache de imagens processadas por tipo
        total_start_time = time.time()
        
        print(f" Iniciando inspeção com {len(self.tools)} ferramentas...")
        
        for i, tool in enumerate(self.tools):
            print(f"  [{i+1}/{len(self.tools)}] Processando {tool.name} (ID: {tool.id}, Tipo: {tool.type})")
            
            try:
                # Extrair ROI (retorna também bbox/máscara através de atributos internos do tool)
                # Antes de extrair ROI, calcule offset acumulado de ferramentas anteriores com apply_transform=true
                try:
                    tx = self._compute_cumulative_offset(i)
                    if tx:
                        setattr(tool, '_transform_offset', tx)
                    else:
                        if hasattr(tool, '_transform_offset'):
                            delattr(tool, '_transform_offset')
                        # Sem offset: garantir ROI original
                        # (não altera tool.roi)
                except Exception:
                    pass
                roi_image = tool.extract_roi(current_image)
                
                # Verificar se já temos uma imagem processada do tipo necessário
                if tool.type == 'blob' and 'grayscale' in processed_images:
                    print(f"    🔄 Usando imagem grayscale já processada para {tool.name}")
                    roi_image = tool.extract_roi(processed_images['grayscale'])
                
                # Processar com a ferramenta
                if tool.is_filter_tool():
                    # Ferramentas de filtro modificam a imagem
                    processed_image = tool.process(current_image, roi_image, self.results)
                    
                    # Armazenar imagem processada por tipo para reutilização
                    if tool.type == 'grayscale':
                        processed_images['grayscale'] = processed_image.copy()
                        print(f"    💾 Imagem grayscale armazenada para reutilização")
                    
                    # Aplica resultado de volta considerando shape/máscara
                    current_image = self._apply_roi_result(current_image, processed_image, getattr(tool, '_last_roi_bbox', None), getattr(tool, '_last_roi_mask', None))
                    
                    # Adicionar tempo de processamento
                    result = {
                        'tool_id': tool.id,
                        'tool_name': tool.name,
                        'tool_type': tool.type,
                        'status': 'success',
                        'image_modified': True,
                        'pass_fail': None,
                        'processing_time_ms': getattr(tool, 'last_processing_time', 0)
                    }
                    # Injetar ROI efetivo usado (após transform)
                    try:
                        x, y, w, h = getattr(tool, '_last_roi_bbox', (None, None, None, None))
                        if all(v is not None for v in (x, y, w, h)) and w > 0 and h > 0:
                            result['ROI'] = { 'shape': 'rect', 'rect': { 'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h) } }
                        rd = getattr(tool, '_last_roi_debug', None)
                        if isinstance(rd, dict):
                            result['debug'] = result.get('debug') or {}
                            result['debug']['roi_debug'] = rd
                    except Exception:
                        pass
                    
                else:
                    # Ferramentas de análise/math geram resultados
                    result = tool.process(current_image, roi_image, self.results)
                    result['status'] = 'success'
                    result['image_modified'] = False
                    # Injetar ROI efetivo usado (após transform)
                    try:
                        x, y, w, h = getattr(tool, '_last_roi_bbox', (None, None, None, None))
                        if all(v is not None for v in (x, y, w, h)) and w > 0 and h > 0:
                            result['ROI'] = { 'shape': 'rect', 'rect': { 'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h) } }
                    except Exception:
                        pass
                    # Injeta debug do offset aplicado ao ROI se houver
                    try:
                        applied = getattr(tool, '_last_applied_offset', None)
                        result['debug'] = result.get('debug') or {}
                        result['debug']['roi_transform'] = {
                            'applied': bool(applied is not None),
                            'offset': applied if isinstance(applied, dict) else None
                        }
                        rd = getattr(tool, '_last_roi_debug', None)
                        if isinstance(rd, dict):
                            result['debug']['roi_debug'] = rd
                    except Exception:
                        pass
                
                # Armazenar resultado por chave estável (fallback para índice quando não houver ID)
                result_key = tool.id if tool.id is not None else f"idx_{i}"
                # Garantir que tool_id esteja preenchido no resultado para consumo do frontend
                if result.get('tool_id') is None:
                    result['tool_id'] = tool.id if tool.id is not None else i
                self.results[result_key] = result
                print(f"    ✅ {tool.name} processado em {result.get('processing_time_ms', 0):.2f}ms")
                
            except Exception as e:
                error_result = {
                    'tool_id': tool.id,
                    'tool_name': tool.name,
                    'tool_type': tool.type,
                    'status': 'error',
                    'error': str(e),
                    'pass_fail': False if tool.inspec_pass_fail else None,
                    'processing_time_ms': 0
                }
                self.results[tool.id] = error_result
                print(f"    ❌ Erro em {tool.name}: {str(e)}")
        
        total_processing_time = (time.time() - total_start_time) * 1000
        
        # Resultado final da inspeção
        return self._generate_final_result(current_image, total_processing_time)

    def _apply_offset_to_roi_copy(self, roi_obj, tx):
        import copy
        roi = copy.deepcopy(roi_obj) if isinstance(roi_obj, dict) else {}
        if not isinstance(tx, dict):
            return roi
        dx = float(tx.get('dx', 0.0) or 0.0)
        dy = float(tx.get('dy', 0.0) or 0.0)
        dth = float(tx.get('dtheta_deg', 0.0) or 0.0)
        rotate = bool(tx.get('rotate', False))
        shape = roi.get('shape')
        if shape == 'rect' or (not shape and all(k in roi for k in ('x','y','w','h'))):
            r = roi.get('rect', roi)
            r['x'] = int(round(float(r.get('x', 0)) + dx))
            r['y'] = int(round(float(r.get('y', 0)) + dy))
            if 'rect' in roi:
                roi['rect'] = r
            else:
                roi.update(r)
            if 'shape' not in roi:
                roi['shape'] = 'rect'
        elif shape == 'circle' and isinstance(roi.get('circle'), dict):
            c = roi['circle']
            c['cx'] = int(round(float(c.get('cx', 0)) + dx))
            c['cy'] = int(round(float(c.get('cy', 0)) + dy))
        elif shape == 'ellipse' and isinstance(roi.get('ellipse'), dict):
            e = roi['ellipse']
            e['cx'] = int(round(float(e.get('cx', 0)) + dx))
            e['cy'] = int(round(float(e.get('cy', 0)) + dy))
            if rotate:
                e['angle'] = float(e.get('angle', 0.0)) + dth
        return roi

    def _compute_cumulative_offset(self, upto_index: int):
        """Computa offset cumulativo (dx, dy, dtheta_deg) somando todas as ferramentas anteriores
        com apply_transform=true (tipicamente Locate) até o índice anterior a `upto_index`.

        Regras de composição (simples e robustas para coordenadas globais):
        - Somar dx e dy em coordenadas globais
        - Somar dtheta_deg apenas quando a ferramenta anterior tiver rotate=true
        - O flag rotate final é verdadeiro se qualquer ferramenta anterior tiver rotate=true
        """
        try:
            total_dx = 0.0
            total_dy = 0.0
            total_dth = 0.0
            any_rotate = False
            # percorrer do início até a ferramenta anterior (ordem natural de composição)
            for j in range(0, max(0, upto_index)):
                tool_j = self.tools[j]
                res_key = tool_j.id if tool_j.id is not None else f"idx_{j}"
                res = self.results.get(res_key)
                if not isinstance(res, dict):
                    continue
                # apply_transform pode vir na definição (tool.config) ou no result (eco)
                apply_tx = bool(getattr(tool_j, 'apply_transform', False))
                if 'apply_transform' in res:
                    try:
                        apply_tx = bool(res.get('apply_transform'))
                    except Exception:
                        pass
                if not apply_tx:
                    continue
                # localizar offset do padrão novo; se ausente, tentar derivar de reference/result
                off = res.get('offset') if isinstance(res.get('offset'), dict) else None
                ref = res.get('reference') if isinstance(res.get('reference'), dict) else None
                cur = res.get('result') if isinstance(res.get('result'), dict) else None
                dx = dy = dth = 0.0
                rot = bool(res.get('rotate', False))
                if off:
                    dx = float(off.get('x', 0.0) or 0.0)
                    dy = float(off.get('y', 0.0) or 0.0)
                    dth = float(off.get('angle_deg', 0.0) or 0.0)
                elif ref and cur:
                    try:
                        dx = float(cur.get('x', 0.0)) - float(ref.get('x', 0.0))
                        dy = float(cur.get('y', 0.0)) - float(ref.get('y', 0.0))
                        ca = float(cur.get('angle_deg', cur.get('angle', 0.0) or 0.0))
                        ra = float(ref.get('angle_deg', ref.get('angle', 0.0) or 0.0))
                        dth = float(ca - ra)
                    except Exception:
                        dx = dy = dth = 0.0
                else:
                    continue

                total_dx += float(dx)
                total_dy += float(dy)
                if rot:
                    any_rotate = True
                    total_dth += float(dth)

            if total_dx != 0.0 or total_dy != 0.0 or total_dth != 0.0:
                return {
                    'dx': float(total_dx),
                    'dy': float(total_dy),
                    'dtheta_deg': float(total_dth),
                    'rotate': bool(any_rotate)
                }
        except Exception:
            return None
        return None
    
    def _apply_roi_result(self, original_image: np.ndarray, roi_result: np.ndarray, bbox, mask) -> np.ndarray:
        """Aplica o resultado do ROI de volta à imagem original respeitando máscara (para circle/ellipse)."""
        if bbox is None:
            return roi_result

        x, y, w, h = bbox
        if w <= 0 or h <= 0:
            return original_image

        result_image = original_image.copy()

        # Compatibiliza canais
        if len(original_image.shape) == 3 and len(roi_result.shape) == 2:
            roi_result = cv2.cvtColor(roi_result, cv2.COLOR_GRAY2BGR)
        elif len(original_image.shape) == 2 and len(roi_result.shape) == 3:
            roi_result = cv2.cvtColor(roi_result, cv2.COLOR_BGR2GRAY)

        if x + w <= original_image.shape[1] and y + h <= original_image.shape[0]:
            if mask is None:
                # retângulo puro
                result_image[y:y+h, x:x+w] = roi_result
            else:
                # aplica somente onde mask > 0
                sub = result_image[y:y+h, x:x+w]
                if len(sub.shape) == 3:
                    mask3 = cv2.merge([mask, mask, mask])
                    np.copyto(sub, roi_result, where=mask3.astype(bool))
                else:
                    np.copyto(sub, roi_result, where=mask.astype(bool))
                result_image[y:y+h, x:x+w] = sub
        else:
            print(f"⚠️ ROI result ({w}x{h}) não cabe na posição ({x},{y}) da imagem original {original_image.shape}")

        return result_image
    
    def _generate_final_result(self, final_image: np.ndarray, total_time: float) -> Dict[str, Any]:
        """Gera resultado final da inspeção"""
        # Contar ferramentas com pass/fail
        pass_fail_tools = [r for r in self.results.values() if r.get('pass_fail') is not None]
        passed_tools = [r for r in pass_fail_tools if r['pass_fail']]
        
        # Calcular tempo total de processamento das ferramentas
        tools_processing_time = sum(
            r.get('processing_time_ms', 0) for r in self.results.values()
        )
        
        overall_result = {
            'inspection_summary': {
                'total_tools': len(self.tools),
                'successful_tools': len([r for r in self.results.values() if r['status'] == 'success']),
                'failed_tools': len([r for r in self.results.values() if r['status'] == 'error']),
                'pass_fail_tools': len(pass_fail_tools),
                'passed_tests': len(passed_tools),
                'overall_pass': len(pass_fail_tools) == 0 or len(passed_tools) == len(pass_fail_tools),
                'total_processing_time_ms': total_time,
                'tools_processing_time_ms': tools_processing_time,
                'overhead_time_ms': total_time - tools_processing_time
            },
            'tool_results': list(self.results.values()),  # Lista para manter ordem
            'final_image': final_image,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return overall_result
    
    def get_tool_by_id(self, tool_id: int):
        """Retorna uma ferramenta pelo ID"""
        for tool in self.tools:
            if tool.id == tool_id:
                return tool
        return None
    
    def get_tools_by_type(self, tool_type: str) -> List:
        """Retorna todas as ferramentas de um tipo específico"""
        return [tool for tool in self.tools if tool.type == tool_type]
    
    def validate_all_tools(self) -> bool:
        """Valida todas as ferramentas configuradas"""
        all_valid = True
        for tool in self.tools:
            if not tool.validate_config():
                print(f"❌ Ferramenta {tool.name} (ID: {tool.id}) falhou na validação")
                all_valid = False
        return all_valid
