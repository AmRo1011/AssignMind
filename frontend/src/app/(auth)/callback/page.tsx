"use client";

/**
 * AssignMind — Auth Callback Page
 *
 * Handles Supabase OAuth redirect, syncs user with the Python backend,
 * and navigates to the correct page based on phone verification.
 */

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/AuthProvider";
import { apiPost } from "@/lib/api";
import { useToast } from "@/providers/ToastProvider";
import { Spinner } from "@/components/ui/Spinner";

export default function CallbackPage() {
    const { session, isLoading } = useAuth();
    const router = useRouter();
    const { addToast } = useToast();
    const hasSyncedObj = useRef(false);

    useEffect(() => {
        if (isLoading || !session || hasSyncedObj.current) return;

        hasSyncedObj.current = true;
        syncUser();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [session, isLoading]);

    const syncUser = async () => {
        try {
            if (!session?.user) throw new Error("No user in session");

            const payload = {
                supabase_id: session.user.id,
                email: session.user.email!,
                full_name: session.user.user_metadata?.full_name || session.user.email?.split("@")[0] || "User",
                avatar_url: session.user.user_metadata?.avatar_url || null,
            };

            const { user } = await apiPost<{ user: any; is_new: boolean }>("/auth/callback", payload, false);

            if (!user.is_active) {
                router.push("/reactivate");
            } else if (!user.phone_verified) {
                router.push("/verify-phone");
            } else {
                router.push("/");
            }
        } catch (error) {
            addToast("error", "Failed to sync user data");
            router.push("/login");
        }
    };

    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-surface gap-4">
            <Spinner size="lg" />
            <p className="text-muted text-sm font-medium">Completing sign in...</p>
        </div>
    );
}
