/**
 * AssignMind — Client-Side Input Sanitization
 *
 * Strip dangerous HTML from user inputs before display.
 * This is a defense-in-depth layer — the backend also sanitizes
 * (Constitution §III).
 */

import DOMPurify from "dompurify";

/** Strip ALL HTML tags from user input text. */
export function sanitizeText(input: string): string {
    return DOMPurify.sanitize(input, {
        ALLOWED_TAGS: [],
        ALLOWED_ATTR: [],
    });
}

/** Strip HTML and enforce max length. */
export function sanitizeAndTrim(input: string, maxLength: number = 5000): string {
    const cleaned = sanitizeText(input).trim();
    return cleaned.slice(0, maxLength);
}

/** Check if a string is empty or whitespace-only. */
export function isEmptyOrWhitespace(input: string | null | undefined): boolean {
    if (input == null) return true;
    return input.trim().length === 0;
}
