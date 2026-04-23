#include <stdio.h>
#include "header1.h"
#include "header2.h"

char* global_var = "I'm global in main";

void recursive_function(int n) {
    if (n <= 0) return;
    printf("Recursion level: %d\n", n);
    recursive_function(n - 1);
}

int main() {
    char* local_var = "I'm local to main";
    printf("%s\n", global_var);
    printf("%s\n", local_var);
    printf("Imported constant: %s\n", HEADER2_CONSTANT);

    struct1_t* obj = create_struct1();
    method1(obj);

    function1();
    recursive_function(5);

    // Accessing module-level variables (reads)
    printf("Header1 global: %s\n", get_header1_global());
    printf("Header2 global: %s\n", get_header2_global());

    // Cross-TU WRITE
    set_header1_global("rotated-from-main");
    printf("Header1 global after: %s\n", get_header1_global());

    // Function-like macro expansion
    printf("MAX(3, 7) = %d\n", MAX(3, 7));
    printf("label: %s\n", HEADER1_LABEL("hello"));

    // Enum / union / bitfield / varargs
    run_c_feature_demo();

    // Labeled scope test cases
    run_scope_demo_c();

    destroy_struct1(obj);
    return 0;
}