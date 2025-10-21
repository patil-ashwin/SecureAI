// src/hooks/useKeyboardShortcuts.js
import { useEffect, useCallback } from 'react';

export const useKeyboardShortcuts = (shortcuts) => {
  const handleKeyDown = useCallback((event) => {
    for (const [key, handler] of Object.entries(shortcuts)) {
      const keys = key.toLowerCase().split('+');
      let match = true;

      // Check modifiers
      if (keys.includes('cmd') || keys.includes('ctrl')) {
        if (!(event.metaKey || event.ctrlKey)) match = false;
      }
      if (keys.includes('shift') && !event.shiftKey) match = false;
      if (keys.includes('alt') && !event.altKey) match = false;

      // Check main key
      const mainKey = keys[keys.length - 1];
      if (event.key.toLowerCase() !== mainKey) match = false;

      if (match) {
        event.preventDefault();
        handler(event);
        break;
      }
    }
  }, [shortcuts]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
};