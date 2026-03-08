"use client";

/**
 * AssignMind — Current User Hook
 *
 * Fetches the backend user profile using the Supabase JWT.
 */

import { useState, useCallback, useEffect } from "react";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/providers/AuthProvider";
import type { UserWithCredits } from "@/types/user";

interface UseCurrentUserReturn {
    user: UserWithCredits | null;
    isLoading: boolean;
    error: Error | null;
    refresh: () => Promise<void>;
}

export function useCurrentUser(): UseCurrentUserReturn {
    const { session, isLoading: authLoading } = useAuth();
    const [user, setUser] = useState<UserWithCredits | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const refresh = useCallback(async () => {
        if (!session) {
            setUser(null);
            setIsLoading(false);
            return;
        }

        try {
            setIsLoading(true);
            setError(null);
            const data = await apiGet<UserWithCredits>("/auth/me");
            setUser(data);
        } catch (err) {
            setError(err instanceof Error ? err : new Error("Failed to fetch user"));
        } finally {
            setIsLoading(false);
        }
    }, [session]);

    useEffect(() => {
        if (!authLoading) {
            refresh();
        }
    }, [authLoading, refresh]);

    return { user, isLoading: isLoading || authLoading, error, refresh };
}
