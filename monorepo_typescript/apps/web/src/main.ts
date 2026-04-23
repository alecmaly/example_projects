// Ported coverage from the flat typescript/ fixture.
import { runScopeDemo } from "./scopes";
import { runFeatureDemo } from "./features";
import { runAdvancedDemo } from "./advanced";
import { runCastsDemo } from "./casts";
// T1 consumer — 3-level transitive chain: chain_deep ← chain_middle ← chain_origin.
import { VALUE_ALIAS, type DeepFlag } from "./chain_deep";
import "./imports";   // side-effect: catalogues every import form at load

// Named import via workspace path alias.
import { formatUser, DEFAULT_ROLE } from "@mono/shared";
// Default import + re-exported default.
import hello from "@mono/shared";
// Type-only import (stripped at runtime).
import type { User, Role } from "@mono/shared";
// Namespace import.
import * as utils from "@mono/utils";
// Aliased named import.
import { clamp as bounded } from "@mono/utils";
// Subpath import via package "exports".
import { formatUser as formatUserSubpath } from "@mono/shared/util";
// Side-effect import.
import "@mono/utils/side-effect";

async function main(): Promise<void> {
    const u: User = { id: 1, name: "alice" };
    const role: Role = DEFAULT_ROLE;
    console.log(hello(formatUser(u)));
    console.log("role:", role, "tag:", utils.TAG);
    console.log("clamped:", bounded(42, 0, 10));
    console.log("subpath:", formatUserSubpath(u));

    // Dynamic import (runtime-resolved).
    const mod = await import("@mono/shared/types");
    console.log("dynamic:", mod.DEFAULT_ROLE);

    // Exercise ported coverage.
    runFeatureDemo();
    runScopeDemo();
    await runAdvancedDemo();
    runCastsDemo();

    // Transitive chain sanity: must resolve to ORIGIN_VALUE defined in chain_origin.ts.
    console.log(`transitive: ${VALUE_ALIAS}`);
    const _flag: DeepFlag = { origin: true };
    void _flag;

    // Cycle sanity: cycle_a → cycle_b → cycle_a.
    const { kickOff } = await import('./cycle_a');
    console.log(`cycle: ${await kickOff()}`);
}

main();
