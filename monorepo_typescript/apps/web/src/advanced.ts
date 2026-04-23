// TypeScript advanced-feature coverage ported from the flat typescript/.
// Covers: async iterator + `for await`, Promise-based async/await, function
// overload signatures, generic class with constraint, ambient .d.ts
// consumption, primordials pattern.

/// <reference path="../typings/primordials.d.ts" />

// --- function overloading via overload signatures ---
export function addOverload(a: number, b: number): number;
export function addOverload(a: string, b: string): string;
export function addOverload(a: any, b: any): any {
    return a + b;
}

// --- generic class with constraint ---
export class NumberProcessor<T extends number | bigint> {
    process(input: T): T {
        return input;
    }
}

// --- async generator / async iterator ---
export async function* generateSequence(): AsyncIterableIterator<number> {
    for (let i = 0; i < 5; i++) {
        await new Promise(resolve => setTimeout(resolve, 10));
        yield i;
    }
}

// --- Promise-based async with .catch / Promise.all ---
export async function parallelFetch(): Promise<number[]> {
    const jobs = [1, 2, 3].map(async (n) => {
        await new Promise(resolve => setTimeout(resolve, 5));
        return n * 2;
    });
    return Promise.all(jobs);
}

// --- conditional promise handling ---
export function maybeReject(flag: boolean): Promise<string> {
    return flag
        ? Promise.resolve("ok")
        : Promise.reject(new Error("nope"));
}

export async function runAdvancedDemo(): Promise<void> {
    console.log("overload num:", addOverload(5, 3));
    console.log("overload str:", addOverload("hi", "there"));

    console.log("generic:", new NumberProcessor<number>().process(10));

    for await (const item of generateSequence()) {
        console.log("stream item:", item);
    }

    console.log("parallel:", await parallelFetch());

    try {
        const r = await maybeReject(false);
        console.log("unexpected:", r);
    } catch (e) {
        console.log("caught:", (e as Error).message);
    }

    // primordials — exercise the ambient `.d.ts` declaration.
    const keys = primordials.ObjectKeys({ a: 1, b: 2 });
    console.log("keys:", keys);
}

// --- conditional type with `infer` ---
export type ElementOf<T> = T extends (infer U)[] ? U : never;

// --- mapped type + key-remapped mapped type ---
export type OptionalAll<T> = { [K in keyof T]?: T[K] };
export type GettersOf<T> = { [K in keyof T & string as `get_${K}`]: () => T[K] };

// --- template literal type + distributive conditional ---
export type EventNameAdv<T extends string> = `on_${T}_event`;
export type Boxed<T> = T extends any ? { v: T } : never;
export type BoxedUnion = Boxed<string | number>;

// --- `satisfies` operator ---
export const cfgAdv = { port: 8080, host: "local" } satisfies { port: number; host: string };

// --- const assertion + indexed access ---
export const TUPLE_ADV = [1, "a", true] as const;
export type TupleFirst = (typeof TUPLE_ADV)[0];

// --- namespace with nested namespace ---
export namespace AdvNS {
    export type Level = "info" | "warn";
    export const LEVELS: Level[] = ["info", "warn"];
    export namespace Nested {
        export function tag(l: Level) {
            return `[${l}]`;
        }
    }
}

// external usage of the namespace
export const advNsTagged = AdvNS.Nested.tag(AdvNS.LEVELS[0]);
