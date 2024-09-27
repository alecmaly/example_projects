#ifndef HEADER2_H
#define HEADER2_H

#define HEADER2_CONSTANT "I'm a constant in header2"

void function1(void);
char* get_header2_global(void);

// Function pointer type definition
typedef int (*MathOperation)(int, int);

// Function that takes a function pointer
int perform_operation(int a, int b, MathOperation operation);

#endif