import React, { useState, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  InputAdornment,
  useTheme,
  Stack,
} from '@mui/material';
import { Search, CheckCircle, Pending, RadioButtonUnchecked } from '@mui/icons-material';
import { Job, KeywordStatus } from '../../types/job';

interface KeywordsDialogProps {
  open: boolean;
  onClose: () => void;
  job: Job;
}

export const KeywordsDialog: React.FC<KeywordsDialogProps> = ({ open, onClose, job }) => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');

  const keywords = job.keywords || [];
  const keywordStatus = job.keyword_status || {};

  // Filter keywords based on search query
  const filteredKeywords = useMemo(() => {
    if (!searchQuery.trim()) {
      return keywords;
    }
    const query = searchQuery.toLowerCase();
    return keywords.filter((keyword) => keyword.toLowerCase().includes(query));
  }, [keywords, searchQuery]);

  const getKeywordStatus = (keyword: string): KeywordStatus | null => {
    return keywordStatus[keyword] || null;
  };

  const getStatusDisplay = (status: KeywordStatus | null): { text: string; color: 'success' | 'warning' | 'default' } => {
    if (!status) {
      return { text: 'Pending', color: 'default' };
    }

    const { completed_websites, total_websites } = status;
    const completedCount = completed_websites.length;

    if (completedCount === 0) {
      return { text: 'Pending', color: 'default' };
    } else if (completedCount === total_websites) {
      return { text: `Completed (${completedCount}/${total_websites})`, color: 'success' };
    } else {
      return { text: `In Progress (${completedCount}/${total_websites})`, color: 'warning' };
    }
  };

  const renderWebsiteIndicators = (status: KeywordStatus | null) => {
    if (!status) {
      return null;
    }

    const { completed_websites, total_websites } = status;
    const indicators = [];

    for (let i = 1; i <= total_websites; i++) {
      const isCompleted = completed_websites.includes(i);
      indicators.push(
        <Box
          key={i}
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 24,
            height: 24,
            borderRadius: '50%',
            bgcolor: isCompleted
              ? theme.palette.success.main
              : theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.1)',
            color: isCompleted ? theme.palette.success.contrastText : theme.palette.text.secondary,
            fontSize: '0.75rem',
            fontWeight: 600,
            mr: 0.5,
          }}
          title={`Website ${i} - ${isCompleted ? 'Completed' : 'Pending'}`}
        >
          {isCompleted ? <CheckCircle sx={{ fontSize: 16 }} /> : i}
        </Box>
      );
    }

    return <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 0.5 }}>{indicators}</Box>;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '90vh',
        },
      }}
    >
      <DialogTitle>
        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
          Keywords - Job {String(job.id).slice(0, 8)}...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          {keywords.length} keyword{keywords.length !== 1 ? 's' : ''} total
        </Typography>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search sx={{ fontSize: 20, color: theme.palette.text.secondary }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
          />
        </Box>

        {filteredKeywords.length === 0 ? (
          <Box
            sx={{
              textAlign: 'center',
              py: 4,
              color: theme.palette.text.secondary,
            }}
          >
            <Typography variant="body2">
              {searchQuery ? 'No keywords match your search' : 'No keywords found'}
            </Typography>
          </Box>
        ) : (
          <TableContainer
            component={Paper}
            variant="outlined"
            sx={{
              maxHeight: '60vh',
              borderRadius: 2,
              border: `1px solid ${theme.palette.divider}`,
            }}
          >
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600, width: '40%' }}>Keyword</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: '30%' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 600, width: '30%' }}>Websites</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredKeywords.map((keyword, index) => {
                  const status = getKeywordStatus(keyword);
                  const statusDisplay = getStatusDisplay(status);

                  return (
                    <TableRow key={index} hover>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            wordBreak: 'break-word',
                            fontWeight: 500,
                          }}
                        >
                          {keyword}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={statusDisplay.text}
                          color={statusDisplay.color}
                          size="small"
                          sx={{
                            fontWeight: 500,
                          }}
                        />
                      </TableCell>
                      <TableCell>{renderWebsiteIndicators(status)}</TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} variant="contained" color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

