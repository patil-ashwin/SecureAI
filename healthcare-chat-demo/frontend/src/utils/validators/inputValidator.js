// src/utils/validators/inputValidator.js
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isValidSessionId = (sessionId) => {
  return typeof sessionId === 'string' && sessionId.length > 0;
};

export const validateRequired = (value) => {
  return value !== null && value !== undefined && value !== '';
};