import React from 'react';
import { Box, Container } from '@mui/material';
import { AppBar } from './AppBar';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar />
      <Container
        maxWidth="lg"
        sx={{
          mt: { xs: 2, sm: 3, md: 4 },
          mb: { xs: 2, sm: 3, md: 4 },
          px: { xs: 2, sm: 3 },
          flex: 1,
          width: '100%',
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

