#ifndef LIBFOO_H
#define LIBFOO_H

#include <stddef.h>

/* Function-like macro across translation units. */
#define FOO_MIN(a, b)      ((a) < (b) ? (a) : (b))
#define FOO_CONCAT(a, b)   a##b

/* Opaque type definition. */
typedef struct foo_state foo_state_t;

/* Public API */
foo_state_t* foo_state_new(const char* name);
void         foo_state_free(foo_state_t* s);

int          foo_counter_get(void);
void         foo_counter_inc(void);
void         foo_counter_set(int v);   /* cross-TU WRITE target */

extern int   foo_error_code;           /* cross-TU mutable extern */

#endif
