import React from 'react';
import { Typography, Box, Paper, useTheme } from '@mui/material';
import { Inbox } from '@mui/icons-material';
import { JobCard } from './JobCard';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import { useJobs } from '../../hooks/useJobs';
import { useJobPolling } from '../../hooks/useJobPolling';

interface JobListProps {
  refreshTrigger?: number;
}

export const JobList: React.FC<JobListProps> = ({ refreshTrigger }) => {
  const { jobs, loading, fetchJobs } = useJobs(50);
  const theme = useTheme();

  // Poll for job updates
  useJobPolling(fetchJobs, {
    enabled: true,
    interval: 2000,
  });

  // Refresh when trigger changes
  React.useEffect(() => {
    if (refreshTrigger !== undefined && refreshTrigger > 0) {
      fetchJobs();
    }
  }, [refreshTrigger, fetchJobs]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Box>
      <Typography
        variant="h5"
        gutterBottom
        sx={{
          fontWeight: 600,
          mb: 3,
          fontSize: { xs: '1.5rem', sm: '1.75rem' },
        }}
      >
        Your Jobs
      </Typography>
      {jobs.length === 0 ? (
        <Paper
          sx={{
            p: { xs: 3, sm: 4, md: 6 },
            textAlign: 'center',
            borderRadius: 3,
            border: `1px dashed ${theme.palette.divider}`,
            bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.02)' : 'rgba(0, 0, 0, 0.02)',
          }}
        >
          <Inbox
            sx={{
              fontSize: { xs: 48, sm: 64 },
              color: theme.palette.text.secondary,
              mb: 2,
              opacity: 0.5,
            }}
          />
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ mb: 1, fontWeight: 500 }}
          >
            No jobs yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Create your first job above to get started
          </Typography>
        </Paper>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onUpdate={fetchJobs} />
          ))}
        </Box>
      )}
    </Box>
  );
};
