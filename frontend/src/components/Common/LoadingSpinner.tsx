import React from 'react';
import { Box, CircularProgress, Typography, useTheme } from '@mui/material';

export const LoadingSpinner: React.FC = () => {
  const theme = useTheme();
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '200px',
        gap: 2,
      }}
    >
      <CircularProgress
        sx={{
          color: theme.palette.primary.main,
          animation: 'spin 1s linear infinite',
        }}
      />
      <Typography variant="body2" color="text.secondary">
        Loading...
      </Typography>
    </Box>
  );
};

