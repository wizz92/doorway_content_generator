import React from 'react';
import { Box, Button, Stack, Typography, useTheme } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

interface FileUploadSectionProps {
  file: File | null;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const FileUploadSection: React.FC<FileUploadSectionProps> = React.memo(({ file, onFileChange }) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        mb: 3,
        p: 2,
        borderRadius: 2,
        border: `2px dashed ${file ? theme.palette.primary.main : theme.palette.divider}`,
        bgcolor: file
          ? theme.palette.mode === 'dark'
            ? 'rgba(102, 126, 234, 0.1)'
            : 'rgba(102, 126, 234, 0.05)'
          : 'transparent',
        transition: 'all 0.3s ease-in-out',
      }}
    >
      <input
        accept=".csv"
        style={{ display: 'none' }}
        id="csv-upload"
        type="file"
        onChange={onFileChange}
      />
      <label htmlFor="csv-upload" aria-label="Upload CSV file">
        <Button
          variant={file ? 'contained' : 'outlined'}
          component="span"
          startIcon={<CloudUpload aria-hidden="true" />}
          fullWidth
          aria-label={file ? `Selected file: ${file.name}` : 'Select CSV file to upload'}
          sx={{
            py: 2,
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: file ? `0 4px 12px ${theme.palette.primary.main}40` : undefined,
            },
          }}
        >
          {file ? file.name : 'Upload CSV File'}
        </Button>
      </label>
      {file && (
        <Stack
          direction="row"
          spacing={1}
          sx={{ mt: 1.5, alignItems: 'center', justifyContent: 'center' }}
        >
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: theme.typography.button.fontWeight }}>
            File size: {(file.size / 1024).toFixed(2)} KB
          </Typography>
        </Stack>
      )}
    </Box>
  );
});

FileUploadSection.displayName = 'FileUploadSection';

