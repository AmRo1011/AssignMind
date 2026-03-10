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
                    <SendOtpForm setPhone={setPhone} onSent={() => setStep("otp")} />
                ) : (
                    <VerifyOtpForm phone={phone} onResend={() => setStep("phone")} />
                )}
            </Card>
        </div>
    );
}

const COUNTRIES = [
    { code: "+20", label: "🇪🇬 +20", name: "Egypt" },
    { code: "+1", label: "🇺🇸 +1", name: "US/Canada" },
    { code: "+44", label: "🇬🇧 +44", name: "UK" },
    { code: "+971", label: "🇦🇪 +971", name: "UAE" },
    { code: "+966", label: "🇸🇦 +966", name: "Saudi Arabia" },
    { code: "+965", label: "🇰🇼 +965", name: "Kuwait" },
    { code: "+974", label: "🇶🇦 +974", name: "Qatar" },
    { code: "+973", label: "🇧🇭 +973", name: "Bahrain" },
    { code: "+968", label: "🇴🇲 +968", name: "Oman" },
    { code: "+962", label: "🇯🇴 +962", name: "Jordan" },
    { code: "+961", label: "🇱🇧 +961", name: "Lebanon" },
    { code: "+212", label: "🇲🇦 +212", name: "Morocco" },
    { code: "+213", label: "🇩🇿 +213", name: "Algeria" },
    { code: "+216", label: "🇹🇳 +216", name: "Tunisia" },
    { code: "+970", label: "🇵🇸 +970", name: "Palestine" },
    { code: "+964", label: "🇮🇶 +964", name: "Iraq" },
    { code: "+218", label: "🇱🇾 +218", name: "Libya" },
    { code: "+249", label: "🇸🇩 +249", name: "Sudan" },
    { code: "+963", label: "🇸🇾 +963", name: "Syria" },
    { code: "+967", label: "🇾🇪 +967", name: "Yemen" },
    { code: "+49", label: "🇩🇪 +49", name: "Germany" },
    { code: "+33", label: "🇫🇷 +33", name: "France" },
    { code: "+39", label: "🇮🇹 +39", name: "Italy" },
    { code: "+34", label: "🇪🇸 +34", name: "Spain" },
    { code: "+61", label: "🇦🇺 +61", name: "Australia" },
];

function SendOtpForm({ setPhone, onSent }: { setPhone: (v: string) => void; onSent: () => void }) {
    const [isLoading, setIsLoading] = useState(false);
    const { addToast } = useToast();
    const [countryCode, setCountryCode] = useState("+20");
    const [localNumber, setLocalNumber] = useState("");

    const handleSend = async (e: FormEvent) => {
        e.preventDefault();
        const fullPhone = `${countryCode}${localNumber}`;
        if (!/^\+\d{7,15}$/.test(fullPhone)) return addToast("error", "Invalid E.164 phone");
        try {
            setIsLoading(true);
            await apiPost("/auth/resend-otp", { phone: fullPhone });
            setPhone(fullPhone);
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
            <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium">Phone Number</label>
                <div className="flex gap-2">
                    <select
                        value={countryCode}
                        onChange={(e) => setCountryCode(e.target.value)}
                        disabled={isLoading}
                        className="w-[110px] flex h-10 items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {COUNTRIES.map((c) => (
                            <option key={c.code} value={c.code}>
                                {c.label}
                            </option>
                        ))}
                    </select>
                    <div className="flex-1">
                        <Input
                            placeholder="1234567890"
                            value={localNumber}
                            onChange={(e) => setLocalNumber(e.target.value.replace(/\D/g, ''))}
                            disabled={isLoading}
                            required
                        />
                    </div>
                </div>
            </div>
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
