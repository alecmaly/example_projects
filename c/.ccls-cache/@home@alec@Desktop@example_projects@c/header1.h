#ifndef HEADER1_H
#define HEADER1_H

typedef struct {
    char* private_var;
} struct1_t;

struct1_t* create_struct1();
void destroy_struct1(struct1_t* s);
void method1(struct1_t* s);

#endif