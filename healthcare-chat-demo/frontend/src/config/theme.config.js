// src/config/theme.config.js
export const THEME_CONFIG = {
  themes: {
    dark: {
      name: 'dark',
      colors: {
        primary: '#171717',
        secondary: '#212121',
        tertiary: '#2f2f2f',
        text: {
          primary: '#ececec',
          secondary: '#8e8ea0',
          tertiary: '#6e7681'
        },
        border: '#4d4d4f',
        accent: '#10a37f',
        error: '#ff6b6b',
        warning: '#ffa726',
        success: '#4caf50'
      }
    },
    light: {
      name: 'light',
      colors: {
        primary: '#ffffff',
        secondary: '#f8f9fa',
        tertiary: '#e9ecef',
        text: {
          primary: '#212529',
          secondary: '#6c757d',
          tertiary: '#adb5bd'
        },
        border: '#dee2e6',
        accent: '#10a37f',
        error: '#dc3545',
        warning: '#fd7e14',
        success: '#198754'
      }
    }
  },
  defaultTheme: 'dark',
  enableSystemTheme: true,
  transitions: {
    duration: '0.3s',
    easing: 'ease-in-out'
  }
};
