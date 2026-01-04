import React from 'react';
import { Box, LinearProgress, Stack, Typography, useTheme } from '@mui/material';

import { Job } from '../../types/job';
import { getStatusDisplayText } from '../../utils/statusUtils';

interface JobCardProgressProps {
  job: Job;
}

export const JobCardProgress: React.FC<JobCardProgressProps> = React.memo(({ job }) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        mb: 2,
        p: 2,
        borderRadius: 2,
        bgcolor: theme.palette.mode === 'dark' ? 'rgba(33, 150, 243, 0.1)' : 'rgba(33, 150, 243, 0.05)',
        border: `2px solid ${theme.palette.primary.main}40`,
      }}
    >
      <Box sx={{ mb: 1.5 }}>
        <LinearProgress
          variant="determinate"
          value={Math.max(0, Math.min(100, job.progress || 0))}
          sx={{
            height: 12,
            borderRadius: 6,
            mb: 1.5,
            bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
            '& .MuiLinearProgress-bar': {
              borderRadius: 6,
            },
          }}
        />
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ fontSize: theme.typography.body2.fontSize, fontWeight: theme.typography.h6.fontWeight }}
        >
          {job.progress || 0}% Complete - {getStatusDisplayText(job.status)}
        </Typography>
      </Box>
      <Stack direction="row" spacing={2} flexWrap="wrap" sx={{ gap: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Keywords: <strong>{job.keywords_completed || 0}/{job.total_keywords || 0}</strong>
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Websites: <strong>{job.websites_completed || 0}/{job.num_websites || 0}</strong>
        </Typography>
      </Stack>
    </Box>
  );
});

JobCardProgress.displayName = 'JobCardProgress';

