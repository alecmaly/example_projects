#ifndef CYCLE_B_H
#define CYCLE_B_H

struct alpha;                           /* forward ref the other direction */

struct bravo {
    const char *tag;
    struct alpha *owner;
};

struct bravo *bravo_new(const char *tag);
const char   *bravo_bounce_to_alpha(const struct bravo *b);

#endif
