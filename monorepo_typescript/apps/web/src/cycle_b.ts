// C1.b — closes the cycle back to Alpha.
import type { Alpha } from './cycle_a';

export class Bravo {
    constructor(public tag: string) {}

    async bounceToAlpha(): Promise<string> {
        const { Alpha } = await import('./cycle_a');
        return new Alpha(`bounce-from-${this.tag}`).describe();
    }
}
