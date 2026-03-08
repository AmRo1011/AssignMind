"use client";

/**
 * AssignMind — Root Providers Wrapper
 *
 * Client component that wraps all context providers.
 * Imported by the root layout to keep it as a server component.
 */

import { useEffect, type ReactNode } from "react";
import { AuthProvider } from "@/providers/AuthProvider";
import { ToastProvider } from "@/providers/ToastProvider";

interface ProvidersProps {
    children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
    useEffect(() => {
        if ("serviceWorker" in navigator) {
            navigator.serviceWorker.register("/sw.js").catch(() => { });
        }
    }, []);

    return (
        <AuthProvider>
            <ToastProvider>{children}</ToastProvider>
        </AuthProvider>
    );
}
