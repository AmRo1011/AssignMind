/**
 * AssignMind — User Type Definitions
 *
 * TypeScript interfaces mirroring the backend user schema.
 */

export interface User {
    id: string;
    email: string;
    full_name: string;
    avatar_url: string | null;
    phone: string | null;
    phone_verified: boolean;
    timezone: string;
    is_active: boolean;
    created_at: string;
}

export interface UserWithCredits extends User {
    credit_balance: number;
    credit_reserved: number;
    credit_available: number;
    low_credit_warning: boolean;
}

export type UserResponse = User;
