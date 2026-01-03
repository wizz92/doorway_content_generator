import React, { useState, useMemo } from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  InputAdornment,
  useTheme,
} from '@mui/material';
import { ExpandMore, Search, CheckCircle } from '@mui/icons-material';
import { Job, KeywordStatus } from '../../types/job';

interface KeywordsAccordionProps {
  job: Job;
}

export const KeywordsAccordion: React.FC<KeywordsAccordionProps> = ({ job }) => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [expanded, setExpanded] = useState(false);

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

  if (!keywords || keywords.length === 0) {
    return null;
  }

  return (
    <Accordion
      expanded={expanded}
      onChange={(_, isExpanded) => setExpanded(isExpanded)}
      sx={{
        mt: 2,
        '&:before': {
          display: 'none',
        },
        boxShadow: 'none',
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 2,
        '&.Mui-expanded': {
          margin: '16px 0',
        },
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandMore />}
        sx={{
          px: 2,
          py: 1.5,
          '&:hover': {
            bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
          },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
          <Typography variant="body1" sx={{ fontWeight: 600 }}>
            Keywords
          </Typography>
          <Chip
            label={`${keywords.length} keyword${keywords.length !== 1 ? 's' : ''}`}
            size="small"
            variant="outlined"
            sx={{ height: 24, fontSize: '0.75rem' }}
          />
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ px: 2, pb: 2, pt: 0 }}>
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
              maxHeight: '400px',
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
      </AccordionDetails>
    </Accordion>
  );
};

