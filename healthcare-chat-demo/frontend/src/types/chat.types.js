// src/types/chat.types.js
/**
 * Chat Message Types
 */

export const MessageShape = {
  id: 'string',
  text: 'string',
  type: 'string', // user | assistant | system | error
  timestamp: 'string',
  suggestions: 'array|null',
  queryData: 'object|null',
  needsParams: 'boolean',
  isFollowUp: 'boolean'
};

/**
 * Chat Session Shape
 */
export const SessionShape = {
  id: 'string',
  canFollowUp: 'boolean',
  suggestions: 'array',
  lastActivity: 'string'
};