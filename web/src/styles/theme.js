import { createTheme } from '@mui/material/styles';

const pink = '#FC0474';
const pinkLight = '#FF4599';
const pinkDark = '#D1035F';
const purple = '#6D16A5';
const purpleLight = '#9932CC';
const purpleDark = '#4B0082';
const darkBackground = '#0F0F13';
const darkerBackground = '#080810';
const panelBackground = '#16161E';


const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: pink,
      light: pinkLight,
      dark: pinkDark,
      contrastText: '#fff',
    },
    secondary: {
      main: purple,
      light: purpleLight,
      dark: purpleDark,
      contrastText: '#fff',
    },
    background: {
      default: darkBackground,
      paper: panelBackground,
      darker: darkerBackground,
    },
    text: {
      primary: '#ffffff',
      secondary: '#B0B0B0',
    },
    error: {
      main: '#FF4A4A',
      light: '#FF7373',
    },
    warning: {
      main: '#FFA726',
      light: '#FFB851',
    },
    info: {
      main: '#29B6F6',
      light: '#5BC8F8',
    },
    success: {
      main: '#66BB6A',
      light: '#7CC97F',
    },
    gradient: {
      primary: `linear-gradient(45deg, ${pink} 0%, ${purple} 100%)`,
      secondary: `linear-gradient(45deg, ${purple} 0%, ${pink} 100%)`,
      dark: `linear-gradient(45deg, ${darkBackground} 0%, ${panelBackground} 100%)`,
    },
  },
  typography: {
    fontFamily: '"Roboto", "Inter", "Segoe UI", Arial, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      marginBottom: '1rem',
      backgroundImage: `linear-gradient(45deg, ${pink} 0%, ${purple} 100%)`,
      backgroundClip: 'text',
      textFillColor: 'transparent',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      marginBottom: '0.8rem',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
      marginBottom: '0.6rem',
    },
    h4: {
      fontSize: '1.2rem',
      fontWeight: 500,
      marginBottom: '0.4rem',
    },
    button: {
      textTransform: 'none',
    }
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(0, 0, 0, 0.1)',
    '0 5px 10px rgba(0, 0, 0, 0.15)',
    '0 8px 15px rgba(0, 0, 0, 0.2)',
    '0 12px 22px rgba(0, 0, 0, 0.25)',
    '0 14px 24px rgba(0, 0, 0, 0.3)',
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          scrollbarColor: `${purpleDark} ${darkBackground}`,
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: darkBackground,
          },
          '&::-webkit-scrollbar-thumb': {
            background: purpleDark,
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: purple,
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          padding: '10px 20px',
          borderRadius: '10px',
          transition: 'all 0.2s ease',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            transform: 'translateX(-100%)',
            transition: 'transform 0.3s ease',
          },
          '&:hover::before': {
            transform: 'translateX(0)',
          },
        },
        contained: {
          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)',
          '&:hover': {
            boxShadow: '0 6px 12px rgba(0, 0, 0, 0.3)',
            transform: 'translateY(-2px)',
          },
        },
        containedPrimary: {
          backgroundImage: `linear-gradient(45deg, ${pink} 0%, ${purpleLight} 100%)`,
          '&:hover': {
            backgroundImage: `linear-gradient(45deg, ${pinkLight} 0%, ${purple} 100%)`,
          },
        },
        containedSecondary: {
          backgroundImage: `linear-gradient(45deg, ${purple} 0%, ${pinkLight} 100%)`,
          '&:hover': {
            backgroundImage: `linear-gradient(45deg, ${purpleLight} 0%, ${pink} 100%)`,
          },
        },
        outlined: {
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
          },
        },
        outlinedPrimary: {
          borderImageSlice: 1,
          borderImageSource: `linear-gradient(45deg, ${pink}, ${purple})`,
          '&:hover': {
            borderImageSource: `linear-gradient(45deg, ${pinkLight}, ${purpleLight})`,
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          marginBottom: '1rem',
          '& .MuiOutlinedInput-root': {
            borderRadius: '10px',
            transition: 'all 0.2s ease',
            '&:hover': {
              boxShadow: '0 0 0 1px rgba(252, 4, 116, 0.2)',
            },
            '&.Mui-focused': {
              boxShadow: '0 0 0 2px rgba(252, 4, 116, 0.3)',
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          padding: '20px',
          borderRadius: '16px',
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.15)',
          backgroundImage: 'none',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': {
            boxShadow: '0 12px 20px rgba(0, 0, 0, 0.2)',
          },
        },
        elevation1: {
          boxShadow: '0 5px 10px rgba(0, 0, 0, 0.12)',
        },
        elevation2: {
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.15)',
        },
        elevation3: {
          boxShadow: '0 12px 20px rgba(0, 0, 0, 0.18)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: `linear-gradient(90deg, ${darkerBackground} 0%, ${pinkDark} 100%)`,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          borderRadius: '10px',
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: 'rgba(22, 22, 30, 0.9)',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
          borderRadius: '8px',
          padding: '8px 12px',
          fontSize: '0.85rem',
          border: `1px solid ${purple}`,
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          margin: '2px 4px',
          '&:hover': {
            backgroundImage: `linear-gradient(45deg, rgba(109, 22, 165, 0.1) 0%, rgba(252, 4, 116, 0.1) 100%)`,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          transition: 'all 0.2s ease',
          '&:hover': {
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
          },
        },
      },
    },
  },
});

export default theme; 