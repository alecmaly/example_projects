// TypeScript feature coverage — ported from typescript/features.ts.
// Self-contained; exercises enums, discriminated unions, mapped types,
// conditional types, template-literal types, namespaces, overloads.

export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
}

export enum Protocol {
    HTTP  = "http",
    HTTPS = "https",
    WS    = "ws",
}

// Abstract class + concrete subclass — ported from the flat
// typescript/module2.ts so the monorepo retains abstract-class coverage.
export abstract class Animal {
    abstract speak(): string;
    describe(): string { return `${this.constructor.name} says ${this.speak()}`; }
}

export class Cat extends Animal {
    speak(): string { return "meow"; }
    // TS 4.3+ `override` modifier — overrides the concrete base method.
    override describe(): string { return `Cat-${this.speak()}`; }
}

// Further-derived class using `override` on a concrete method.
export class Kitten extends Cat {
    override speak(): string { return "mew"; }
}

// Concrete Circle class (separate from the Shape discriminated union
// below) — ports `typescript/module2.ts`'s `class Circle implements Shape`
// equivalent for the LSP's symbol tracker.
export class CircleClass {
    constructor(private r: number) {}
    readonly name = "Circle";
    area(): number { return Math.PI * this.r * this.r; }
}

export type Shape =
    | { kind: "circle";    r: number }
    | { kind: "square";    side: number }
    | { kind: "rectangle"; w: number; h: number };

export function area(s: Shape): number {
    switch (s.kind) {
        case "circle":    return Math.PI * s.r * s.r;
        case "square":    return s.side * s.side;
        case "rectangle": return s.w * s.h;
    }
}

export type DeepReadonly<T> = {
    readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

export type NonNullableKeys<T> = {
    [K in keyof T]: null extends T[K] ? never : K;
}[keyof T];

export type PickNonNullable<T> = Pick<T, NonNullableKeys<T>>;

export type EventName<T extends string> = `on${Capitalize<T>}`;

export namespace Geometry {
    export const PI = Math.PI;
    export function circumference(r: number) { return 2 * PI * r; }

    export namespace Solid {
        export function sphereVolume(r: number) { return (4 / 3) * PI * r ** 3; }
    }
}

export type HttpCall<Args extends unknown[]> = [url: string, ...args: Args];

export function toArray<T>(x: T[]): T[];
export function toArray<T>(x: T): [T];
export function toArray<T>(x: T | T[]): T[] {
    return Array.isArray(x) ? x : [x];
}

export function runFeatureDemo(): void {
    console.log(`area circle=${area({ kind: "circle",    r: 2 })}`);
    console.log(`area square=${area({ kind: "square",    side: 3 })}`);
    console.log(`area rect  =${area({ kind: "rectangle", w: 2, h: 5 })}`);

    console.log(`log level DEBUG=${LogLevel.DEBUG}, name=${LogLevel[LogLevel.DEBUG]}`);
    console.log(`proto = ${Protocol.HTTPS}`);

    console.log(`circ(5) = ${Geometry.circumference(5)}`);
    console.log(`sphereV(3) = ${Geometry.Solid.sphereVolume(3)}`);

    const a: number[] = toArray(7);
    const b: number[] = toArray([1, 2, 3]);
    console.log(`toArray ${a} / ${b}`);

    const call: HttpCall<[number, string]> = ["/api", 200, "ok"];
    console.log(`call = ${JSON.stringify(call)}`);

    type Event = EventName<"click">;
    const evt: Event = "onClick";
    console.log(`evt = ${evt}`);
}
