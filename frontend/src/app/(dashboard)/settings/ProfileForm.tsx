"use client";

import { useState, type FormEvent } from "react";
import { apiPatch } from "@/lib/api";
import { useToast } from "@/providers/ToastProvider";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { UserWithCredits } from "@/types/user";
import { ProfileAvatar } from "./ProfileAvatar";

export function ProfileForm({ user }: { user: UserWithCredits }) {
    const [name, setName] = useState(user.full_name);
    const [isLoading, setIsLoading] = useState(false);
    const { addToast } = useToast();

    const handleSave = async (e: FormEvent) => {
        e.preventDefault();
        if (name.trim() === user.full_name) return;
        try {
            setIsLoading(true);
            await apiPatch("/users/me", { full_name: name });
            addToast("success", "Profile updated successfully");
        } catch (err) {
            addToast("error", err instanceof Error ? err.message : "Failed to update profile");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card>
            <CardHeader title="Profile Information" />
            <ProfileAvatar user={user} />
            <form onSubmit={handleSave} className="flex flex-col gap-4 mt-4">
                <Input label="Full Name" value={name} onChange={(e) => setName(e.target.value)}
                    disabled={isLoading} required />

                <div className="pt-2 flex justify-between items-center border-t border-border mt-2">
                    <div className="flex flex-col">
                        <span className="text-sm font-medium text-foreground">Available Credits</span>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-2xl font-bold text-primary font-[family-name:var(--font-outfit)]">{user.credit_available}</span>
                            <Badge variant="success">Active</Badge>
                        </div>
                    </div>
                    <Button type="submit" isLoading={isLoading} disabled={name.trim() === user.full_name}>
                        Save Changes
                    </Button>
                </div>
            </form>
        </Card>
    );
}
