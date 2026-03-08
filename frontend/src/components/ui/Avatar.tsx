/**
 * AssignMind — Avatar Component
 *
 * User avatar with image, initials fallback, and size variants.
 */

import Image from "next/image";

type AvatarSize = "sm" | "md" | "lg";

interface AvatarProps {
    src?: string | null;
    name: string;
    size?: AvatarSize;
    className?: string;
}

const SIZE_MAP: Record<AvatarSize, { container: string; text: string; px: number }> = {
    sm: { container: "h-8 w-8", text: "text-xs", px: 32 },
    md: { container: "h-10 w-10", text: "text-sm", px: 40 },
    lg: { container: "h-14 w-14", text: "text-lg", px: 56 },
};

function getInitials(name: string): string {
    return name
        .split(" ")
        .map((part) => part[0])
        .filter(Boolean)
        .slice(0, 2)
        .join("")
        .toUpperCase();
}

export function Avatar({ src, name, size = "md", className = "" }: AvatarProps) {
    const sizeConfig = SIZE_MAP[size];

    if (src) {
        return (
            <Image
                src={src}
                alt={name}
                width={sizeConfig.px}
                height={sizeConfig.px}
                className={`${sizeConfig.container} rounded-full object-cover ${className}`}
            />
        );
    }

    return (
        <div
            className={`${sizeConfig.container} rounded-full bg-primary/10 text-primary flex items-center justify-center font-semibold ${sizeConfig.text} ${className}`}
            aria-label={name}
        >
            {getInitials(name)}
        </div>
    );
}
