// src/hooks/useScrollToBottom.js
import { useEffect, useRef } from 'react';

export const useScrollToBottom = (dependency) => {
  const ref = useRef();

  useEffect(() => {
    if (ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [dependency]);

  return ref;
};