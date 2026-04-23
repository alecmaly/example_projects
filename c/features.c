#include <stdio.h>
#include <stdarg.h>
#include <string.h>

/* Enum */
typedef enum {
    COLOR_RED   = 0,
    COLOR_GREEN = 1,
    COLOR_BLUE  = 2,
    COLOR_MAX
} color_t;

/* Union */
typedef union {
    int   as_int;
    float as_float;
    char  as_bytes[4];
} scalar_t;

/* Struct with bitfields */
typedef struct {
    unsigned int is_active : 1;
    unsigned int is_admin  : 1;
    unsigned int level     : 4;   /* 0..15 */
    unsigned int flags     : 10;
} perm_t;

/* Varargs — classic printf-style */
static int sum_ints(int count, ...) {
    va_list ap;
    int s = 0;
    va_start(ap, count);
    for (int i = 0; i < count; i++) s += va_arg(ap, int);
    va_end(ap);
    return s;
}

void run_c_feature_demo(void) {
    color_t c = COLOR_GREEN;
    printf("color = %d of %d total\n", (int)c, (int)COLOR_MAX);

    scalar_t s;
    s.as_float = 3.14f;
    printf("as_float=%f as_int=0x%08x bytes=%02x%02x%02x%02x\n",
        s.as_float, s.as_int,
        (unsigned char)s.as_bytes[0], (unsigned char)s.as_bytes[1],
        (unsigned char)s.as_bytes[2], (unsigned char)s.as_bytes[3]);

    perm_t p = { .is_active = 1, .is_admin = 0, .level = 7, .flags = 0x2A };
    printf("perm: active=%u admin=%u level=%u flags=0x%x\n",
        p.is_active, p.is_admin, p.level, p.flags);

    printf("sum(1,2,3,4) = %d\n", sum_ints(4, 1, 2, 3, 4));
}

/* Function-pointer typedef */
typedef int (*binop_t)(int, int);

/* Leaf ops with the binop_t shape */
static int add_ii(int a, int b) { return a + b; }
static int sub_ii(int a, int b) { return a - b; }
static int mul_ii(int a, int b) { return a * b; }

/* Dispatch table */
static binop_t binops[3] = { add_ii, sub_ii, mul_ii };

int dispatch(int which, int a, int b) {
    if (which < 0 || which >= 3) return 0;
    return binops[which](a, b);
}

/* _Generic selection macro — C11 */
#define typestr(x) _Generic((x), \
    int:     "int",              \
    double:  "double",           \
    default: "other")

/* Variadic sum — summing `n` ints off the va_list */
int sum_n(int n, ...) {
    va_list ap;
    int s = 0;
    va_start(ap, n);
    for (int i = 0; i < n; i++) s += va_arg(ap, int);
    va_end(ap);
    return s;
}
