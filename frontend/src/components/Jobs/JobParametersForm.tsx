import React from 'react';
import { Box, TextField } from '@mui/material';

import { MAX_NUM_WEBSITES, MIN_NUM_WEBSITES } from '../../constants';
import { textFieldStyles } from '../../utils/styleUtils';

interface JobParametersFormProps {
  lang: string;
  geo: string;
  numWebsites: number;
  onLangChange: (lang: string) => void;
  onGeoChange: (geo: string) => void;
  onNumWebsitesChange: (num: number) => void;
}

export const JobParametersForm: React.FC<JobParametersFormProps> = React.memo(
  ({ lang, geo, numWebsites, onLangChange, onGeoChange, onNumWebsitesChange }) => {
    return (
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
          gap: 2,
          mb: 3,
        }}
      >
        <TextField
          fullWidth
          label="Language Code"
          value={lang}
          onChange={(e) => onLangChange(e.target.value)}
          required
          sx={textFieldStyles}
        />
        <TextField
          fullWidth
          label="Geography Code"
          value={geo}
          onChange={(e) => onGeoChange(e.target.value)}
          required
          sx={textFieldStyles}
        />
        <TextField
          fullWidth
          label="Number of Websites"
          type="number"
          value={numWebsites}
          onChange={(e) => onNumWebsitesChange(parseInt(e.target.value) || MIN_NUM_WEBSITES)}
          inputProps={{ min: MIN_NUM_WEBSITES, max: MAX_NUM_WEBSITES }}
          required
          sx={textFieldStyles}
        />
      </Box>
    );
  }
);

JobParametersForm.displayName = 'JobParametersForm';
