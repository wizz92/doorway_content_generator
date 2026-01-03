import React from 'react';
import { LinearProgress, Box, Typography } from '@mui/material';

interface ProgressBarProps {
  progress: number;
  label?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, label }) => {
  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      {label && (
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {label}
        </Typography>
      )}
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{ height: 8, borderRadius: 4 }}
      />
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
        {progress}%
      </Typography>
    </Box>
  );
};

