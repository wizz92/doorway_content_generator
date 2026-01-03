import React, { createContext, useContext } from 'react';
import { ThemeProvider as MuiThemeProvider, Theme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useTheme } from '../../hooks/useTheme';

interface ThemeContextType {
  mode: 'light' | 'dark';
  toggleColorMode: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  mode: 'light',
  toggleColorMode: () => {},
});

export const useThemeContext = () => useContext(ThemeContext);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const { mode, theme, toggleColorMode } = useTheme();

  return (
    <ThemeContext.Provider value={{ mode, toggleColorMode }}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

