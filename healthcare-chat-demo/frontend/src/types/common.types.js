// src/types/common.types.js
/**
 * Common Component Props
 */

export const ButtonPropsShape = {
  variant: 'primary|secondary|ghost|danger',
  size: 'small|medium|large',
  disabled: 'boolean',
  loading: 'boolean',
  onClick: 'function',
  children: 'node'
};

export const InputPropsShape = {
  type: 'string',
  value: 'string',
  onChange: 'function',
  placeholder: 'string',
  disabled: 'boolean',
  error: 'string|null'
};