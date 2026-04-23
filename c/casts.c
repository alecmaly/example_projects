/* C cast catalogue. */

#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* 1. C-style cast. */
static int narrow(long l) { return (int) l; }

/* 2. Pointer cast — reinterpret. */
static uint32_t bits_of_float(float f) {
    /* Technically UB via strict-aliasing — memcpy is the portable form. */
    uint32_t u;
    memcpy(&u, &f, sizeof u);
    return u;
}

/* 3. Compound literal (C99) — cast-like struct initialization. */
typedef struct { int x, y; } point_t;
static point_t origin(void) {
    return (point_t){ .x = 0, .y = 0 };    /* compound literal */
}

/* 4. Union-based reinterpret (alternative to memcpy). */
typedef union {
    float f;
    uint32_t u;
} float_bits_t;
static uint32_t union_bits(float f) {
    float_bits_t b = { .f = f };
    return b.u;
}

/* 5. void* cast — erases/restores type. */
static void set_any(void *p, int v) {
    *(int *)p = v;
}

/* 6. Function-pointer cast. */
typedef int (*int_fn)(int);
static int square(int n) { return n * n; }
static void fn_cast_demo(void) {
    int_fn f = square;             /* implicit assignment fine */
    int_fn g = (int_fn) (void *) square;  /* explicit cast through void* */
    printf("f=%d g=%d\n", f(3), g(4));
}

/* 7. sizeof + implicit numeric promotion. */
static void promotion_demo(void) {
    char c = 'A';
    int i = c;       /* implicit char → int promotion */
    double d = i;    /* implicit int → double */
    printf("c=%c i=%d d=%f\n", c, i, d);
}

void run_casts_demo_c(void) {
    printf("narrow = %d\n", narrow(1000000000000L));
    printf("bits(1.0f) = 0x%08x\n", bits_of_float(1.0f));
    point_t p = origin();
    printf("origin = (%d,%d)\n", p.x, p.y);
    printf("union_bits(2.0f) = 0x%08x\n", union_bits(2.0f));
    int n = 0;
    set_any(&n, 42);
    printf("void* write = %d\n", n);
    fn_cast_demo();
    promotion_demo();
}
