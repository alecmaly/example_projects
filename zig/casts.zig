const std = @import("std");

// 1. @as — explicit type coercion.
pub fn asCast() void {
    const n = @as(u32, 42);
    _ = n;
}

// 2. @intCast — truncating/widening int conversion (compile-time-checked range).
pub fn intCast(big: i64) !u8 {
    if (big < 0 or big > 255) return error.OutOfRange;
    return @intCast(big);
}

// 3. @floatCast — f32 ↔ f64.
pub fn floatCast(d: f64) f32 {
    return @floatCast(d);
}

// 4. @intFromFloat / @floatFromInt.
pub fn floatIntRoundtrip(f: f64) f64 {
    const i: i64 = @intFromFloat(f);
    return @floatFromInt(i);
}

// 5. @ptrCast — reinterpret pointer.
pub fn ptrCast(p: *const u32) *const [4]u8 {
    return @ptrCast(p);
}

// 6. @bitCast — bit-level reinterpretation.
pub fn bitCast(f: f32) u32 {
    return @bitCast(f);
}

// 7. @enumFromInt / @intFromEnum.
pub const Color = enum(u8) { red, green, blue };

pub fn enumCast() void {
    const n: u8 = @intFromEnum(Color.green);
    const c: Color = @enumFromInt(n);
    _ = c;
}

// 8. @truncate — explicit narrowing.
pub fn truncate(big: u32) u8 {
    return @truncate(big);
}

// 9. @errorCast / @errorFromInt (error-set casts).
const ErrA = error{One};
const ErrAB = error{One, Two};
pub fn errWiden(e: ErrA) ErrAB {
    return e;                // Zig permits implicit widening to a wider error set.
}

pub fn runCastsDemo() void {
    asCast();
    if (intCast(200)) |v| std.debug.print("intCast ok {d}\n", .{v}) else |err| std.debug.print("err {}\n", .{err});
    _ = floatCast(3.14);
    _ = floatIntRoundtrip(4.7);
    const n: u32 = 0x12345678;
    _ = ptrCast(&n);
    std.debug.print("bitCast {x}\n", .{bitCast(1.0)});
    enumCast();
    std.debug.print("truncate {d}\n", .{truncate(0x1234)});
}
