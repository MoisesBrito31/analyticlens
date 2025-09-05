// utilitários de parâmetros de tools
import { computed } from 'vue'

export function useToolParams(selectedItemRef, selectedDefRef) {
  function getParam(key, defVal) {
    const it = selectedItemRef?.value || {}
    const def = selectedDefRef?.value || {}
    const src = { ...def, ...it }
    const v = src[key]
    return v === undefined || v === null ? defVal : v
  }

  const selectedToolType = computed(() => String(selectedItemRef?.value?.type || selectedItemRef?.value?.tool_type || '').toLowerCase())

  function toInt(v, def = 0) { const n = parseInt(v); return Number.isFinite(n) ? n : def }
  function toFloat(v, def = 0) { const n = parseFloat(v); return Number.isFinite(n) ? n : def }

  return { getParam, selectedToolType, toInt, toFloat }
}
