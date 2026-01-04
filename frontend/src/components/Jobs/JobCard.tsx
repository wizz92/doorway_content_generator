import React from 'react';
import { Box, Card, CardContent, Divider, useTheme } from '@mui/material';

import { useJobActions } from '../../hooks/useJobActions';
import { Job } from '../../types/job';
import { shouldShowProgress } from '../../utils/jobUtils';
import { JobCardActions } from './JobCardActions';
import { JobCardHeader } from './JobCardHeader';
import { JobCardMetadata } from './JobCardMetadata';
import { JobCardProgress } from './JobCardProgress';
import { KeywordsAccordion } from './KeywordsAccordion';

interface JobCardProps {
  job: Job;
  onUpdate: () => void;
}

export const JobCard: React.FC<JobCardProps> = React.memo(
  ({ job, onUpdate }) => {
    const theme = useTheme();
    const { handleDownload, handleCancel } = useJobActions();
    const showProgress = shouldShowProgress(job);

    const onDownload = () => handleDownload(job.id);
    const onCancel = () => handleCancel(job.id, onUpdate);

    return (
      <Card
        sx={{
          mb: 2,
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: `0 8px 24px ${theme.palette.mode === 'dark' ? 'rgba(0, 0, 0, 0.4)' : 'rgba(0, 0, 0, 0.15)'}`,
          },
          border: `1px solid ${theme.palette.divider}`,
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'start',
              mb: 2,
              flexWrap: { xs: 'wrap', sm: 'nowrap' },
              gap: 2,
            }}
          >
            <JobCardHeader job={job} />
            <JobCardActions job={job} onDownload={onDownload} onCancel={onCancel} />
          </Box>

          {showProgress && <JobCardProgress job={job} />}

          <Divider sx={{ my: 2 }} />

          <JobCardMetadata job={job} />
        </CardContent>
        {job.keywords && job.keywords.length > 0 && <KeywordsAccordion job={job} />}
      </Card>
    );
  },
  (prevProps, nextProps) => {
    // Custom comparison: re-render if job properties change
    // This ensures keyword_status updates trigger re-renders
    if (prevProps.job.id !== nextProps.job.id) {
      return false; // Different job, re-render
    }

    // Check if key job properties changed
    if (
      prevProps.job.status !== nextProps.job.status ||
      prevProps.job.progress !== nextProps.job.progress ||
      prevProps.job.keywords_completed !== nextProps.job.keywords_completed ||
      prevProps.job.websites_completed !== nextProps.job.websites_completed ||
      prevProps.job.error_message !== nextProps.job.error_message
    ) {
      return false; // Job properties changed, re-render
    }

    // Check if keyword_status changed (deep comparison)
    const prevStatus = prevProps.job.keyword_status || {};
    const nextStatus = nextProps.job.keyword_status || {};
    if (JSON.stringify(prevStatus) !== JSON.stringify(nextStatus)) {
      return false; // keyword_status changed, re-render
    }

    // Check if onUpdate function reference changed
    if (prevProps.onUpdate !== nextProps.onUpdate) {
      return false; // onUpdate changed, re-render
    }

    // No changes detected, skip re-render
    return true;
  }
);

JobCard.displayName = 'JobCard';
