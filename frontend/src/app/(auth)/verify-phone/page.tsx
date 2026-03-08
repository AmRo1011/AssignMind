"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/AuthProvider";
import { apiPost } from "@/lib/api";
import { useToast } from "@/providers/ToastProvider";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";

export default function VerifyPhonePage() {
    const { session, isLoading: authLoading } = useAuth();
    const router = useRouter();
    const [step, setStep] = useState<"phone" | "otp">("phone");
    const [phone, setPhone] = useState("");

    useEffect(() => {
        if (!authLoading && !session) router.push("/login");
    }, [session, authLoading, router]);

    if (authLoading || !session) return null;

    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <div className="text-center mb-6">
                    <h2 className="text-xl font-bold font-[family-name:var(--font-outfit)]">
                        Verify your phone number
                    </h2>
                    <p className="text-sm text-muted mt-2">
                        Secures your account and prevents duplicate free credits.
                    </p>
                </div>
                {step === "phone" ? (
                    <SendOtpForm phone={phone} setPhone={setPhone} onSent={() => setStep("otp")} />
                ) : (
                    <VerifyOtpForm phone={phone} onResend={() => setStep("phone")} />
                )}
            </Card>
        </div>
    );
}

function SendOtpForm({ phone, setPhone, onSent }: { phone: string; setPhone: (v: string) => void; onSent: () => void }) {
    const [isLoading, setIsLoading] = useState(false);
    const { addToast } = useToast();

    const handleSend = async (e: FormEvent) => {
        e.preventDefault();
        if (!/^\+\d{7,15}$/.test(phone)) return addToast("error", "Invalid E.164 phone");
        try {
            setIsLoading(true);
            await apiPost("/auth/resend-otp", { phone });
            addToast("success", "OTP sent! (Use 123456 for testing)");
            onSent();
        } catch (err) {
            addToast("error", err instanceof Error ? err.message : "Failed");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSend} className="flex flex-col gap-4">
            <Input label="Phone Number" placeholder="+1234567890" value={phone}
                onChange={(e) => setPhone(e.target.value)} disabled={isLoading} required />
            <Button type="submit" isLoading={isLoading} className="w-full">Send SMS Code</Button>
        </form>
    );
}

function VerifyOtpForm({ phone, onResend }: { phone: string; onResend: () => void }) {
    const [otp, setOtp] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();
    const { addToast } = useToast();

    const handleVerify = async (e: FormEvent) => {
        e.preventDefault();
        if (otp.length !== 6) return addToast("error", "OTP must be 6 digits");
        try {
            setIsLoading(true);
            await apiPost("/auth/verify-phone", { phone, otp });
            addToast("success", "Phone verified! Welcome.");
            router.push("/");
        } catch (err) {
            addToast("error", err instanceof Error ? err.message : "Invalid OTP");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleVerify} className="flex flex-col gap-4">
            <Input label="6-Digit OTP" maxLength={6} value={otp} onChange={(e) => setOtp(e.target.value)}
                disabled={isLoading} autoFocus required />
            <Button type="submit" isLoading={isLoading} className="w-full">Verify Account</Button>
            <button type="button" onClick={onResend} className="text-sm text-primary hover:underline">
                Back to change phone or resend
            </button>
        </form>
    );
}
