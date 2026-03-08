import type { ReactNode } from "react";

export function generateStaticParams() {
    // Return an empty array to indicate that there are no statically known workspace IDs at build time.
    // This allows Next.js static export to pass without errors.
    // The client-side will handle fetching and routing dynamically.
    return [];
}

export default function WorkspaceLayout({ children }: { children: ReactNode }) {
    return children;
}
