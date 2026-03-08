/**
 * AssignMind — API Type Definitions
 *
 * TypeScript interfaces mirroring backend Pydantic schemas.
 * Kept in sync with backend/app/schemas/common.py.
 */

/** Structured error detail from the API. */
export interface ErrorDetail {
    code: string;
    message: string;
}

/** Standard error response envelope. */
export interface ErrorResponse {
    error: ErrorDetail;
}

/** Generic paginated response from the API. */
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
}

/** Simple success message response. */
export interface MessageResponse {
    message: string;
}

/** Response containing a single UUID identifier. */
export interface IDResponse {
    id: string;
}

/** Health check response. */
export interface HealthResponse {
    status: string;
    database: string;
    version: string;
}
