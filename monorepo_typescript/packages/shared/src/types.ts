// Pure type module — imported as `import type` in consumers.
export interface User {
    id: number;
    name: string;
}

export type Role = "admin" | "user" | "guest";

export const DEFAULT_ROLE: Role = "user";
