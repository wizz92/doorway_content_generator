import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Button,
  TextField,
  Grid,
  Box,
  Alert,
  useTheme,
  Stack,
} from '@mui/material';
import { CloudUpload, Description } from '@mui/icons-material';
import { jobsService } from '../../services/jobs';
import { useError } from '../../context/ErrorContext';

interface JobUploadProps {
  onUploadSuccess: (jobId: string) => void;
}

export const JobUpload: React.FC<JobUploadProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [lang, setLang] = useState('hu');
  const [geo, setGeo] = useState('HU');
  const [numWebsites, setNumWebsites] = useState(3);
  const [uploading, setUploading] = useState(false);
  const { showError, showSuccess } = useError();
  const theme = useTheme();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      showError('Please select a CSV file');
      return;
    }

    setUploading(true);
    try {
      const uploadResponse = await jobsService.uploadFile(file);
      await jobsService.generateContent({
        job_id: uploadResponse.job_id,
        lang,
        geo,
        num_websites: numWebsites,
      });
      showSuccess('Job created successfully!');
      onUploadSuccess(uploadResponse.job_id);
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to upload and generate job');
    } finally {
      setUploading(false);
    }
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
        gutterBottom
        sx={{
          fontWeight: 600,
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Description sx={{ color: theme.palette.primary.main }} />
        Create New Job
      </Typography>
      <Box component="form" onSubmit={handleSubmit}>
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
            onChange={handleFileChange}
          />
          <label htmlFor="csv-upload">
            <Button
              variant={file ? 'contained' : 'outlined'}
              component="span"
              startIcon={<CloudUpload />}
              fullWidth
              sx={{
                py: 2,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: file
                    ? `0 4px 12px ${theme.palette.primary.main}40`
                    : undefined,
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
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                File size: {(file.size / 1024).toFixed(2)} KB
              </Typography>
            </Stack>
          )}
        </Box>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Language Code"
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-1px)',
                  },
                  '&.Mui-focused': {
                    transform: 'translateY(-1px)',
                  },
                },
              }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Geography Code"
              value={geo}
              onChange={(e) => setGeo(e.target.value)}
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-1px)',
                  },
                  '&.Mui-focused': {
                    transform: 'translateY(-1px)',
                  },
                },
              }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Number of Websites"
              type="number"
              value={numWebsites}
              onChange={(e) => setNumWebsites(parseInt(e.target.value) || 1)}
              inputProps={{ min: 1, max: 100 }}
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-1px)',
                  },
                  '&.Mui-focused': {
                    transform: 'translateY(-1px)',
                  },
                },
              }}
            />
          </Grid>
        </Grid>

        <Button
          type="submit"
          variant="contained"
          fullWidth
          disabled={!file || uploading}
          sx={{
            py: 1.5,
            fontSize: '1rem',
            fontWeight: 600,
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

