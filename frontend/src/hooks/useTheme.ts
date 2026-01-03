import { useState, useEffect, useMemo } from 'react';
import { createTheme, Theme } from '@mui/material/styles';
import { getDesignTokens } from '../theme/theme';

type ThemeMode = 'light' | 'dark';

interface UseThemeReturn {
  mode: ThemeMode;
  theme: Theme;
  toggleColorMode: () => void;
}

/**
 * Hook for managing theme.
 */
export function useTheme(): UseThemeReturn {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const savedMode = localStorage.getItem('themeMode');
    return (savedMode as ThemeMode) || 'light';
  });

  useEffect(() => {
    localStorage.setItem('themeMode', mode);
  }, [mode]);

  const colorMode = useMemo(
    () => ({
      mode,
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
    }),
    [mode]
  );

  const theme = useMemo(() => createTheme(getDesignTokens(mode)), [mode]);

  return {
    ...colorMode,
    theme,
  };
}

