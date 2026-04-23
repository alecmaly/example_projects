// Zig forbids @import cycles between files — the compiler will error out.
// The idiomatic way to express A↔B in Zig is to put both types in ONE
// file using `*const @This()` / `*Other` pointer indirection.

const std = @import("std");

pub const Alpha = struct {
    name: []const u8,
    child: ?*const Bravo = null,              // pointer to forward-referenced type

    pub fn describe(self: Alpha) void {
        std.debug.print("Alpha({s})\n", .{self.name});
    }
};

pub const Bravo = struct {
    tag: []const u8,
    owner: ?*const Alpha = null,

    pub fn bounceToAlpha(self: Bravo) void {
        const a = Alpha{ .name = "bounce-from" };
        _ = self;
        a.describe();
    }
};

pub fn run() void {
    const a = Alpha{ .name = "root" };
    const b = Bravo{ .tag = "b", .owner = &a };
    b.bounceToAlpha();
}
