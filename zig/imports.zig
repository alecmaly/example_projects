// Zig's module-reference forms.

// 1. @import stdlib.
const std = @import("std");

// 2. @import local file.
const lib = @import("lib.zig");

// 3. Re-export via pub const.
pub const helper = lib.helper;

// 4. Destructure — pull individual names into local constants.
const debug = std.debug;
const print = std.debug.print;
const ArrayList = std.ArrayList;

pub fn importsDemo() void {
    print("hello from imports\n", .{});
    debug.assert(true);
    const list = ArrayList(i32).init(std.heap.page_allocator);
    _ = list;
    lib.helper();
    helper();
}
