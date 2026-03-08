/**
 * AssignMind — API Client
 *
 * Fetch wrapper that injects auth tokens and provides
 * standardized error handling for all backend API calls.
 */

import type { ErrorResponse } from "@/types/api";
import { getSupabase } from "@/lib/supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

/** Custom error with structured error details from the API */
export class ApiError extends Error {
    code: string;
    status: number;

    constructor(code: string, message: string, status: number) {
        super(message);
        this.code = code;
        this.status = status;
        this.name = "ApiError";
    }
}

/** Get the current session's access token. */
async function getAccessToken(): Promise<string | null> {
    const { data } = await getSupabase().auth.getSession();
    return data.session?.access_token ?? null;
}

/** Build headers with optional auth token. */
async function buildHeaders(
    includeAuth: boolean = true
): Promise<HeadersInit> {
    const headers: Record<string, string> = {
        "Content-Type": "application/json",
    };

    if (includeAuth) {
        const token = await getAccessToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }

    return headers;
}

/** Parse API error response into ApiError. */
async function handleErrorResponse(response: Response): Promise<never> {
    let code = "unknown_error";
    let message = "An unexpected error occurred";

    try {
        const body = (await response.json()) as ErrorResponse;
        code = body.error.code;
        message = body.error.message;
    } catch {
        message = response.statusText || message;
    }

    throw new ApiError(code, message, response.status);
}

/** Type-safe fetch wrapper with auth injection. */
async function apiFetch<T>(
    path: string,
    options: RequestInit = {},
    includeAuth: boolean = true
): Promise<T> {
    const url = `${API_BASE}${path}`;
    const headers = await buildHeaders(includeAuth);

    const response = await fetch(url, {
        ...options,
        headers: { ...headers, ...(options.headers ?? {}) },
    });

    if (!response.ok) {
        await handleErrorResponse(response);
    }

    return response.json() as Promise<T>;
}

/** GET request. */
export async function apiGet<T>(
    path: string,
    includeAuth: boolean = true
): Promise<T> {
    return apiFetch<T>(path, { method: "GET" }, includeAuth);
}

/** POST request with JSON body. */
export async function apiPost<T>(
    path: string,
    body?: unknown,
    includeAuth: boolean = true
): Promise<T> {
    return apiFetch<T>(
        path,
        { method: "POST", body: body ? JSON.stringify(body) : undefined },
        includeAuth
    );
}

/** PATCH request with JSON body. */
export async function apiPatch<T>(
    path: string,
    body: unknown,
    includeAuth: boolean = true
): Promise<T> {
    return apiFetch<T>(
        path,
        { method: "PATCH", body: JSON.stringify(body) },
        includeAuth
    );
}

/** DELETE request. */
export async function apiDelete<T>(
    path: string,
    includeAuth: boolean = true
): Promise<T> {
    return apiFetch<T>(path, { method: "DELETE" }, includeAuth);
}

/** POST multipart/form-data (file uploads). */
export async function apiUpload<T>(
    path: string,
    formData: FormData
): Promise<T> {
    const token = await getAccessToken();
    const headers: Record<string, string> = {};

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    // Don't set Content-Type — browser sets it with boundary
    const response = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers,
        body: formData,
    });

    if (!response.ok) {
        await handleErrorResponse(response);
    }

    return response.json() as Promise<T>;
}
