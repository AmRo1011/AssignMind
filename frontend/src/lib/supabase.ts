/**
 * AssignMind — Supabase Client
 *
 * Browser-side Supabase client for auth and storage.
 * Uses only NEXT_PUBLIC_* env vars (Constitution §II — no secrets).
 *
 * Lazy initialization to avoid build-time errors during SSR/SSG
 * when env vars may not be available.
 */

import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

let _supabase: SupabaseClient | null = null;

/**
 * Get the Supabase browser client (singleton, lazy-initialized).
 *
 * Throws at runtime if env vars are missing — never at build time.
 */
export function getSupabase(): SupabaseClient {
    if (_supabase) return _supabase;

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
        throw new Error(
            "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY"
        );
    }

    _supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);
    return _supabase;
}
