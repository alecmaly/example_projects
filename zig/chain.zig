// T1 transitive chain via 3 files — Zig needs explicit @import at each hop.

const origin = @import("chain_origin.zig");
const middle = @import("chain_middle.zig");
const deep   = @import("chain_deep.zig");

pub fn run() void {
    _ = origin.ORIGIN_VALUE;
    _ = middle.MIDDLE_VALUE;
    const alias: []const u8 = deep.VALUE_ALIAS;    // T1.consumer.read
    @import("std").debug.print("transitive: {s}\n", .{alias});
}
