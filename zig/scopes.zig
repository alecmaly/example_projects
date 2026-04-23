// Labeled scope test cases for Zig. See SCOPE_TEST_SPEC.md.

const std = @import("std");
const lib = @import("lib.zig");                     // for S06 cross-file read

// --- S04 def / S05 write target.
pub var module_var: u32 = 1;                        // S04.def

pub fn s01Local() void {
    const local_a: []const u8 = "S01.local";        // S01.def
    std.debug.print("{s}\n", .{local_a});           // S01.read
}

pub fn s05SameModuleWrite() void {
    module_var = 2;                                 // S05.write
    std.debug.print("{d}\n", .{module_var});        // S05.read
}

pub fn s06CrossRead() u32 {
    return lib.CONSTANT;                            // S06.read
}

pub fn s08Shadowing() void {
    const module_var: u32 = 999;                    // S08.shadow.def
    std.debug.print("{d}\n", .{module_var});        // S08.shadow.read
}

// --- S11: struct-field vs param collision.
pub const ScopeBase = struct {
    x: i32,                                         // S11.instance.def
    pub fn readInstance(self: ScopeBase, x: i32) i32 {
        return x + self.x;                          // S11.param.read + S11.instance.read
    }
};

// S14: namespace-qualified type reference (nested struct in a namespace struct).
pub const scope_ns = struct {
    pub const Widget = struct {                     // S14.Widget.def
        label: []const u8,
    };
};

pub fn s14Qualified() []const u8 {
    const w = scope_ns.Widget{ .label = "hi" };
    return w.label;                                 // S14.read
}

pub fn runScopeDemo() void {
    s01Local();
    s05SameModuleWrite();
    std.debug.print("cross={d}\n", .{s06CrossRead()});
    s08Shadowing();
    const b = ScopeBase{ .x = 42 };
    std.debug.print("s11={d}\n", .{b.readInstance(100)});
    std.debug.print("s14={s}\n", .{s14Qualified()});
}
