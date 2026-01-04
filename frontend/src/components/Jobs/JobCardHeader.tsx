import React from 'react';
import { Box, Chip, Stack, Typography, useTheme } from '@mui/material';

import { Job } from '../../types/job';
import { formatStatus, getStatusColor, getStatusIcon } from '../../utils/statusUtils';

interface JobCardHeaderProps {
  job: Job;
}

export const JobCardHeader: React.FC<JobCardHeaderProps> = React.memo(({ job }) => {
  const theme = useTheme();
  const StatusIcon = getStatusIcon(job.status);
  const statusColor = getStatusColor(job.status);

  return (
    <Box sx={{ flex: 1, minWidth: 0 }}>
      <Typography
        variant="h6"
        gutterBottom
        sx={{
          fontWeight: theme.typography.h6.fontWeight,
          mb: 1.5,
          wordBreak: 'break-word',
        }}
      >
        Job {String(job.id).slice(0, 8)}...
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1, alignItems: 'center' }}>
        <Chip
          icon={<StatusIcon sx={{ fontSize: theme.typography.body2.fontSize, mr: 0.5 }} />}
          label={formatStatus(job.status)}
          color={statusColor}
          size="small"
          sx={{
            fontWeight: theme.typography.button.fontWeight,
            '& .MuiChip-icon': {
              color: 'inherit',
            },
          }}
        />
        {job.lang && job.geo && (
          <Chip
            label={`${job.lang.toUpperCase()}/${job.geo.toUpperCase()}`}
            size="small"
            variant="outlined"
            sx={{ fontWeight: theme.typography.button.fontWeight }}
          />
        )}
      </Stack>
    </Box>
  );
});

JobCardHeader.displayName = 'JobCardHeader';

