// C1.a — ES module cycle with a type-only ref to cycle_b.
// ES modules load cyclic imports as partial modules; at runtime one
// side will see undefined exports until the other side finishes.
// Type-only imports (`import type`) are elided so cause no cycle.

import type { Bravo } from './cycle_b';

export class Alpha {
    constructor(public name: string) {}

    async spawnBravo(): Promise<Bravo> {
        // Dynamic import at call time — safe even in a cycle.
        const { Bravo } = await import('./cycle_b');
        return new Bravo(`${this.name}/b`);
    }

    describe(): string {
        return `Alpha(${this.name})`;
    }
}

export async function kickOff(): Promise<string> {
    const a = new Alpha('root');
    const b = await a.spawnBravo();
    return b.bounceToAlpha();
}
