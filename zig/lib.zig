const std = @import("std");

pub fn helper() void {
    std.debug.print("from lib\n", .{});
}

pub const CONSTANT: u32 = 42;
