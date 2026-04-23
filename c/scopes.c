/* Labeled scope test cases for C. See SCOPE_TEST_SPEC.md at repo root.
 * N/A for C: S02/S03 (no closures), S09 (no aliased import), S10 (no
 * re-export), S12 (no class/static distinction — translation-unit-level
 * statics cover it), S13 (no inheritance), S14 (no nested namespaces).
 */

#include <stdio.h>
#include "header2.h"                /* for cross-TU reference in S06/S07 */

/* ------------------------------------------------- S04 def / S05 write target */
int module_var = 1;                 /* S04.def */
extern char* header2_global_ref;    /* referenced cross-TU for S06 — see below */

void s01_local(void) {
    int local_a = 123;              /* S01.def */
    printf("%d\n", local_a);        /* S01.read */
}

void s05_same_module_write(void) {
    module_var = 2;                 /* S05.write */
    printf("%d\n", module_var);     /* S05.read */
}

const char* s06_cross_read(void) {
    return get_header2_global();    /* S06.read — resolves to source2.c's static */
}

/* S07 cross-TU write: main.c already has set_header1_global();
 * use it here to exercise the write path from a different call site. */
void s07_cross_write(void) {
    extern void set_header1_global(char* v);
    set_header1_global("S07");      /* S07.write */
}

void s08_shadowing(void) {
    int module_var = 999;           /* S08.shadow.def — block-local shadows file scope */
    printf("%d\n", module_var);     /* S08.shadow.read */
    {
        int module_var = 7;         /* nested shadow of the shadow */
        printf("%d\n", module_var); /* must resolve to nested, not outer */
    }
}

/* S11: struct member vs parameter name collision. */
typedef struct {
    int x;                          /* S11.instance.def */
} ScopeBase;

int read_instance(ScopeBase* b, int x) {
    return x + b->x;                /* S11.param.read + S11.instance.read */
}

void run_scope_demo_c(void) {
    s01_local();
    s05_same_module_write();
    printf("S06 read: %s\n", s06_cross_read());
    s07_cross_write();
    s08_shadowing();
    ScopeBase b = { .x = 42 };
    printf("S11: %d\n", read_instance(&b, 100));
}
