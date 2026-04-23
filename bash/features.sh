#!/bin/bash
# Feature-coverage helpers sourced by main.sh.

# Readonly — the third declaration_command wrapper form.
readonly CONFIG_PATH="/etc/app.conf"

# Indexed array
declare -a INDEXED=(alpha beta gamma delta)

# Associative array (bash 4+)
declare -A ASSOC=(
    [host]="example.com"
    [port]="8080"
    [scheme]="https"
)

print_indexed() {
    echo "indexed len=${#INDEXED[@]}"
    for i in "${!INDEXED[@]}"; do
        echo "  [$i]=${INDEXED[$i]}"
    done
}

print_assoc() {
    echo "assoc len=${#ASSOC[@]}"
    for k in "${!ASSOC[@]}"; do
        echo "  $k=${ASSOC[$k]}"
    done
}

print_heredoc() {
    cat <<EOF
-- HEREDOC (expansions enabled) --
user=$USER host=${ASSOC[host]} port=${ASSOC[port]}
EOF

    cat <<'EOF'
-- HEREDOC (quoted — no expansion) --
literal $USER and ${ASSOC[host]}
EOF
}

# Command substitution + process substitution.
show_substitutions() {
    local now
    now=$(date +"%Y-%m-%dT%H:%M:%S")
    echo "now=$now"
    diff <(printf 'a\nb\nc\n') <(printf 'a\nb\nd\n') || true
}

run_feature_demo() {
    print_indexed
    print_assoc
    print_heredoc
    show_substitutions
}
