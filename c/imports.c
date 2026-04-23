/* C has only preprocessor-level "imports"; catalogue the forms here. */

/* 1. System include (angle brackets — searches -I system paths only). */
#include <stdio.h>

/* 2. Local include (double quotes — searches CWD first, then -I). */
#include "header1.h"

/* 3. Deeper path; relative. */
#include "header2.h"

/* 4. #include_next — GCC/Clang extension; used in header chaining. */
/*    Shape-only; commented out so compilation doesn't need the chain.    */
/* #include_next <stdio.h> */

/* 5. Conditional include. */
#ifdef __unix__
#include <unistd.h>
#else
/* could #include <windows.h> */
#endif

/* 6. Macro-defined include path (rare but legal). */
#define PICK_HEADER "header2.h"
#include PICK_HEADER

/* 7. External declaration — the closest C equivalent to "import symbol X". */
extern char* header1_global;

void imports_demo(void) {
    printf("header1_global = %s\n", header1_global);
    printf("HEADER2_CONSTANT = %s\n", HEADER2_CONSTANT);
}
