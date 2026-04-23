// Labeled scope test cases for TypeScript — monorepo edition.
// Ported from typescript/scopes.ts. Cross-module refs now target the
// @mono/shared and @mono/utils workspace packages via path aliases.
// See SCOPE_TEST_SPEC.md at repo root.

import { formatUser as sharedFormatUser } from "@mono/shared";     // S09.def
import * as shared from "@mono/shared";                             // for S06/S07
import { reExportedValue } from "./scopes_reexport";                // S10.consumer.import
import { Widget } from "./scopes_ns/inner";                         // S14.import

// ------------------------------------------------ S04 def / S05 write target
export let moduleVar = "mod-initial";                               // S04.def

export function s01Local(): void {
    const localA = "S01.local";                                     // S01.def
    console.log(localA);                                            // S01.read
}

export function s02ClosureRead(): void {
    const outerA = "S02.outer";                                     // S02.outer.def
    const inner = () => console.log(outerA);                        // S02.inner.read
    inner();
}

export function s03ClosureWrite(): number {
    let counter = 0;                                                // S03.outer.def
    const bump = () => { counter++; };                              // S03.inner.write
    bump(); bump();
    return counter;                                                 // S03.outer.read
}

export function s05SameModuleWrite(): void {
    moduleVar = "rotated";                                          // S05.write
    console.log(moduleVar);                                         // S05.read
}

export function s06CrossRead(): string {
    return shared.DEFAULT_ROLE;                                     // S06.read
}

export function s07CrossWrite(): void {
    // Writing to an exported const isn't legal TS, so write to a
    // mutable namespace member instead. Exercises cross-pkg write.
    (shared as unknown as { DEFAULT_ROLE: string }).DEFAULT_ROLE = "S07"; // S07.write
}

export function s08Shadowing(): void {
    const moduleVar = "shadowed";                                   // S08.shadow.def
    console.log(moduleVar);                                         // S08.shadow.read
}

export function s09AliasedImport(): void {
    console.log(sharedFormatUser({ id: 1, name: "s09" }));          // S09.read
}

export function s10ReexportChain(): void {
    console.log(reExportedValue);                                   // S10.consumer.read
}

export class ScopeBase {
    static staticX = 1;                                             // S12.static.def / S13.base.def
    constructor(public x: number) {}                                // S11.instance.def (x)

    readInstance(x: number): number {
        return x + this.x;                                          // S11.param.read + S11.instance.read
    }
}

export class ScopeDerived extends ScopeBase {
    constructor() { super(5); }
    readInherited(): number {
        return ScopeBase.staticX;                                   // S13.derived.read
    }
}

export function s14Qualified(): string {
    return new Widget("hi").label;                                  // S14.read
}

export function runScopeDemo(): void {
    s01Local();
    s02ClosureRead();
    console.log(s03ClosureWrite());
    s05SameModuleWrite();
    console.log(s06CrossRead());
    s07CrossWrite();
    s08Shadowing();
    s09AliasedImport();
    s10ReexportChain();
    console.log(new ScopeBase(42).readInstance(100));
    console.log(new ScopeDerived().readInherited());
    console.log(s14Qualified());
}
