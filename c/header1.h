#ifndef HEADER1_H
#define HEADER1_H

/* Function-like macro (Phase 1 addition) — exercises preprocessor expansion. */
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define HEADER1_LABEL(name) "h1_" name

typedef struct {
    char* private_var;
} struct1_t;


struct1_t* create_struct1();
void destroy_struct1(struct1_t* s);
void method1(struct1_t* s);
char* get_header1_global(void);
void set_header1_global(char* v);

#endif