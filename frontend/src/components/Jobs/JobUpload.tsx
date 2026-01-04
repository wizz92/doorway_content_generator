import React from 'react';
import { Box, Button, Paper, Typography, useTheme } from '@mui/material';
import { Description } from '@mui/icons-material';

import { useJobUpload } from '../../hooks/useJobUpload';
import { FileUploadSection } from './FileUploadSection';
import { JobParametersForm } from './JobParametersForm';

interface JobUploadProps {
  onUploadSuccess: (jobId: string) => void;
}

export const JobUpload: React.FC<JobUploadProps> = ({ onUploadSuccess }) => {
  const theme = useTheme();
  const {
    file,
    lang,
    geo,
    numWebsites,
    uploading,
    setFile,
    setLang,
    setGeo,
    setNumWebsites,
    handleSubmit,
  } = useJobUpload();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleSubmit(onUploadSuccess);
  };

  return (
    <Paper
      sx={{
        p: { xs: 2, sm: 3, md: 4 },
        mb: 3,
        borderRadius: 3,
        border: `1px solid ${theme.palette.divider}`,
      }}
    >
      <Typography
        variant="h5"
        component="h2"
        gutterBottom
        sx={{
          fontWeight: theme.typography.h5.fontWeight,
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Description sx={{ color: theme.palette.primary.main }} aria-hidden="true" />
        Create New Job
      </Typography>
      <Box component="form" onSubmit={onSubmit} aria-label="Create new job form">
        <FileUploadSection file={file} onFileChange={handleFileChange} />

        <JobParametersForm
          lang={lang}
          geo={geo}
          numWebsites={numWebsites}
          onLangChange={setLang}
          onGeoChange={setGeo}
          onNumWebsitesChange={setNumWebsites}
        />

        <Button
          type="submit"
          variant="contained"
          fullWidth
          disabled={!file || uploading}
          aria-label={uploading ? 'Creating job, please wait' : 'Create new job'}
          sx={{
            py: 1.5,
            fontSize: theme.typography.body1.fontSize,
            fontWeight: theme.typography.h5.fontWeight,
            background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
            '&:hover': {
              background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
              transform: 'translateY(-2px)',
              boxShadow: `0 6px 20px ${theme.palette.primary.main}40`,
            },
            '&:disabled': {
              background: theme.palette.action.disabledBackground,
            },
            transition: 'all 0.3s ease-in-out',
          }}
        >
          {uploading ? 'Creating Job...' : 'Create Job'}
        </Button>
      </Box>
    </Paper>
  );
};

