export default {
  theme: {
    extend: {
      colors: {
        bg: '#0a0a0a',
        surface: '#111111',
        surface2: '#1a1a1a',
        border: '#2a2a2a',
        accent: '#e8ff00',
        'accent-dim': '#c8df00',
        text1: '#f0f0f0',
        text2: '#888888',
        text3: '#444444',
        danger: '#ff3b3b',
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
        sans: ['"DM Sans"', '"IBM Plex Sans"', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '2px',
        sm: '2px',
        md: '2px',
        lg: '4px',
        full: '9999px',
      },
      letterSpacing: {
        mono: '0.08em',
        'mono-wide': '0.12em',
      },
    },
  },
};