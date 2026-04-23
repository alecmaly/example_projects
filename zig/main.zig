const std = @import("std");
pub const GREETING: []const u8 = "hi";

pub const Greeter = struct {
    prefix: []const u8 = GREETING,
    pub fn greet(self: Greeter, name: []const u8) void {
        std.debug.print("{s} {s}\n", .{ self.prefix, name });
    }
};

pub fn main() void {
    const g = Greeter{};
    g.greet("world");
}
