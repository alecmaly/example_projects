import type { User } from "./types";

export function formatUser(u: User): string {
    return `${u.id}:${u.name}`;
}

// Default export demo
export default function hello(msg: string): string {
    return `hello, ${msg}`;
}
