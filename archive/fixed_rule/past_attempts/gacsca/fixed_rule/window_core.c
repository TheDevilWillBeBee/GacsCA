/* One fixed 370-bit radius-one rule, including all SEND and packet dynamics. */
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

enum { KIND, INDEX, A, B, D, BIT, HEAD, PHASE, PC, RA, RB, RD, VALUE,
       FIRST, LAST, DIRECTION, LP_TARGET, LP_BIT, LP_CROSS, LP_VALID,
       RP_TARGET, RP_BIT, RP_CROSS, RP_VALID, ADDRESS, FIELDS };
enum { MEM, GATE, LOOP, SEND, LOAD, CLEAR, META, WAIT };
enum { FETCH, READ_A, READ_B, WRITE, TRANSMIT, READ_LOAD, READ_META, WAIT_META };

static uint32_t static_bit(const uint32_t *c, uint32_t selector) {
    const int fields[] = {KIND, INDEX, A, B, D, FIRST, LAST};
    const uint32_t widths[] = {3, 32, 32, 32, 32, 1, 1};
    for (int j = 0; j < 7; ++j) {
        if (selector < widths[j]) return (c[fields[j]] >> selector) & 1;
        selector -= widths[j];
    }
    return 0;
}

static uint32_t fallback_bit(uint32_t address, uint32_t selector) {
    if (selector<3) return (LOOP >> selector) & 1;
    return selector >= 3 && selector < 35 ? (address >> (selector-3)) & 1 : 0;
}

static void reflect_left(const uint32_t *c, uint32_t *o) {
    for (int j = PHASE; j <= VALUE; ++j) o[j] = c[j];
    if (c[PHASE] == READ_META) {
        if (!c[VALUE]) o[VALUE] = 1;
        else {
            o[VALUE] = fallback_bit(c[RD], c[RB]); o[RD] = c[RA]; o[PHASE] = WRITE;
        }
    } else if (c[PHASE] == WAIT_META) o[PHASE] = WRITE;
}

#define COLONY_CELLS (UINT32_C(1) << 28)
static int waiting(const uint32_t *c) {
    return c[HEAD] && !c[DIRECTION] && c[PHASE]==FETCH && c[KIND]==WAIT &&
           c[INDEX]==c[PC] && c[RD]>0;
}

static void advance(const uint32_t *c, uint32_t *o) {
    for (int j = PHASE; j <= VALUE; ++j) o[j] = c[j];
    if (c[PHASE] == FETCH && c[INDEX] == c[PC]) {
        if (c[KIND] == GATE || c[KIND] == SEND) {
            o[PHASE] = c[KIND] == GATE ? READ_A : TRANSMIT;
            o[RA] = c[A]; o[RB] = c[B]; o[RD] = c[D];
        } else if (c[KIND] == LOOP) o[PC] = 0;
        else if (c[KIND] == LOAD) { o[PHASE] = READ_LOAD; o[RA] = c[A]; }
        else if (c[KIND] == CLEAR) { o[RD] = 0; o[PC] = (c[PC] + 1) & UINT32_MAX; }
        else if (c[KIND] == META) {
            o[PHASE] = READ_META; o[RA] = c[A]; o[RB] = c[B]; o[VALUE] = 0;
        } else if (c[KIND]==WAIT) {
            if (c[RD]) o[RD]=c[RD]-1;
            else o[PC]=c[PC]+1;
        }
    } else if (c[PHASE] == READ_META && c[VALUE] && c[ADDRESS] == c[RD]) {
        o[PHASE] = WAIT_META; o[VALUE] = static_bit(c, c[RB]); o[RD] = c[RA];
    } else if (c[KIND] == MEM) {
        if (c[PHASE] == READ_A && c[INDEX] == c[RA]) {
            o[VALUE] = c[BIT]; o[PHASE] = READ_B;
        } else if (c[PHASE] == READ_B && c[INDEX] == c[RB]) {
            o[VALUE] = 1 - (c[VALUE] & c[BIT]); o[PHASE] = WRITE;
        } else if (c[PHASE] == READ_LOAD && c[INDEX] == c[RA]) {
            o[RD] = ((c[RD] << 1) | c[BIT]) & UINT32_MAX;
            o[PHASE] = FETCH; o[PC] = (c[PC] + 1) & UINT32_MAX;
        } else if ((c[PHASE] == WRITE && c[INDEX] == c[RD]) ||
                   (c[PHASE] == TRANSMIT && c[INDEX] == c[RA])) {
            o[PC] = (c[PC] + 1) & UINT32_MAX; o[PHASE] = FETCH;
        }
    }
}

static void receive(const uint32_t *source, const uint32_t *c, uint32_t *o,
                    int track, uint32_t edge) {
    uint32_t valid = source[track+3] && !(source[track+2] && edge);
    uint32_t crossed = source[track+2] || edge;
    uint32_t hit = valid && crossed && c[KIND] == MEM && c[INDEX] == source[track];
    if (hit) o[BIT] = source[track+1];
    if (valid && !hit) {
        o[track] = source[track]; o[track+1] = source[track+1];
        o[track+2] = crossed; o[track+3] = 1;
    } else for (int j = 0; j < 4; ++j) o[track+j] = 0;
}

void fm_local(const uint32_t *l, const uint32_t *c, const uint32_t *r, uint32_t *o) {
    memcpy(o, c, FIELDS * sizeof(uint32_t));
    o[HEAD] = 0; o[DIRECTION] = 0;
    for (int j = PHASE; j <= VALUE; ++j) o[j] = 0;
    if (r[HEAD] && r[DIRECTION] && !r[FIRST]) {
        o[HEAD] = 1; o[DIRECTION] = 1;
        for (int j = PHASE; j <= VALUE; ++j) o[j] = r[j];
    }
    if (l[HEAD] && !l[DIRECTION] && !l[LAST] && !waiting(l)) {
        o[HEAD] = 1; o[DIRECTION] = 0; advance(l, o);
    }
    if (c[HEAD] && ((!c[DIRECTION] && c[LAST]) || (c[DIRECTION] && c[FIRST]))) {
        o[HEAD] = 1; o[DIRECTION] = !c[DIRECTION];
        if (!c[DIRECTION]) advance(c, o);
        else reflect_left(c, o);
    }
    if (waiting(c)) { o[HEAD]=1; o[DIRECTION]=0; advance(c,o); }
    receive(r, c, o, LP_TARGET, r[ADDRESS]==0);
    receive(l, c, o, RP_TARGET, l[ADDRESS]==COLONY_CELLS-1);
    if (c[HEAD] && !c[DIRECTION] && c[KIND] == MEM) {
        if (c[PHASE] == WRITE && c[INDEX] == c[RD]) o[BIT] = c[VALUE];
        if (c[PHASE] == TRANSMIT && c[INDEX] == c[RA]) {
            int track = c[RD] & 1 ? LP_TARGET : RP_TARGET;
            o[track] = c[RB]; o[track+1] = c[BIT]; o[track+2] = 0; o[track+3] = 1;
        }
    }
}

void fm_dense(const uint32_t *cells, uint32_t *out, size_t n) {
    for (size_t p = 0; p < n; ++p)
        fm_local(cells + ((p + n - 1) % n) * FIELDS, cells + p * FIELDS,
                 cells + ((p + 1) % n) * FIELDS, out + p * FIELDS);
}

/* A site is active if it has a head or a packet. Inactive canonical sites are
   fixed unless touched by an active nearest neighbor. Compute the union of
   those neighborhoods from OLD cells, then synchronously commit every result.
   This is an exact implementation of fm_local, not a simulated macrostep. */
int fm_run(uint32_t *cells, size_t n, uint64_t ticks, uint64_t *evaluations) {
    size_t *active = malloc(n * sizeof(size_t));
    size_t *dirty = malloc(n * sizeof(size_t));
    uint8_t *marked = calloc(n, sizeof(uint8_t));
    uint32_t *outputs = malloc(n * FIELDS * sizeof(uint32_t));
    int code = 0;
    size_t count = 0;
    *evaluations = 0;
    if (!active || !dirty || !marked || !outputs) { code = -1; goto done; }
    for (size_t p = 0; p < n; ++p) {
        const uint32_t *c = cells + p * FIELDS;
        if (c[HEAD] || c[LP_VALID] || c[RP_VALID]) active[count++] = p;
        /* Stale controller or packet bits also require one canonicalizing step.
           Track them as active rather than silently rejecting raw configurations. */
        else {
            int stale = c[DIRECTION];
            for (int j = PHASE; j <= VALUE; ++j) stale |= c[j] != 0;
            for (int j = LP_TARGET; j <= RP_VALID; ++j) stale |= c[j] != 0;
            if (stale) active[count++] = p;
        }
    }
    for (uint64_t tick = 0; tick < ticks; ++tick) {
        size_t size = 0;
        for (size_t i = 0; i < count; ++i) {
            size_t p = active[i];
            size_t positions[3] = {p ? p - 1 : n - 1, p, p + 1 == n ? 0 : p + 1};
            for (int j = 0; j < 3; ++j) {
                size_t q = positions[j];
                if (!marked[q]) { marked[q] = 1; dirty[size++] = q; }
            }
        }
        for (size_t i = 0; i < size; ++i) {
            size_t p = dirty[i], l = p ? p - 1 : n - 1, r = p + 1 == n ? 0 : p + 1;
            fm_local(cells + l * FIELDS, cells + p * FIELDS,
                     cells + r * FIELDS, outputs + i * FIELDS);
        }
        count = 0;
        for (size_t i = 0; i < size; ++i) {
            size_t p = dirty[i];
            const uint32_t *o = outputs + i * FIELDS;
            memcpy(cells + p * FIELDS, o, FIELDS * sizeof(uint32_t));
            if (o[HEAD] || o[LP_VALID] || o[RP_VALID]) active[count++] = p;
            marked[p] = 0;
        }
        *evaluations += size;
    }
 done:
    free(active); free(dirty); free(marked); free(outputs);
    return code;
}
