import React, { useCallback } from 'react';
import {
  AppBar as MuiAppBar,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { AccountCircle, Brightness4, Brightness7 } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../context/AuthContext';
import { useThemeContext } from '../Theme/ThemeProvider';

export const AppBar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { mode, toggleColorMode } = useThemeContext();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  }, []);

  const handleClose = useCallback(() => {
    setAnchorEl(null);
  }, []);

  const handleLogout = useCallback(async () => {
    await logout();
    navigate('/login');
    handleClose();
  }, [logout, navigate, handleClose]);

  return (
    <MuiAppBar 
      position="static" 
      elevation={2}
      sx={{
        background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
      }}
    >
      <Toolbar sx={{ px: { xs: 2, sm: 3 } }}>
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1,
            fontWeight: theme.typography.h6.fontWeight,
            letterSpacing: 0.5,
          }}
        >
          Content Generator
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 } }}>
          <IconButton
            onClick={toggleColorMode}
            color="inherit"
            aria-label="toggle theme"
            sx={{
              transition: 'transform 0.2s ease-in-out',
              '&:hover': {
                transform: 'scale(1.1)',
              },
            }}
          >
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
          {!isMobile && (
            <Typography 
              variant="body2" 
              sx={{ 
                display: { xs: 'none', sm: 'block' },
                opacity: 0.9,
              }}
            >
              {user?.username}
            </Typography>
          )}
          <Button
            color="inherit"
            onClick={handleMenu}
            startIcon={<AccountCircle />}
            sx={{
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            {isMobile ? '' : 'Account'}
          </Button>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            {isMobile && (
              <MenuItem disabled>
                <Typography variant="body2" color="text.secondary">
                  {user?.username}
                </Typography>
              </MenuItem>
            )}
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </MuiAppBar>
  );
};

