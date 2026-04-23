#!/bin/bash
# Bash "cast" catalogue — bash has dynamic types but several
# explicit coercions around integer/string/array.

# 1. Integer arithmetic expansion coerces its argument.
int_from_str() {
    local s="$1"
    echo $((s + 0))        # implicit cast to int; 'foo' becomes 0
}

# 2. printf with format specifier forces numeric/string formatting.
fmt_int()    { printf '%d\n' "$1"; }
fmt_float()  { printf '%.2f\n' "$1"; }
fmt_string() { printf '%s\n'  "$1"; }

# 3. declare -i marks a variable as integer — arithmetic context automatic.
declare_i_demo() {
    declare -i n
    n="2+3"        # evaluated as arithmetic (-> 5), not literal
    echo "n=$n"
}

# 4. declare -a / -A — explicit array / assoc-array typing.
declare_a_demo() {
    declare -a ixs=(1 2 3)
    declare -A m=([a]=1 [b]=2)
    echo "ixs len=${#ixs[@]} m keys=${!m[*]}"
}

# 5. [[ =~ ]] regex — string-pattern narrowing.
regex_narrow() {
    local s="$1"
    if [[ "$s" =~ ^[0-9]+$ ]]; then echo "all-digit"
    else echo "not-digit"
    fi
}

run_casts_demo_bash() {
    int_from_str 42
    int_from_str foo       # 0
    fmt_int 3
    fmt_float 3
    fmt_string 42
    declare_i_demo
    declare_a_demo
    regex_narrow "123"
    regex_narrow "ab"
}
