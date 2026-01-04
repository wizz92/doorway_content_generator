import React from 'react';
import { Box, Stack, Typography, useTheme } from '@mui/material';
import { AccessTime, Error as ErrorIcon } from '@mui/icons-material';

import { Job } from '../../types/job';
import { formatDate } from '../../utils/dateUtils';
import { getStatusIcon } from '../../utils/statusUtils';

interface JobCardMetadataProps {
  job: Job;
}

export const JobCardMetadata: React.FC<JobCardMetadataProps> = React.memo(({ job }) => {
  const theme = useTheme();
  const StatusIcon = getStatusIcon(job.status);

  return (
    <Stack spacing={1}>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
      >
        <AccessTime sx={{ fontSize: theme.typography.body2.fontSize }} />
        Created: {formatDate(job.created_at)}
      </Typography>
      {job.completed_at && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
        >
          <StatusIcon sx={{ fontSize: theme.typography.body2.fontSize }} />
          Completed: {formatDate(job.completed_at)}
        </Typography>
      )}
      {job.error_message && (
        <Box
          sx={{
            mt: 1,
            p: 1.5,
            borderRadius: 1,
            bgcolor: theme.palette.mode === 'dark' ? 'rgba(244, 67, 54, 0.15)' : 'rgba(244, 67, 54, 0.08)',
            border: `1px solid ${theme.palette.error.main}30`,
          }}
        >
          <Typography
            variant="body2"
            color="error"
            sx={{ display: 'flex', alignItems: 'start', gap: 0.5 }}
          >
            <ErrorIcon sx={{ fontSize: theme.typography.body2.fontSize, mt: 0.25, flexShrink: 0 }} />
            <span>{job.error_message}</span>
          </Typography>
        </Box>
      )}
    </Stack>
  );
});

JobCardMetadata.displayName = 'JobCardMetadata';

