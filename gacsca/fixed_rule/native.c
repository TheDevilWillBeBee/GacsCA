/* Exact CPU execution of the fixed radius-one rule. No table/ROM/depth access. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>

enum { KIND, INDEX, A, B, D, BIT, HEAD, PHASE, PC, RA, RB, RD, VALUE, FIELDS };
enum { MEM, GATE, LOOP, INERT };
enum { FETCH, READ_A, READ_B, WRITE };

void fr_local(const uint32_t *l, const uint32_t *c, uint32_t *o) {
    memcpy(o, c, FIELDS * sizeof(uint32_t));
    if (c[HEAD] && c[KIND] == MEM && c[PHASE] == WRITE && c[INDEX] == c[RD])
        o[BIT] = c[VALUE];
    o[HEAD] = l[HEAD];
    for (int j = PHASE; j < FIELDS; ++j) o[j] = l[HEAD] ? l[j] : 0;
    if (!l[HEAD]) return;
    if (l[PHASE] == FETCH && l[INDEX] == l[PC]) {
        if (l[KIND] == GATE) {
            o[PHASE] = READ_A; o[RA] = l[A]; o[RB] = l[B]; o[RD] = l[D];
        } else if (l[KIND] == LOOP) o[PC] = 0;
    } else if (l[KIND] == MEM) {
        if (l[PHASE] == READ_A && l[INDEX] == l[RA]) {
            o[VALUE] = l[BIT]; o[PHASE] = READ_B;
        } else if (l[PHASE] == READ_B && l[INDEX] == l[RB]) {
            o[VALUE] = 1 - (l[VALUE] & l[BIT]); o[PHASE] = WRITE;
        } else if (l[PHASE] == WRITE && l[INDEX] == l[RD]) {
            o[PC] = (l[PC] + 1) & 65535; o[PHASE] = FETCH;
        }
    }
}

void fr_dense(const uint32_t *cells, uint32_t *out, size_t n) {
    for (size_t p = 0; p < n; ++p)
        fr_local(cells + ((p + n - 1) % n) * FIELDS,
                 cells + p * FIELDS, out + p * FIELDS);
}

/* Sparse evaluation of a proved invariant: exactly one head, and all controller
   fields at non-head cells zero. All other sites are fixed points of fr_local.
   Every physical tick is executed: two local evaluations, no event skipping,
   global lookup, or replacement of a represented transition. */
int fr_run(uint32_t *cells, size_t n, uint64_t limit, uint64_t periods,
           uint64_t *ticks, uint64_t *completed) {
    size_t p = 0, heads = 0;
    uint32_t here[FIELDS], there[FIELDS], zero[FIELDS] = {0};
    *ticks = 0; *completed = 0;
    if (!n) return -1;
    for (size_t i = 0; i < n; ++i) {
        const uint32_t *c = cells + i * FIELDS;
        if (c[HEAD]) { p = i; ++heads; }
        else for (int j = PHASE; j < FIELDS; ++j) if (c[j]) return -2;
    }
    if (heads != 1) return -3;
    while (*ticks < limit && (!periods || *completed < periods)) {
        uint32_t *c = cells + p * FIELDS;
        int boundary = c[KIND] == LOOP && c[PHASE] == FETCH && c[PC] == c[INDEX];
        size_t next = (p + 1 == n) ? 0 : p + 1;
        if (n == 1) {
            fr_local(c, c, here);
            memcpy(c, here, sizeof here);
        } else {
            uint32_t *r = cells + next * FIELDS;
            fr_local(zero, c, here);
            fr_local(c, r, there);
            memcpy(c, here, sizeof here);
            memcpy(r, there, sizeof there);
        }
        p = next; ++*ticks;
        if (boundary) ++*completed;
    }
    return 0;
}
