"use client";

/**
 * AssignMind — Dashboard Layout Wrapper
 *
 * Ensures the user has verified their phone number. If verified,
 * renders the Sidebar and the Header alongside page children.
 */

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Spinner } from "@/components/ui/Spinner";

export default function DashboardLayout({ children }: { children: ReactNode }) {
    const { user, isLoading } = useCurrentUser();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading) {
            if (!user) {
                router.push("/login");
            } else if (!user.phone_verified) {
                router.push("/verify-phone");
            }
        }
    }, [user, isLoading, router]);

    if (isLoading || !user || !user.phone_verified) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background">
                <Spinner size="lg" />
            </div>
        );
    }

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar />
            <div className="flex-1 flex flex-col relative overflow-hidden">
                <Header />
                <main className="flex-1 overflow-auto p-8">{children}</main>
            </div>
        </div>
    );
}
