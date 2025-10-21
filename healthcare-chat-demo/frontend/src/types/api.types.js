// src/types/api.types.js
/**
 * API Response Types
 */

export const API_RESPONSE_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  LOADING: 'loading'
};

/**
 * Query Response Shape
 */
export const QueryResponseShape = {
  session_id: 'string',
  intent: 'string',
  parameters: 'object',
  query_name: 'string',
  raw_result: 'object',
  explanation: 'string',
  can_follow_up: 'boolean',
  suggested_questions: 'array',
  error: 'string|null',
  missing_parameters: 'array|null',
  export_data: 'object|null',
  processing_time: 'number|null'
};

/**
 * Configuration Shape
 */
export const ConfigurationShape = {
  intent: 'string',
  query_name: 'string',
  description: 'string',
  category: 'string',
  input_params: 'array',
  optional_params: 'array',
  explanation_type: 'string',
  keywords: 'array',
  enabled: 'boolean'
};