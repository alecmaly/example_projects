// Exhaustive TypeScript cast / type-assertion catalogue.

// 1. `as` type assertion — the canonical form.
const a = 42 as unknown as string;

// 2. `<T>` angle-bracket form (legacy; disallowed in .tsx).
const b = <number>3;

// 3. Non-null assertion.
function firstChar(s?: string) {
    return s!.charAt(0);                 // `!` asserts non-null
}

// 4. `as const` — literal type freezing.
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number];        // 'admin' | 'user' | 'guest'

// 5. `satisfies` (TS 4.9+) — checks against a shape WITHOUT widening.
const config = {
    host: 'localhost',
    port: 8080,
} satisfies { host: string; port: number };

// 6. Type narrowing via `typeof`.
function narrow(x: string | number): number {
    if (typeof x === 'string') return x.length;   // narrowed to string
    return x;                                      // narrowed to number
}

// 7. Type narrowing via `instanceof`.
class Ape { swing(): void {} }
class Fish { swim(): void {} }
function move(a: Ape | Fish): void {
    if (a instanceof Ape) a.swing(); else a.swim();
}

// 8. Discriminated-union narrowing.
type Shape =
    | { kind: 'circle'; r: number }
    | { kind: 'rect'; w: number; h: number };
function area(s: Shape): number {
    switch (s.kind) {
        case 'circle': return Math.PI * s.r * s.r;
        case 'rect':   return s.w * s.h;
    }
}

// 9. `in` operator narrowing.
interface A { kind: 'a'; x: number; }
interface B { kind: 'b'; y: number; }
function readXOrY(o: A | B): number {
    return 'x' in o ? o.x : o.y;
}

// 10. `as` with generic (user-defined type guard function).
function isString(x: unknown): x is string {
    return typeof x === 'string';
}

// 11. Bracketed keyed access cast.
const mapped: Record<string, number> = { a: 1, b: 2 };
const v: number = mapped['a'];

// 12. Explicit object cast via `as`.
interface User { name: string; }
const u: User = JSON.parse('{"name":"alice"}') as User;

export function runCastsDemo(): void {
    console.log(a, b, firstChar('hi'));
    const r: Role = 'admin';
    console.log(r, config);
    console.log(narrow('foo'), narrow(42));
    move(new Ape());
    console.log(area({ kind: 'circle', r: 2 }));
    console.log(readXOrY({ kind: 'a', x: 9 }));
    const x: unknown = 'y';
    if (isString(x)) console.log(x.length);
    console.log(v, u.name);
}
