// Import from the same shared package as apps/web — tests that the
// path alias resolves from multiple consumers.
import { formatUser, type User } from "@mono/shared";

const u: User = { id: 99, name: "cli-user" };
console.log(formatUser(u));
