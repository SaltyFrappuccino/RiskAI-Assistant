import React from 'react';
import { AppBar, Toolbar, Typography, Box, useTheme, useMediaQuery, Container } from '@mui/material';
import { keyframes } from '@emotion/react';

const pulseGlow = keyframes`
  0% {
    text-shadow: 0 0 5px rgba(252, 4, 116, 0.3);
  }
  50% {
    text-shadow: 0 0 15px rgba(252, 4, 116, 0.7), 0 0 25px rgba(109, 22, 165, 0.5);
  }
  100% {
    text-shadow: 0 0 5px rgba(252, 4, 116, 0.3);
  }
`;

const Header = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        mb: 4, 
        background: `linear-gradient(90deg, ${theme.palette.background.darker} 0%, ${theme.palette.primary.dark} 100%)`,
        borderBottom: `1px solid rgba(109, 22, 165, 0.2)`,
        backdropFilter: 'blur(8px)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: '-50%',
          right: '-10%',
          width: '300px',
          height: '300px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(252, 4, 116, 0.05) 0%, rgba(109, 22, 165, 0.05) 50%, transparent 70%)',
          zIndex: 0,
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          bottom: '-50%',
          left: '10%',
          width: '250px',
          height: '250px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(109, 22, 165, 0.05) 0%, rgba(252, 4, 116, 0.05) 50%, transparent 70%)',
          zIndex: 0,
        }
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{ px: { xs: 0 } }}>
          <Box 
            display="flex" 
            alignItems="center"
            justifyContent={isMobile ? "center" : "space-between"}
            width="100%"
            flexDirection={isMobile ? "column" : "row"}
            py={isMobile ? 2 : 1}
            sx={{ position: 'relative', zIndex: 1 }}
          >
            <Typography 
              variant={isMobile ? "h5" : "h4"} 
              component="div" 
              sx={{ 
                fontWeight: 'bold',
                background: theme.palette.gradient.primary,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                animation: `${pulseGlow} 3s ease-in-out infinite`,
                letterSpacing: '0.5px',
                textTransform: 'uppercase',
                display: 'inline-block'
              }}
            >
              RiskAI Assistant
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: theme.palette.text.secondary,
                mt: isMobile ? 1 : 0,
                fontStyle: 'italic',
                opacity: 0.9,
                transition: 'all 0.3s ease',
                '&:hover': {
                  opacity: 1,
                  color: theme.palette.primary.light
                }
              }}
            >
              Анализ кода с использованием ИИ
            </Typography>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header; 