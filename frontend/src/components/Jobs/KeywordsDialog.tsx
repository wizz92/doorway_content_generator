import React, { useState } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Typography, useTheme } from '@mui/material';

import { useKeywordStatus } from '../../hooks/useKeywordStatus';
import { Job } from '../../types/job';
import { KeywordSearchInput } from './KeywordSearchInput';
import { KeywordTable } from './KeywordTable';

interface KeywordsDialogProps {
  open: boolean;
  onClose: () => void;
  job: Job;
}

export const KeywordsDialog: React.FC<KeywordsDialogProps> = React.memo(({ open, onClose, job }) => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const keywords = job.keywords || [];
  const { filteredKeywords, getKeywordStatus, getStatusDisplay } = useKeywordStatus(job, searchQuery);

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
        <Typography variant="h6" component="div" sx={{ fontWeight: theme.typography.h6.fontWeight }}>
          Keywords - Job {String(job.id).slice(0, 8)}...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          {keywords.length} keyword{keywords.length !== 1 ? 's' : ''} total
        </Typography>
      </DialogTitle>
      <DialogContent>
        <KeywordSearchInput value={searchQuery} onChange={setSearchQuery} />
        <KeywordTable
          keywords={filteredKeywords}
          getKeywordStatus={getKeywordStatus}
          getStatusDisplay={getStatusDisplay}
          emptyMessage={searchQuery ? 'No keywords match your search' : 'No keywords found'}
          maxHeight="60vh"
        />
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} variant="contained" color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
});

KeywordsDialog.displayName = 'KeywordsDialog';

