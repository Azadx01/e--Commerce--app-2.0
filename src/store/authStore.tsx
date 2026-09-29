import React, {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useState,
    ReactNode,
} from 'react';
import { authService, UserRead } from '../services/authService';

// ─── State Shape ──────────────────────────────────────────────────────────────
interface AuthState {
    user: UserRead | null;
    isAuthenticated: boolean;
    isLoading: boolean; // true during initial "restore session" check
}

// ─── Actions ──────────────────────────────────────────────────────────────────
interface AuthContextValue extends AuthState {
    signIn: (email: string, password: string) => Promise<void>;
    signUp: (name: string, email: string, password: string) => Promise<void>;
    signOut: () => Promise<void>;
    refreshUser: () => Promise<void>;
}

// ─── Context ──────────────────────────────────────────────────────────────────
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// ─── Provider ─────────────────────────────────────────────────────────────────
export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<UserRead | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    /**
     * On mount: if a token exists in AsyncStorage, try to fetch the user.
     * This restores session across app launches.
     */
    useEffect(() => {
        const restoreSession = async () => {
            try {
                const hasToken = await authService.hasToken();
                if (hasToken) {
                    const me = await authService.getMe();
                    setUser(me);
                }
            } catch {
                // Token invalid / expired — stay logged out
                setUser(null);
            } finally {
                setIsLoading(false);
            }
        };
        restoreSession();
    }, []);

    const signIn = useCallback(async (email: string, password: string) => {
        await authService.login({ username: email, password });
        const me = await authService.getMe();
        setUser(me);
    }, []);

    const signUp = useCallback(async (name: string, email: string, password: string) => {
        // Register then immediately log in
        await authService.register({ name, email, password, role: 'customer' });
        await authService.login({ username: email, password });
        const me = await authService.getMe();
        setUser(me);
    }, []);

    const signOut = useCallback(async () => {
        await authService.logout();
        setUser(null);
    }, []);

    const refreshUser = useCallback(async () => {
        const me = await authService.getMe();
        setUser(me);
    }, []);

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: !!user,
                isLoading,
                signIn,
                signUp,
                signOut,
                refreshUser,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

// ─── Hook ─────────────────────────────────────────────────────────────────────
export const useAuth = (): AuthContextValue => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within an <AuthProvider>');
    return ctx;
};
