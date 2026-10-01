import Constants from 'expo-constants';
import { Platform } from 'react-native';

declare const process: {
    env?: {
        EXPO_PUBLIC_API_URL?: string;
        [key: string]: string | undefined;
    };
};

/**
 * Centralized environment configuration.
 *
 * Checks EXPO_PUBLIC_API_URL first (inlined from .env by Expo CLI),
 * then falls back to detecting the Metro host or the machine's LAN IP.
 */
const getDevApiBaseUrl = (): string => {
    try {
        if (typeof process !== 'undefined' && process?.env?.EXPO_PUBLIC_API_URL) {
            return process.env.EXPO_PUBLIC_API_URL;
        }
    } catch {
        // Ignore process reference errors
    }

    try {
        const hostUri =
            Constants?.expoConfig?.hostUri ??
            (Constants as any)?.expoGoConfig?.debuggerHost ??
            (Constants as any)?.manifest?.debuggerHost ??
            (Constants as any)?.manifest2?.extra?.expoGo?.debuggerHost;
        if (hostUri && typeof hostUri === 'string') {
            const host = hostUri.split(':')[0];
            if (host && host !== 'localhost' && host !== '127.0.0.1') {
                return `http://${host}:8000/api/v1`;
            }
        }
    } catch {
        // Fall back gracefully if manifest cannot be read
    }

    return 'http://192.168.1.6:8000/api/v1';
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

const currentEnv: EnvKey = typeof __DEV__ !== 'undefined' && __DEV__ ? 'development' : 'production';

export const config = ENV[currentEnv];
