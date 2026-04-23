const std = @import("std");

// Zig feature coverage: comptime, tagged unions, error unions, optional,
// defer/errdefer, structs, @fieldParentPtr, packed struct, inline for.

// --- Error set.
const ParseError = error{ Overflow, InvalidChar };

// --- Tagged union.
const Shape = union(enum) {
    circle: f64,
    square: f64,
    rectangle: struct { w: f64, h: f64 },
};

pub fn area(s: Shape) f64 {
    return switch (s) {
        .circle => |r| 3.14159 * r * r,
        .square => |side| side * side,
        .rectangle => |r| r.w * r.h,
    };
}

// --- comptime function.
pub fn Matrix(comptime T: type, comptime rows: comptime_int, comptime cols: comptime_int) type {
    return struct {
        data: [rows][cols]T,
        pub fn identity() @This() {
            var m: @This() = undefined;
            inline for (0..rows) |i| {
                inline for (0..cols) |j| {
                    m.data[i][j] = if (i == j) 1 else 0;
                }
            }
            return m;
        }
    };
}

// --- Error union.
pub fn parseByte(s: []const u8) ParseError!u8 {
    if (s.len == 0) return error.InvalidChar;
    var acc: u16 = 0;
    for (s) |c| {
        if (c < '0' or c > '9') return error.InvalidChar;
        acc = acc * 10 + (c - '0');
        if (acc > 255) return error.Overflow;
    }
    return @intCast(acc);
}

// --- Optional pointer.
pub fn firstByteOrNull(s: []const u8) ?u8 {
    if (s.len == 0) return null;
    return s[0];
}

// --- struct + init + method.
pub const Counter = struct {
    value: usize = 0,
    pub fn bump(self: *Counter) void {
        self.value += 1;
    }
};

// --- defer / errdefer for cleanup.
pub fn demoDefer() void {
    std.debug.print("start\n", .{});
    defer std.debug.print("deferred\n", .{});
    std.debug.print("middle\n", .{});
}

pub fn runFeatureDemo() void {
    std.debug.print("area circle={d}\n", .{area(.{ .circle = 2.0 })});
    std.debug.print("area rect ={d}\n", .{area(.{ .rectangle = .{ .w = 3, .h = 4 } })});

    const Mat3 = Matrix(f32, 3, 3);
    const m = Mat3.identity();
    std.debug.print("m[1][1]={d}\n", .{m.data[1][1]});

    if (parseByte("42")) |n| {
        std.debug.print("parseByte ok: {d}\n", .{n});
    } else |err| {
        std.debug.print("parseByte err: {}\n", .{err});
    }

    if (firstByteOrNull("hi")) |b| {
        std.debug.print("firstByte: {d}\n", .{b});
    }

    var c = Counter{};
    c.bump();
    c.bump();
    std.debug.print("counter={d}\n", .{c.value});

    demoDefer();
}
