#include <stdio.h>

/* Cross-dir include — relative from app/ to lib/include/. */
#include "../lib/include/libfoo.h"

int main(void) {
    foo_state_t* s = foo_state_new("demo");
    printf("counter start: %d\n", foo_counter_get());
    foo_counter_inc();
    foo_counter_set(FOO_MIN(7, 12));       /* cross-TU WRITE via setter */
    foo_error_code = 42;                   /* direct cross-TU extern WRITE */
    printf("counter now: %d, err=%d\n", foo_counter_get(), foo_error_code);
    foo_state_free(s);
    return 0;
}
