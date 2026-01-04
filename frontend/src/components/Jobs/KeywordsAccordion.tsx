import React, { useState } from 'react';
import { Accordion, AccordionDetails, AccordionSummary, Box, Chip, Typography, useTheme } from '@mui/material';
import { ExpandMore } from '@mui/icons-material';

import { useKeywordStatus } from '../../hooks/useKeywordStatus';
import { Job } from '../../types/job';
import { KeywordSearchInput } from './KeywordSearchInput';
import { KeywordTable } from './KeywordTable';

interface KeywordsAccordionProps {
  job: Job;
}

export const KeywordsAccordion: React.FC<KeywordsAccordionProps> = ({ job }) => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [expanded, setExpanded] = useState(false);

  const keywords = job.keywords || [];
  const { filteredKeywords, getKeywordStatus, getStatusDisplay } = useKeywordStatus(job, searchQuery);

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
        expandIcon={<ExpandMore aria-label={expanded ? 'Collapse keywords' : 'Expand keywords'} />}
        aria-label={`Keywords list with ${keywords.length} keyword${keywords.length !== 1 ? 's' : ''}`}
        sx={{
          px: 2,
          py: 1.5,
          '&:hover': {
            bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
          },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
          <Typography variant="body1" sx={{ fontWeight: theme.typography.h6.fontWeight }}>
            Keywords
          </Typography>
          <Chip
            label={`${keywords.length} keyword${keywords.length !== 1 ? 's' : ''}`}
            size="small"
            variant="outlined"
            sx={{ height: 24, fontSize: theme.typography.caption.fontSize }}
          />
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ px: 2, pb: 2, pt: 0 }}>
        <KeywordSearchInput value={searchQuery} onChange={setSearchQuery} />
        <KeywordTable
          keywords={filteredKeywords}
          getKeywordStatus={getKeywordStatus}
          getStatusDisplay={getStatusDisplay}
          emptyMessage={searchQuery ? 'No keywords match your search' : 'No keywords found'}
        />
      </AccordionDetails>
    </Accordion>
  );
};

KeywordsAccordion.displayName = 'KeywordsAccordion';

