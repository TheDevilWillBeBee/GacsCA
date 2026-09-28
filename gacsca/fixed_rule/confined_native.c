/* Fixed 138-bit radius-one rule. All evolution dependencies are in l/c/r. */
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

enum { KIND, INDEX, A, B, D, BIT, HEAD, PHASE, PC, RA, RB, RD, VALUE,
       FIRST, LAST, DIRECTION, FIELDS };
enum { MEM, GATE, LOOP, INERT };
enum { FETCH, READ_A, READ_B, WRITE };

static void advance(const uint32_t *c, uint32_t *o) {
    for (int j = PHASE; j <= VALUE; ++j) o[j] = c[j];
    if (c[PHASE] == FETCH && c[INDEX] == c[PC]) {
        if (c[KIND] == GATE) {
            o[PHASE] = READ_A; o[RA] = c[A]; o[RB] = c[B]; o[RD] = c[D];
        } else if (c[KIND] == LOOP) o[PC] = 0;
    } else if (c[KIND] == MEM) {
        if (c[PHASE] == READ_A && c[INDEX] == c[RA]) {
            o[VALUE] = c[BIT]; o[PHASE] = READ_B;
        } else if (c[PHASE] == READ_B && c[INDEX] == c[RB]) {
            o[VALUE] = 1 - (c[VALUE] & c[BIT]); o[PHASE] = WRITE;
        } else if (c[PHASE] == WRITE && c[INDEX] == c[RD]) {
            o[PC] = (c[PC] + 1) & 65535; o[PHASE] = FETCH;
        }
    }
}

void fc_local(const uint32_t *l, const uint32_t *c, const uint32_t *r, uint32_t *o) {
    memcpy(o, c, FIELDS * sizeof(uint32_t));
    o[HEAD] = 0; o[DIRECTION] = 0;
    for (int j = PHASE; j <= VALUE; ++j) o[j] = 0;
    if (r[HEAD] && r[DIRECTION] && !r[FIRST]) {
        o[HEAD] = 1; o[DIRECTION] = 1;
        for (int j = PHASE; j <= VALUE; ++j) o[j] = r[j];
    }
    if (l[HEAD] && !l[DIRECTION] && !l[LAST]) {
        o[HEAD] = 1; o[DIRECTION] = 0; advance(l, o);
    }
    if (c[HEAD] && ((!c[DIRECTION] && c[LAST]) || (c[DIRECTION] && c[FIRST]))) {
        o[HEAD] = 1; o[DIRECTION] = !c[DIRECTION];
        if (!c[DIRECTION]) advance(c, o);
        else for (int j = PHASE; j <= VALUE; ++j) o[j] = c[j];
    }
    if (c[HEAD] && !c[DIRECTION] && c[KIND] == MEM && c[PHASE] == WRITE && c[INDEX] == c[RD])
        o[BIT] = c[VALUE];
}

void fc_dense(const uint32_t *cells, uint32_t *out, size_t n) {
    for (size_t p = 0; p < n; ++p)
        fc_local(cells + ((p + n - 1) % n) * FIELDS, cells + p * FIELDS,
                 cells + ((p + 1) % n) * FIELDS, out + p * FIELDS);
}

/* Exact sparse evolution, including head collisions. The head index list is an
   execution cache; all changed values are produced by fc_local on OLD neighbors.
   Dirty sets contain the union of radius-one neighborhoods of all old heads.
   Headless cells with zero controller fields outside that set are fixed points.
   No cell geometry, colony count, rule description, or hierarchy depth is input. */
int fc_run(uint32_t *cells, size_t n, uint64_t ticks, uint64_t *evaluations) {
    size_t *heads = malloc(n * sizeof(size_t));
    size_t *dirty = malloc(n * sizeof(size_t));
    uint8_t *marked = calloc(n, sizeof(uint8_t));
    uint32_t *outputs = malloc(n * FIELDS * sizeof(uint32_t));
    int code = 0;
    size_t count = 0;
    *evaluations = 0;
    if (!heads || !dirty || !marked || !outputs) { code = -1; goto done; }
    for (size_t p = 0; p < n; ++p) {
        const uint32_t *c = cells + p * FIELDS;
        if (c[HEAD]) heads[count++] = p;
        else {
            for (int j = PHASE; j <= VALUE; ++j) if (c[j]) { code = -2; goto done; }
            if (c[DIRECTION]) { code = -2; goto done; }
        }
    }
    for (uint64_t tick = 0; tick < ticks; ++tick) {
        size_t size = 0;
        for (size_t i = 0; i < count; ++i) {
            size_t p = heads[i];
            size_t positions[3] = {p ? p - 1 : n - 1, p, p + 1 == n ? 0 : p + 1};
            for (int j = 0; j < 3; ++j) {
                size_t q = positions[j];
                if (!marked[q]) { marked[q] = 1; dirty[size++] = q; }
            }
        }
        for (size_t i = 0; i < size; ++i) {
            size_t p = dirty[i], l = p ? p - 1 : n - 1, r = p + 1 == n ? 0 : p + 1;
            fc_local(cells + l * FIELDS, cells + p * FIELDS,
                     cells + r * FIELDS, outputs + i * FIELDS);
        }
        count = 0;
        for (size_t i = 0; i < size; ++i) {
            size_t p = dirty[i];
            const uint32_t *o = outputs + i * FIELDS;
            memcpy(cells + p * FIELDS, o, FIELDS * sizeof(uint32_t));
            if (o[HEAD]) heads[count++] = p;
            marked[p] = 0;
        }
        *evaluations += size;
    }
 done:
    free(heads); free(dirty); free(marked); free(outputs);
    return code;
}
