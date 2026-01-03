import React from 'react';
import { Alert, AlertTitle, useTheme } from '@mui/material';
import { Fade } from '@mui/material';

interface ErrorAlertProps {
  message: string;
  title?: string;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, title = 'Error' }) => {
  const theme = useTheme();
  return (
    <Fade in timeout={300}>
      <Alert
        severity="error"
        sx={{
          mb: 2,
          borderRadius: 2,
          animation: 'shake 0.5s ease-in-out',
          '@keyframes shake': {
            '0%, 100%': { transform: 'translateX(0)' },
            '25%': { transform: 'translateX(-10px)' },
            '75%': { transform: 'translateX(10px)' },
          },
        }}
      >
        <AlertTitle sx={{ fontWeight: 600 }}>{title}</AlertTitle>
        {message}
      </Alert>
    </Fade>
  );
};

