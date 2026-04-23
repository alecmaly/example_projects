; NASM cast catalogue — sign/zero extension + FP conversions.

section .data
    fmt_int db "int=%d", 10, 0
    fmt_flt db "flt=%f", 10, 0
    val8  db 0xFE              ; -2 as signed int8, 254 as unsigned
    valf  dd 3.14              ; single-precision float

section .text
    global casts_demo
    extern printf

casts_demo:
    push rbp
    mov rbp, rsp
    sub rsp, 16

    ; 1. Zero-extend: movzx — unsigned widen.
    movzx rax, byte [val8]     ; rax = 254 (zero-extended)

    ; 2. Sign-extend: movsx — signed widen.
    movsx rbx, byte [val8]     ; rbx = -2 (sign-extended)

    ; 3. Register-size implicit: low bits only.
    mov eax, 0xFFFFFFFF        ; upper bits zeroed automatically in x86-64

    ; 4. cdq — sign-extend EAX into EDX:EAX (for idiv).
    mov eax, -5
    cdq                        ; edx = 0xFFFFFFFF

    ; 5. cqo — 64-bit equivalent of cdq.
    mov rax, -5
    cqo                        ; rdx = 0xFFFFFFFFFFFFFFFF

    ; 6. cvtsi2sd — convert signed int → double.
    mov eax, 42
    cvtsi2sd xmm0, eax         ; xmm0 = 42.0

    ; 7. cvttsd2si — truncating convert double → signed int.
    cvttsd2si ebx, xmm0        ; ebx = 42

    ; 8. cvtps2pd — float → double.
    movss xmm1, [valf]
    cvtps2pd xmm2, xmm1

    add rsp, 16
    pop rbp
    ret
