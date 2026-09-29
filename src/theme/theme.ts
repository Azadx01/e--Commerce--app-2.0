export const theme = {
    colors: {
        primary: '#007AFF', // ReVivo main blue
        background: '#F2F2F7', // Light gray background
        surface: '#FFFFFF', // Card/Input backgrounds
        text: '#1C1C1E',
        textSecondary: '#8E8E93',
        error: '#FF3B30',
        success: '#34C759',
        border: '#C6C6C8',
    },
    spacing: {
        xs: 4,
        s: 8,
        m: 16,
        l: 24,
        xl: 32,
        xxl: 48,
    },
    borderRadius: {
        s: 4,
        m: 8,
        l: 12,
    },
    typography: {
        h1: { fontSize: 32, fontWeight: '700' },
        h2: { fontSize: 24, fontWeight: '600' },
        body: { fontSize: 16, fontWeight: '400' },
        caption: { fontSize: 12, fontWeight: '400' },
    }
} as const;
