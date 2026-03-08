"use client";

/**
 * AssignMind — Login Page
 *
 * Google and GitHub OAuth login buttons.
 */

import { useState } from "react";
import { getSupabase } from "@/lib/supabase";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { useToast } from "@/providers/ToastProvider";

export default function LoginPage() {
    const [isLoading, setIsLoading] = useState<"google" | "github" | null>(null);
    const { addToast } = useToast();

    const handleOAuthLogin = async (provider: "google" | "github") => {
        try {
            setIsLoading(provider);
            const supabase = getSupabase();

            const { error } = await supabase.auth.signInWithOAuth({
                provider,
                options: {
                    redirectTo: `${window.location.origin}/callback`,
                },
            });

            if (error) throw error;
        } catch (error) {
            setIsLoading(null);
            const msg = error instanceof Error ? error.message : "Login failed";
            addToast("error", msg);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-surface p-4">
            <Card className="w-full max-w-md">
                <div className="text-center mb-6">
                    <h1 className="text-2xl font-bold font-[family-name:var(--font-outfit)] text-foreground mb-2">
                        Welcome to AssignMind
                    </h1>
                    <p className="text-sm text-muted">
                        Sign in to start collaborating with your team
                    </p>
                </div>

                <div className="flex flex-col gap-3">
                    <Button
                        variant="secondary"
                        onClick={() => handleOAuthLogin("google")}
                        isLoading={isLoading === "google"}
                        disabled={isLoading !== null}
                        className="w-full flex justify-center gap-2"
                    >
                        Google
                    </Button>

                    <Button
                        variant="secondary"
                        onClick={() => handleOAuthLogin("github")}
                        isLoading={isLoading === "github"}
                        disabled={isLoading !== null}
                        className="w-full flex justify-center gap-2"
                    >
                        GitHub
                    </Button>
                </div>
            </Card>
        </div>
    );
}
