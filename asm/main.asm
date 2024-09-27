section .data
    global_var db "I'm global in main", 0
    format db "%s", 10, 0

section .text
    global main
    extern printf
    extern function1

main:
    push rbp
    mov rbp, rsp

    ; Print global variable
    mov rdi, format
    mov rsi, global_var
    xor eax, eax
    call printf

    ; Call function1
    call function1

    ; Call recursive function
    mov edi, 5
    call recursive_function

    mov rsp, rbp
    pop rbp
    xor eax, eax
    ret

recursive_function:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov [rbp-4], edi  ; Local variable n

    ; Check if n <= 0
    cmp dword [rbp-4], 0
    jle .end

    ; Print current level
    mov rdi, format
    mov esi, [rbp-4]
    xor eax, eax
    call printf

    ; Recursive call
    mov edi, [rbp-4]
    dec edi
    call recursive_function

.end:
    add rsp, 16
    pop rbp
    ret