import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  LinearProgress,
  useTheme,
  Divider,
  Stack,
} from '@mui/material';
import { Download, Cancel, AccessTime, Error as ErrorIcon } from '@mui/icons-material';
import { Job } from '../../types/job';
import { jobsService } from '../../services/jobs';
import { useError } from '../../context/ErrorContext';
import { formatDate } from '../../utils/dateUtils';
import { getStatusColor, getStatusIcon, formatStatus, getStatusDisplayText } from '../../utils/statusUtils';
import { shouldShowProgress } from '../../utils/jobUtils';

interface JobCardProps {
  job: Job;
  onUpdate: () => void;
}

export const JobCard: React.FC<JobCardProps> = React.memo(({ job, onUpdate }) => {
  const { showError, showSuccess } = useError();
  const theme = useTheme();
  const StatusIcon = getStatusIcon(job.status);

  const handleDownload = async () => {
    try {
      const blob = await jobsService.downloadJob(job.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `content-${job.id}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showSuccess('Download started');
    } catch (error: unknown) {
      const errorMessage = (error as Error).message || 'Failed to download';
      showError(errorMessage);
    }
  };

  const handleCancel = async () => {
    try {
      await jobsService.cancelJob(job.id);
      showSuccess('Job cancelled');
      onUpdate();
    } catch (error: unknown) {
      const errorMessage = (error as Error).message || 'Failed to cancel job';
      showError(errorMessage);
    }
  };

  const showProgress = shouldShowProgress(job);

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
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="h6"
              gutterBottom
              sx={{
                fontWeight: 600,
                mb: 1.5,
                wordBreak: 'break-word',
              }}
            >
              Job {String(job.id).slice(0, 8)}...
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
              <Chip
                icon={<StatusIcon sx={{ fontSize: 16, mr: 0.5 }} />}
                label={formatStatus(job.status)}
                color={getStatusColor(job.status) as any}
                size="small"
                sx={{
                  fontWeight: 500,
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
                  sx={{ fontWeight: 500 }}
                />
              )}
            </Stack>
          </Box>
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
                onClick={handleDownload}
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
                onClick={handleCancel}
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
        </Box>

        {showProgress && (
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
                sx={{ fontSize: '0.875rem', fontWeight: 600 }}
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
        )}

        <Divider sx={{ my: 2 }} />

        <Stack spacing={1}>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <AccessTime sx={{ fontSize: 14 }} />
            Created: {formatDate(job.created_at)}
          </Typography>
          {job.completed_at && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <StatusIcon sx={{ fontSize: 14 }} />
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
                <ErrorIcon sx={{ fontSize: 16, mt: 0.25, flexShrink: 0 }} />
                <span>{job.error_message}</span>
              </Typography>
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
});
