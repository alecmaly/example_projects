#include <stdio.h>
#include "header2.h"

static char* header2_global = "I'm global in header2";

void function1(void) {
    printf("This is function1 from source2.c\n");
    printf("Accessing constant: %s\n", HEADER2_CONSTANT);
    internal_function();
}

static void internal_function(void) {
    printf("This is an internal function in source2.c\n");
}

char* get_header2_global(void) {
    return header2_global;
}

// Example math operations
static int add(int a, int b) { return a + b; }
static int subtract(int a, int b) { return a - b; }

int perform_operation(int a, int b, MathOperation operation) {
    return operation(a, b);
}

// Usage example (can be called from main.c)
void demonstrate_function_pointer(void) {
    printf("Add result: %d\n", perform_operation(5, 3, add));
    printf("Subtract result: %d\n", perform_operation(5, 3, subtract));
}