#ifndef CYCLE_A_H
#define CYCLE_A_H

/* Forward-declare struct bravo so alpha can hold a pointer to it. */
struct bravo;

struct alpha {
    const char *name;
    struct bravo *child;                /* forward-declared pointer */
};

void alpha_describe(const struct alpha *a);
struct bravo *alpha_spawn_bravo(const struct alpha *a);
const char *cycle_kick_off(void);

#endif
