import React from 'react';
import { Box, Button, useTheme } from '@mui/material';
import { Cancel, Download } from '@mui/icons-material';

import { Job } from '../../types/job';

interface JobCardActionsProps {
  job: Job;
  onDownload: () => void;
  onCancel: () => void;
}

export const JobCardActions: React.FC<JobCardActionsProps> = React.memo(({ job, onDownload, onCancel }) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1,
        flexShrink: 0,
        flexDirection: { xs: 'row', sm: 'column' },
      }}
    >
      {job.status === 'completed' && (
        <Button
          startIcon={<Download />}
          onClick={onDownload}
          variant="contained"
          size="small"
          aria-label={`Download results for job ${String(job.id).slice(0, 8)}`}
          sx={{
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: `0 4px 12px ${theme.palette.primary.main}40`,
            },
          }}
        >
          Download
        </Button>
      )}
      {(job.status === 'queued' || job.status === 'processing') && (
        <Button
          startIcon={<Cancel />}
          onClick={onCancel}
          variant="outlined"
          size="small"
          color="error"
          aria-label={`Cancel job ${String(job.id).slice(0, 8)}`}
          sx={{
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              borderWidth: 2,
            },
          }}
        >
          Cancel
        </Button>
      )}
    </Box>
  );
});

JobCardActions.displayName = 'JobCardActions';

