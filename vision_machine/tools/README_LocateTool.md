# LocateTool - Guia de Configuração e Uso

Projeto Principal: ver `vision_machine/TOOLS_README.md` e `vision_machine/README.md`

## Visão Geral

A LocateTool localiza uma borda ao longo de uma seta (linha dirigida dentro do ROI) e retorna:
- reference: ponto/ângulo base (opcional)
- result: ponto/ângulo detectado
- offset: diferença entre result e reference (dx, dy, dtheta_deg quando rotate=true)
- rotate/apply_transform ecoados no resultado
- lista de edges avaliados (com força e ângulo)

Quando `apply_transform=true`, o offset é aplicado às ROIs das ferramentas seguintes. Offsets são acumulados ao longo do pipeline (dx/dy sempre somam; `dtheta_deg` soma apenas das tools com `rotate=true`).

## Parâmetros de Configuração

- threshold_mode: `fixed | adaptive` (padrão: `fixed`)
- threshold: número (padrão: 20) quando `fixed`
- adaptive_k: número (padrão: 1.0) quando `adaptive`
- polaridade: `dark_to_light | light_to_dark | any` (padrão: `any`)
- edge_select: `first | strongest | closest_to_mid` (padrão: `strongest`)
- smooth_ksize: ímpar, padrão 5
- grad_kernel: 1,3,5 (padrão 3)
- apply_transform: boolean (padrão false)
- rotate: boolean (padrão false)
- reference: `{ x, y, angle_deg } | null`
- arrow: `{ p0: {x,y}, p1: {x,y} }` (coordenadas globais)

## Exemplo de Configuração

```
{
  "id": 10,
  "name": "locate_1",
  "type": "locate",
  "ROI": {"shape": "rect", "rect": {"x": 0, "y": 0, "w": 640, "h": 480}},
  "threshold_mode": "fixed",
  "threshold": 140,
  "adaptive_k": 1,
  "polaridade": "dark_to_light",
  "edge_select": "first",
  "smooth_ksize": 5,
  "grad_kernel": 3,
  "apply_transform": true,
  "rotate": false,
  "reference": { "x": 363.0167, "y": 39.0167, "angle_deg": 180 },
  "arrow": { "p0": { "x": 363, "y": 32 }, "p1": { "x": 364, "y": 452 } }
}
```

## Exemplo de Resultado

```
{
  "tool_id": 10,
  "tool_name": "locate_1",
  "tool_type": "locate",
  "processing_time_ms": 2.91,
  "edges": [{"x": 364.0, "y": 240.0, "angle_deg": 178.0, "strength": 53.2}],
  "edge_count": 1,
  "reference": {"x": 363.0167, "y": 39.0167, "angle_deg": 180},
  "result": {"x": 364.0, "y": 240.0, "angle_deg": 178.0},
  "offset": {"x": 0.9833, "y": 200.9833, "angle_deg": -2.0},
  "rotate": false,
  "apply_transform": true,
  "arrow": {"p0": {"x": 363, "y": 32}, "p1": {"x": 364, "y": 452}}
}
```

## Boas Práticas

- Defina `reference` usando o botão Sync no frontend quando a borda estiver no ponto desejado.
- Use `rotate=false` para pipelines que não dependem de ângulo; `true` quando rotação deve realocar ROIs elípticos/rotacionados.
- Mantenha a seta (`arrow`) dentro do ROI para amostragem correta.
- Em pipelines com múltiplas `Locate`, ative `apply_transform=true` apenas nas que devem influenciar tools seguintes.

## Debug

Cada tool exporta `debug.roi_debug` com dados da transformação de ROI. Quando múltiplas `Locate` aplicam offset, o `InspectionProcessor` compõe (soma) os deslocamentos antes de extrair o ROI da tool atual.
