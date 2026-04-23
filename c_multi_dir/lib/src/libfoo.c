#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Relative include across directories — deliberately no -I flag, no Makefile. */
#include "../include/libfoo.h"

struct foo_state {
    char* name;
};

static int foo_counter = 0;
int foo_error_code = 0;

foo_state_t* foo_state_new(const char* name) {
    foo_state_t* s = (foo_state_t*)malloc(sizeof(foo_state_t));
    s->name = strdup(name);
    return s;
}

void foo_state_free(foo_state_t* s) {
    if (!s) return;
    free(s->name);
    free(s);
}

int  foo_counter_get(void)       { return foo_counter; }
void foo_counter_inc(void)       { foo_counter++; }
void foo_counter_set(int v)      { foo_counter = v; }
