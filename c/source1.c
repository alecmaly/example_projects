#include <stdio.h>
#include <stdlib.h>
#include "header1.h"

static char* header1_global = "I'm global in header1";

struct1_t* create_struct1() {
    struct1_t* s = malloc(sizeof(struct1_t));
    s->private_var = "I'm private";
    return s;
}

void destroy_struct1(struct1_t* s) {
    free(s);
}

void method1(struct1_t* s) {
    printf("This is method1 from struct1\n");
    printf("Private var: %s\n", s->private_var);
    private_method(s);
}

static void private_method(struct1_t* s) {
    printf("This is a private method in struct1\n");
    printf("Accessing global: %s\n", header1_global);
}

char* get_header1_global() {
    return header1_global;
}