import React, { useCallback, useState } from 'react';
import { Alert, Box, Button, Container, Fade, Paper, TextField, Typography, useTheme } from '@mui/material';
import { useNavigate } from 'react-router-dom';

import { ANIMATION_DURATION_FAST, ANIMATION_DURATION_NORMAL } from '../../constants';
import { useAuth } from '../../context/AuthContext';
import { logger } from '../../utils/logger';
import { textFieldStyles } from '../../utils/styleUtils';

export const LoginForm: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError('');
      setLoading(true);

      try {
        await login(username, password);
        navigate('/dashboard');
      } catch (err: unknown) {
        logger.error('Login form error:', err);
        const errorMessage =
          (err as Error).message ||
          (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          'Login failed. Please check your credentials.';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [username, password, login, navigate]
  );

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: { xs: 2, sm: 3 },
        }}
      >
        <Fade in timeout={ANIMATION_DURATION_NORMAL}>
          <Paper
            elevation={8}
            sx={{
              padding: { xs: 3, sm: 5 },
              width: '100%',
              maxWidth: 450,
              borderRadius: 3,
              background: theme.palette.mode === 'dark'
                ? `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`
                : theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
            }}
          >
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography
                component="h1"
                variant="h4"
                gutterBottom
                sx={{
                  fontWeight: theme.typography.h4.fontWeight,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1,
                }}
              >
                Content Generator
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ fontSize: theme.typography.body2.fontSize }}
              >
                Sign in to continue
              </Typography>
            </Box>

            {error && (
              <Fade in timeout={ANIMATION_DURATION_FAST}>
                <Alert
                  severity="error"
                  sx={{
                    mb: 3,
                    borderRadius: 2,
                    animation: 'shake 0.5s ease-in-out',
                    '@keyframes shake': {
                      '0%, 100%': { transform: 'translateX(0)' },
                      '25%': { transform: 'translateX(-10px)' },
                      '75%': { transform: 'translateX(10px)' },
                    },
                  }}
                >
                  {error}
                </Alert>
              </Fade>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                sx={{ mb: 2, ...textFieldStyles }}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                sx={{ mb: 3, ...textFieldStyles }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{
                  py: 1.5,
                  fontSize: theme.typography.body1.fontSize,
                  fontWeight: theme.typography.h5.fontWeight,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
                    transform: 'translateY(-2px)',
                    boxShadow: `0 6px 20px ${theme.palette.primary.main}40`,
                  },
                  '&:disabled': {
                    background: theme.palette.action.disabledBackground,
                  },
                  transition: 'all 0.3s ease-in-out',
                }}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </Box>
          </Paper>
        </Fade>
      </Box>
    </Container>
  );
};

