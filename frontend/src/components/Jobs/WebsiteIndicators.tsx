import React from 'react';
import { Box, useTheme } from '@mui/material';
import { CheckCircle } from '@mui/icons-material';
import { KeywordStatus } from '../../types/job';

interface WebsiteIndicatorsProps {
  status: KeywordStatus | null;
}

export const WebsiteIndicators: React.FC<WebsiteIndicatorsProps> = React.memo(({ status }) => {
  const theme = useTheme();

  if (!status) {
    return null;
  }

  const { completed_websites, total_websites } = status;
  const indicators = [];

  for (let i = 1; i <= total_websites; i++) {
    const isCompleted = completed_websites.includes(i);
    indicators.push(
      <Box
        key={i}
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 24,
          height: 24,
          borderRadius: '50%',
          bgcolor: isCompleted
            ? theme.palette.success.main
            : theme.palette.mode === 'dark'
            ? 'rgba(255, 255, 255, 0.1)'
            : 'rgba(0, 0, 0, 0.1)',
          color: isCompleted ? theme.palette.success.contrastText : theme.palette.text.secondary,
          fontSize: theme.typography.caption.fontSize,
          fontWeight: theme.typography.h6.fontWeight,
          mr: 0.5,
        }}
        title={`Website ${i} - ${isCompleted ? 'Completed' : 'Pending'}`}
        role="img"
        aria-label={`Website ${i} ${isCompleted ? 'completed' : 'pending'}`}
      >
        {isCompleted ? <CheckCircle sx={{ fontSize: theme.typography.body2.fontSize }} /> : i}
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 0.5 }} role="list">
      {indicators}
    </Box>
  );
});

WebsiteIndicators.displayName = 'WebsiteIndicators';

