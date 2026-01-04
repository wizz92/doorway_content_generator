import React from 'react';
import { Alert, AlertTitle, Fade } from '@mui/material';

import { ANIMATION_DURATION_FAST } from '../../constants';

interface ErrorAlertProps {
  message: string;
  title?: string;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, title = 'Error' }) => {
  return (
    <Fade in timeout={ANIMATION_DURATION_FAST}>
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
        <AlertTitle>{title}</AlertTitle>
        {message}
      </Alert>
    </Fade>
  );
};

