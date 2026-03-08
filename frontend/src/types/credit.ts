export interface CreditTransaction {
    id: string;
    user_id: string;
    type: string;
    amount: number;
    description: string | null;
    reference_id: string | null;
    created_at: string;
}

export interface CheckoutUrl {
    checkout_url: string;
}
