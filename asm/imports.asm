; NASM-style cross-file "imports" — catalogue every shape.

; 1. `extern` — declares a symbol defined in another module.
extern printf
extern function1

; 2. `global` — exports a symbol so other modules can `extern` it.
global imports_demo

; 3. `%include` — preprocessor file inclusion (text pastedel).
; %include "common.inc"     ; shape-only

; 4. `%import` — library module import (NASM's macro packages).
; %import "stdio.mac"       ; shape-only

section .data
    msg db "imports demo", 10, 0

section .text
imports_demo:
    push rbp
    mov rbp, rsp
    mov rdi, msg
    xor eax, eax
    call printf
    call function1
    mov rsp, rbp
    pop rbp
    ret
