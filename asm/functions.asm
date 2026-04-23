; NASM multi-line macro — exercises preprocessor symbol extraction.
%macro PRINT_STR 1
    mov rdi, format
    mov rsi, %1
    xor eax, eax
    call printf
%endmacro

section .data
    message db "This is function1", 10, 0
    local_var db "I'm local to function1", 0

section .text
    global function1
    global set_shared
    extern printf
    extern shared_data    ; Phase 1: cross-file data symbol defined in main.asm

set_shared:
    ; Writes the passed rdi pointer into shared_data (cross-TU data WRITE).
    mov rax, shared_data
    mov [rax], rdi
    ret

function1:
    push rbp
    mov rbp, rsp

    mov rdi, message
    xor eax, eax
    call printf

    mov rdi, format
    mov rsi, local_var
    xor eax, eax
    call printf

    mov rsp, rbp
    pop rbp
    ret

section .data
    format db "%s", 10, 0