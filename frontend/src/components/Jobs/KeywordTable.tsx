import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Chip,
  Box,
  useTheme,
} from '@mui/material';
import { KeywordStatus } from '../../types/job';
import { WebsiteIndicators } from './WebsiteIndicators';

interface KeywordTableProps {
  keywords: string[];
  getKeywordStatus: (keyword: string) => KeywordStatus | null;
  getStatusDisplay: (status: KeywordStatus | null) => { text: string; color: 'success' | 'warning' | 'default' };
  emptyMessage?: string;
  maxHeight?: string;
}

export const KeywordTable: React.FC<KeywordTableProps> = React.memo(
  ({ keywords, getKeywordStatus, getStatusDisplay, emptyMessage, maxHeight = '400px' }) => {
    const theme = useTheme();

    if (keywords.length === 0) {
      return (
        <Box
          sx={{
            textAlign: 'center',
            py: 4,
            color: theme.palette.text.secondary,
          }}
        >
          <Typography variant="body2">{emptyMessage || 'No keywords found'}</Typography>
        </Box>
      );
    }

    return (
      <TableContainer
        component={Paper}
        variant="outlined"
        sx={{
          maxHeight,
          borderRadius: 2,
          border: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: theme.typography.h6.fontWeight, width: '40%' }}>Keyword</TableCell>
              <TableCell sx={{ fontWeight: theme.typography.h6.fontWeight, width: '30%' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: theme.typography.h6.fontWeight, width: '30%' }}>Websites</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {keywords.map((keyword, index) => {
              const status = getKeywordStatus(keyword);
              const statusDisplay = getStatusDisplay(status);

              return (
                <TableRow key={index} hover>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{
                        wordBreak: 'break-word',
                        fontWeight: theme.typography.button.fontWeight,
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
                        fontWeight: theme.typography.button.fontWeight,
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <WebsiteIndicators status={status} />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }
);

KeywordTable.displayName = 'KeywordTable';

