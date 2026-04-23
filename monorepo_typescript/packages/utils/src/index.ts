export function clamp(n: number, lo: number, hi: number): number {
    return Math.max(lo, Math.min(hi, n));
}

export const TAG = "utils";

// Side-effect export — consumers can `import "@mono/utils/boot"`
// to trigger this.
export function bootstrap(): void {
    // no-op registration
}
