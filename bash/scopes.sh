#!/bin/bash
# Labeled scope test cases for Bash. See SCOPE_TEST_SPEC.md at repo root.
# N/A for Bash: S09/S10/S11/S12/S13/S14 (no classes, no aliased import,
# no re-export, no nested namespaces). Covers S01..S08.

# -------------------------------------------------- S04 def / S05 write target
MODULE_VAR="mod-initial"                        # S04.def

s01_local() {
    local local_a="S01.local"                   # S01.def
    echo "$local_a"                             # S01.read
}

# Bash doesn't have true lexical closures; inner functions see outer's
# `local` vars because of dynamic scoping — that's the S02 stand-in.
s02_closure_read() {
    local outer_a="S02.outer"                   # S02.outer.def
    inner_reader() { echo "$outer_a"; }         # S02.inner.read (dynamic-scope capture)
    inner_reader
}

# S03: inner function writes to the outer local. Again via dynamic scoping.
s03_closure_write() {
    local counter=0                             # S03.outer.def
    bump() { counter=$((counter + 1)); }        # S03.inner.write
    bump; bump
    echo "$counter"                             # S03.outer.read
}

s05_same_module_write() {
    MODULE_VAR="rotated"                        # S05.write
    echo "$MODULE_VAR"                          # S05.read
}

# Cross-module read: MODULE1_GLOBAL comes from module1.sh, MODULE2_GLOBAL
# from module2.sh. These are "different modules" via `source`.
s06_cross_read() {
    echo "$MODULE1_GLOBAL"                      # S06.read
}

s07_cross_write() {
    set_module1_global "S07"                    # S07.write (indirect via helper)
}

s08_shadowing() {
    local MODULE_VAR="shadowed"                 # S08.shadow.def — local shadows file-scope
    echo "$MODULE_VAR"                          # S08.shadow.read
}

# Subshell: writes inside `( ... )` DO NOT propagate. Exercise for the
# extractor — the write inside must not be linked to the outer MODULE_VAR.
s_subshell_isolation() {
    local outer="visible"
    ( outer="mutated_in_subshell" )             # write in subshell — should NOT affect outer
    echo "after subshell: $outer"               # still "visible"
}

# Nameref — Bash 4.3+: a reference to another variable by name.
s_nameref() {
    local target="direct"
    local -n ref=target                         # nameref
    ref="via-nameref"                           # writes to `target`, not `ref`
    echo "after nameref write: $target"
}

run_scope_demo_bash() {
    s01_local
    s02_closure_read
    echo "counter=$(s03_closure_write)"
    s05_same_module_write
    s06_cross_read
    s07_cross_write
    s08_shadowing
    s_subshell_isolation
    s_nameref
}
