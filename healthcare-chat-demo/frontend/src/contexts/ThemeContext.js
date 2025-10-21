// src/contexts/ThemeContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { THEME_CONFIG } from '@config';

const ThemeContext = createContext();

export { ThemeContext };

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('dark');
  const [customTheme, setCustomTheme] = useState(THEME_CONFIG);

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('bart-theme');
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  useEffect(() => {
    // Save theme to localStorage
    localStorage.setItem('bart-theme', theme);
    
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const updateTheme = (newTheme) => {
    setCustomTheme(prev => ({ ...prev, ...newTheme }));
  };

  const value = {
    theme,
    customTheme,
    setTheme,
    toggleTheme,
    updateTheme,
    colors: customTheme.colors,
    fonts: customTheme.fonts,
    spacing: customTheme.spacing
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};