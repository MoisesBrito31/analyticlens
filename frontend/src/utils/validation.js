/**
 * Sistema de validação JavaScript puro para substituir o Zod
 * Validações simples e eficientes para formulários
 */

// Tipos de validação disponíveis
export const VALIDATION_TYPES = {
  REQUIRED: 'required',
  EMAIL: 'email',
  MIN_LENGTH: 'minLength',
  MAX_LENGTH: 'maxLength',
  MIN_VALUE: 'minValue',
  MAX_VALUE: 'maxValue',
  PATTERN: 'pattern',
  CUSTOM: 'custom'
}

// Funções de validação individuais
export const validators = {
  // Campo obrigatório
  required: (value) => {
    if (value === null || value === undefined) return 'Campo obrigatório'
    if (typeof value === 'string' && value.trim() === '') return 'Campo obrigatório'
    if (Array.isArray(value) && value.length === 0) return 'Campo obrigatório'
    return null
  },

  // Validação de email
  email: (value) => {
    if (!value) return null // Se não for obrigatório
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(value) ? null : 'Email inválido'
  },

  // Comprimento mínimo
  minLength: (value, min) => {
    if (!value) return null
    if (typeof value === 'string' && value.length < min) {
      return `Mínimo de ${min} caracteres`
    }
    if (Array.isArray(value) && value.length < min) {
      return `Mínimo de ${min} itens`
    }
    return null
  },

  // Comprimento máximo
  maxLength: (value, max) => {
    if (!value) return null
    if (typeof value === 'string' && value.length > max) {
      return `Máximo de ${max} caracteres`
    }
    if (Array.isArray(value) && value.length > max) {
      return `Máximo de ${max} itens`
    }
    return null
  },

  // Valor mínimo (para números)
  minValue: (value, min) => {
    if (!value) return null
    const numValue = Number(value)
    if (isNaN(numValue) || numValue < min) {
      return `Valor mínimo: ${min}`
    }
    return null
  },

  // Valor máximo (para números)
  maxValue: (value, max) => {
    if (!value) return null
    const numValue = Number(value)
    if (isNaN(numValue) || numValue > max) {
      return `Valor máximo: ${max}`
    }
    return null
  },

  // Padrão regex
  pattern: (value, regex) => {
    if (!value) return null
    const pattern = new RegExp(regex)
    return pattern.test(value) ? null : 'Formato inválido'
  },

  // Validação customizada
  custom: (value, validatorFn) => {
    if (!value) return null
    return validatorFn(value)
  }
}

/**
 * Valida um campo com múltiplas regras
 * @param {*} value - Valor a ser validado
 * @param {Array} rules - Array de regras de validação
 * @returns {string|null} - Mensagem de erro ou null se válido
 */
export function validateField(value, rules = []) {
  for (const rule of rules) {
    const { type, params, message } = rule
    
    if (type === VALIDATION_TYPES.REQUIRED) {
      const error = validators.required(value)
      if (error) return message || error
    }
    
    if (type === VALIDATION_TYPES.EMAIL) {
      const error = validators.email(value)
      if (error) return message || error
    }
    
    if (type === VALIDATION_TYPES.MIN_LENGTH) {
      const error = validators.minLength(value, params)
      if (error) return message || error
    }
    
    if (type === VALIDATION_TYPES.MAX_LENGTH) {
      const error = validators.maxLength(value, params)
      if (error) return message || error
    }
    
    if (type === VALIDATION_TYPES.MIN_VALUE) {
      const error = validators.minValue(value, params)
      if (error) return message || error
    }
    
    if (type === VALIDATION_TYPES.MAX_VALUE) {
      const error = validators.maxValue(value, params)
      if (error) return message || error
    }
    
    if (type === VALIDATION_TYPES.PATTERN) {
      const error = validators.pattern(value, params)
      if (error) return message || error
    }
    
    if (type === VALIDATION_TYPES.CUSTOM) {
      const error = validators.custom(value, params)
      if (error) return message || error
    }
  }
  
  return null
}

/**
 * Valida um objeto completo com esquema de validação
 * @param {Object} data - Dados a serem validados
 * @param {Object} schema - Esquema de validação
 * @returns {Object} - Resultado da validação
 */
export function validateObject(data, schema) {
  const errors = {}
  let isValid = true
  
  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field]
    const error = validateField(value, rules)
    
    if (error) {
      errors[field] = error
      isValid = false
    }
  }
  
  return {
    isValid,
    errors,
    hasErrors: !isValid
  }
}

/**
 * Cria regras de validação de forma fluente
 * @returns {Object} - Builder de validação
 */
export function createValidationRules() {
  const rules = []
  
  return {
    required(message) {
      rules.push({ type: VALIDATION_TYPES.REQUIRED, message })
      return this
    },
    
    email(message) {
      rules.push({ type: VALIDATION_TYPES.EMAIL, message })
      return this
    },
    
    minLength(min, message) {
      rules.push({ type: VALIDATION_TYPES.MIN_LENGTH, params: min, message })
      return this
    },
    
    maxLength(max, message) {
      rules.push({ type: VALIDATION_TYPES.MAX_LENGTH, params: max, message })
      return this
    },
    
    minValue(min, message) {
      rules.push({ type: VALIDATION_TYPES.MIN_VALUE, params: min, message })
      return this
    },
    
    maxValue(max, message) {
      rules.push({ type: VALIDATION_TYPES.MAX_VALUE, params: max, message })
      return this
    },
    
    pattern(regex, message) {
      rules.push({ type: VALIDATION_TYPES.PATTERN, params: regex, message })
      return this
    },
    
    custom(validatorFn, message) {
      rules.push({ type: VALIDATION_TYPES.CUSTOM, params: validatorFn, message })
      return this
    },
    
    build() {
      return rules
    }
  }
}

// Exemplo de uso:
/*
const userSchema = {
  name: createValidationRules()
    .required('Nome é obrigatório')
    .minLength(2, 'Nome deve ter pelo menos 2 caracteres')
    .maxLength(50, 'Nome deve ter no máximo 50 caracteres')
    .build(),
    
  email: createValidationRules()
    .required('Email é obrigatório')
    .email('Email inválido')
    .build(),
    
  age: createValidationRules()
    .minValue(18, 'Idade mínima: 18 anos')
    .maxValue(120, 'Idade máxima: 120 anos')
    .build()
}

const result = validateObject(userData, userSchema)
if (!result.isValid) {
  console.log('Erros:', result.errors)
}
*/
