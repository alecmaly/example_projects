section .data
    message db "This is function1", 10, 0
    local_var db "I'm local to function1", 0

section .text
    global function1
    extern printf

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