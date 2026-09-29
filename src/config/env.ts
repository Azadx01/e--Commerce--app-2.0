import Constants from 'expo-constants';

/**
 * Centralized environment configuration.
 *
 * Checks EXPO_PUBLIC_API_URL first (inlined from .env by Expo CLI),
 * then falls back to detecting the Metro host or the machine's LAN IP.
 */
const getDevApiBaseUrl = (): string => {
    if (process.env.EXPO_PUBLIC_API_URL) {
        return process.env.EXPO_PUBLIC_API_URL;
    }
    const hostUri = Constants.expoConfig?.hostUri ?? (Constants as any).expoGoConfig?.debuggerHost;
    if (hostUri) {
        const host = hostUri.split(':')[0];
        return `http://${host}:8000/api/v1`;
    }
    return 'http://192.168.1.5:8000/api/v1';
};

const ENV = {
    development: {
        API_BASE_URL: getDevApiBaseUrl(),
    },
    production: {
        API_BASE_URL: 'https://api.revivo.app/api/v1',
    },
};

type EnvKey = keyof typeof ENV;

const currentEnv: EnvKey = __DEV__ ? 'development' : 'production';

export const config = ENV[currentEnv];
