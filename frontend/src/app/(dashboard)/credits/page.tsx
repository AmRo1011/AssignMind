"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { UserWithCredits } from "@/types/user";
import { CreditTransaction, CheckoutUrl } from "@/types/credit";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function CreditsPage() {
    const [user, setUser] = useState<UserWithCredits | null>(null);
    const [transactions, setTransactions] = useState<CreditTransaction[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [buying, setBuying] = useState<string | null>(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);

            const userRes = await apiGet<UserWithCredits>("/api/credits/balance");
            setUser(userRes);

            const txRes = await apiGet<CreditTransaction[]>("/api/credits/transactions?limit=20&offset=0");
            setTransactions(txRes);
        } catch (err: any) {
            setError(err.message || "Failed to load credits data");
        } finally {
            setLoading(false);
        }
    };

    const handleCheckout = async (packageType: string) => {
        try {
            setBuying(packageType);
            setError(null);
            const urlRes = await apiPost<CheckoutUrl>(`/api/credits/checkout/${packageType}`, {});
            window.location.href = urlRes.checkout_url;
        } catch (err: any) {
            setError(err.message || "Failed to initialize checkout.");
            setBuying(null);
        }
    };

    if (loading && !user) return (
        <div className="flex h-full items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
    );

    return (
        <div className="mx-auto max-w-5xl space-y-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">Credits & Billing</h1>
                <p className="text-muted-foreground">Manage your AI tokens and payment history.</p>
            </div>

            {error && (
                <div className="text-sm font-medium text-red-500 bg-red-500/10 border border-red-500/20 p-4 rounded-md">
                    {error}
                </div>
            )}

            {user?.low_credit_warning && (
                <div className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-red-500">
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    <p className="font-medium">
                        Low Credit Warning: You have {user.credit_available} credits left. Please recharge to avoid service interruptions.
                    </p>
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card className="flex flex-col gap-2 p-6 md:col-span-2">
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <svg className="h-5 w-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <h3 className="font-semibold">Available Balance</h3>
                    </div>
                    <p className="text-4xl font-bold text-foreground">
                        {user?.credit_available?.toLocaleString() || 0} <span className="text-lg font-medium text-muted-foreground">Credits</span>
                    </p>
                    <div className="mt-4 flex gap-4 text-sm text-muted-foreground">
                        <div>
                            <span className="font-medium">Total:</span> {user?.credit_balance?.toLocaleString() || 0}
                        </div>
                        <div>
                            <span className="font-medium">Reserved:</span> {user?.credit_reserved?.toLocaleString() || 0}
                        </div>
                    </div>
                </Card>
            </div>

            <div className="space-y-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
                    Purchase Credits
                </h2>
                <div className="grid gap-6 md:grid-cols-3">
                    {[
                        { id: "starter", name: "Starter", credits: 100, price: "$2.00", color: "bg-blue-500/10 text-blue-500 border-blue-500/20" },
                        { id: "standard", name: "Standard", credits: 300, price: "$5.00", color: "bg-purple-500/10 text-purple-500 border-purple-500/20" },
                        { id: "pro", name: "Pro", credits: 700, price: "$10.00", color: "bg-amber-500/10 text-amber-500 border-amber-500/20" },
                    ].map((pkg) => (
                        <Card key={pkg.id} className="relative flex flex-col justify-between p-6">
                            <div className="space-y-4">
                                <div className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors ${pkg.color}`}>
                                    {pkg.name}
                                </div>
                                <div>
                                    <h3 className="text-3xl font-bold">{pkg.credits}</h3>
                                    <p className="text-muted-foreground">AI Credits</p>
                                </div>
                                <p className="text-xl font-medium">{pkg.price}</p>
                            </div>
                            <div className="mt-8">
                                <Button
                                    className="w-full"
                                    isLoading={buying === pkg.id}
                                    disabled={buying !== null}
                                    onClick={() => handleCheckout(pkg.id)}
                                >
                                    Buy {pkg.name}
                                </Button>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>

            <div className="space-y-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Transaction Ledger
                </h2>
                <Card className="overflow-hidden">
                    {transactions.length === 0 ? (
                        <div className="p-8 text-center text-muted-foreground">
                            No transactions found.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">
                                <thead className="border-b bg-muted/40 text-muted-foreground">
                                    <tr>
                                        <th className="h-12 px-6 font-medium">Date</th>
                                        <th className="h-12 px-6 font-medium">Type</th>
                                        <th className="h-12 px-6 font-medium">Amount</th>
                                        <th className="h-12 px-6 font-medium">Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {transactions.map((tx) => (
                                        <tr key={tx.id} className="border-b transition-colors hover:bg-muted/40 last:border-0">
                                            <td className="p-6">{new Date(tx.created_at).toLocaleDateString()} {new Date(tx.created_at).toLocaleTimeString()}</td>
                                            <td className="p-6">
                                                <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${tx.type === "grant" || tx.type === "release" ? "bg-green-500/10 text-green-500" :
                                                    tx.type === "commit" ? "bg-red-500/10 text-red-500" :
                                                        tx.type === "reservation" ? "bg-amber-500/10 text-amber-500" :
                                                            "bg-muted text-muted-foreground"
                                                    }`}>
                                                    {tx.type.charAt(0).toUpperCase() + tx.type.slice(1)}
                                                </span>
                                            </td>
                                            <td className={`p-6 font-medium ${tx.amount > 0 ? "text-green-500" : "text-red-500"}`}>
                                                {tx.amount > 0 ? "+" : ""}{tx.amount}
                                            </td>
                                            <td className="p-6 text-muted-foreground">{tx.description || "-"}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </Card>
            </div>
        </div>
    );
}
