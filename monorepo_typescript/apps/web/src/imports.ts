// Exhaustive catalogue of TypeScript import/export forms — monorepo edition.
// Biased toward workspace-path-alias imports (@mono/...).

// 1. Named import from workspace pkg.
import { formatUser } from "@mono/shared";
// 2. Multiple named + renamed.
import { formatUser as format_user_alias, DEFAULT_ROLE } from "@mono/shared";
// 3. Namespace import.
import * as SharedNs from "@mono/shared";
// 4. Default import (shape-only — "@mono/shared" re-exports `hello` as default).
import hello from "@mono/shared";
// 5. Default + named combined.
import _ignored, { type User } from "@mono/shared";
// 6. Type-only import (elided at runtime).
import type { Role } from "@mono/shared";
// 7. Type-only *named* import with alias (inline type modifier).
import { type User as UserT } from "@mono/shared";
// 8. Side-effect import.
import "@mono/utils/side-effect";
// 9. Dynamic (async) import.
const lazyShared = () => import("@mono/shared/types");
// 10. Subpath import via package "exports".
import { formatUser as subpathFormatUser } from "@mono/shared/util";

// --- exports ---
export const PUBLIC_CONST = 1;
export function exported(): number { return PUBLIC_CONST; }
const a = 1, b = 2;
export { a, b };
const internal = 3;
export { internal as renamedExport };
export default function defaultExported(): string { return "default"; }
// Re-export (barrel).
export { formatUser as reExportedFormatUser } from "@mono/shared";
// Namespace re-export.
export * as ReShared from "@mono/shared";
// Wildcard re-export.
export * from "./features";

// -- usage guard so imports are actually referenced (analyzers care) --
void formatUser({ id: 0, name: "x" });
void format_user_alias({ id: 0, name: "x" });
void SharedNs.DEFAULT_ROLE;
void hello;
void _ignored;
void ({} as User);
void ({} as Role);
void ({} as UserT);
void lazyShared;
void subpathFormatUser({ id: 0, name: "x" });
