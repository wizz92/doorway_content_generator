import React from 'react';
import { Box, TextField, InputAdornment, useTheme } from '@mui/material';
import { Search } from '@mui/icons-material';

interface KeywordSearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const KeywordSearchInput: React.FC<KeywordSearchInputProps> = React.memo(
  ({ value, onChange, placeholder = 'Search keywords...' }) => {
    const theme = useTheme();

    return (
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search sx={{ fontSize: theme.typography.h6.fontSize, color: theme.palette.text.secondary }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            },
          }}
          aria-label="Search keywords"
        />
      </Box>
    );
  }
);

KeywordSearchInput.displayName = 'KeywordSearchInput';

