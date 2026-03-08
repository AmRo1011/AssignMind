"use client";

/**
 * AssignMind — Auth Provider
 *
 * Wraps Supabase auth session listener. Provides user, session,
 * and loading state to all child components via React Context.
 */

import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
    type ReactNode,
} from "react";
import type { Session, User } from "@supabase/supabase-js";
import { getSupabase } from "@/lib/supabase";

interface AuthContextValue {
    user: User | null;
    session: Session | null;
    isLoading: boolean;
    signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
    user: null,
    session: null,
    isLoading: true,
    signOut: async () => { },
});

interface AuthProviderProps {
    children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [session, setSession] = useState<Session | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const client = getSupabase();

        // Get initial session
        client.auth.getSession().then(({ data: { session: s } }) => {
            setSession(s);
            setIsLoading(false);
        });

        // Listen for auth state changes
        const {
            data: { subscription },
        } = client.auth.onAuthStateChange((_event, newSession) => {
            setSession(newSession);
            setIsLoading(false);
        });

        return () => subscription.unsubscribe();
    }, []);

    const signOut = useCallback(async () => {
        await getSupabase().auth.signOut();
        setSession(null);
    }, []);

    const value: AuthContextValue = {
        user: session?.user ?? null,
        session,
        isLoading,
        signOut,
    };

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
}

/** Hook to access auth context. Must be used within AuthProvider. */
export function useAuth(): AuthContextValue {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
