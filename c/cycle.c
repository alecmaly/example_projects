#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cycle_a.h"
#include "cycle_b.h"

void alpha_describe(const struct alpha *a) {
    printf("Alpha(%s)\n", a->name);
}

struct bravo *alpha_spawn_bravo(const struct alpha *a) {
    char *tag = malloc(strlen(a->name) + 3);
    strcpy(tag, a->name);
    strcat(tag, "/b");
    return bravo_new(tag);
}

struct bravo *bravo_new(const char *tag) {
    struct bravo *b = malloc(sizeof *b);
    b->tag = tag;
    b->owner = NULL;
    return b;
}

const char *bravo_bounce_to_alpha(const struct bravo *b) {
    static char buf[128];
    snprintf(buf, sizeof buf, "Alpha(bounce-from-%s)", b->tag);
    return buf;
}

const char *cycle_kick_off(void) {
    struct alpha a = { .name = "root", .child = NULL };
    struct bravo *b = alpha_spawn_bravo(&a);
    return bravo_bounce_to_alpha(b);
}
