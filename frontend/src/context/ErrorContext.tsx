import React, { createContext, ReactNode, useContext, useState } from 'react';
import { Alert, Snackbar } from '@mui/material';

import { SNACKBAR_DURATION_ERROR, SNACKBAR_DURATION_SUCCESS } from '../constants';

interface ErrorContextType {
  showError: (message: string) => void;
  showSuccess: (message: string) => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

export const ErrorProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [openSuccess, setOpenSuccess] = useState(false);

  const showError = (message: string) => {
    setError(message);
    setOpen(true);
  };

  const showSuccess = (message: string) => {
    setSuccess(message);
    setOpenSuccess(true);
  };

  return (
    <ErrorContext.Provider value={{ showError, showSuccess }}>
      {children}
      <Snackbar
        open={open}
        autoHideDuration={SNACKBAR_DURATION_ERROR}
        onClose={() => setOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setOpen(false)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      <Snackbar
        open={openSuccess}
        autoHideDuration={SNACKBAR_DURATION_SUCCESS}
        onClose={() => setOpenSuccess(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setOpenSuccess(false)} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </ErrorContext.Provider>
  );
};

export const useError = () => {
  const context = useContext(ErrorContext);
  if (context === undefined) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};

