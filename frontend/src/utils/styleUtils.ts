import { SxProps, Theme } from '@mui/material/styles';

/**
 * Shared TextField styling for consistent form inputs.
 * Provides hover and focus animations.
 */
export const textFieldStyles: SxProps<Theme> = {
  '& .MuiOutlinedInput-root': {
    transition: 'all 0.2s ease-in-out',
    '&:hover': {
      transform: 'translateY(-1px)',
    },
    '&.Mui-focused': {
      transform: 'translateY(-1px)',
    },
  },
};

