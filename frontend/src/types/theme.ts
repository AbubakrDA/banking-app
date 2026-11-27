export interface ThemeTokens {
  colors: {
    canvas: string;
    surface: {
      default: string;
      subdued: string;
      hover: string;
      selected: string;
    };
    text: {
      primary: string;
      secondary: string;
      muted: string;
      inverted: string;
    };
    accent: {
      teal: string;
      tealHover: string;
      tealLight: string;
      blue: string;
      blueHover: string;
      blueLight: string;
    };
    status: {
      success: string;
      warning: string;
      danger: string;
      info: string;
    };
    border: {
      subtle: string;
      default: string;
      focus: string;
    };
  };
  radii: {
    sm: string;
    md: string;
    card: string;
    xl: string;
    full: string;
  };
  shadows: {
    subtle: string;
    card: string;
    cardHover: string;
    elevation: string;
  };
}

export type ThemeMode = 'light' | 'dark';
