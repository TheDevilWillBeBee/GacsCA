/* Exact representation of the fixed windowed CA on a finite colony ring.
   Explicit cores use fp_local. Headless LOOP padding transports the two packet
   tracks independently at speed one, without deposits. Events encode those
   physical world-lines, NOT simulated-cell transitions. */
#include "windowed_native.c"
#include <limits.h>

typedef struct { uint64_t due; size_t colony; int track; uint32_t value[4]; } Event;
typedef struct {
    uint32_t *cells,*outputs,*ghosts;
    size_t colonies,n,count,*active,*dirty;
    uint8_t *marked;
    Event *events; size_t used,cursor,capacity;
    uint64_t now,literal,skipped,evaluations;
} World;

static uint32_t *ghost(World *w,size_t colony,int right) {
    return w->ghosts+(2*colony+right)*P_FIELDS;
}
static void clear_ghosts(World *w) {
    memset(w->ghosts,0,2*w->colonies*P_FIELDS*sizeof(uint32_t));
    for (size_t c=0;c<w->colonies;++c) {
        ghost(w,c,0)[P_ADDRESS]=COLONY_CELLS-1;
        ghost(w,c,1)[P_ADDRESS]=ROM_ROWS;
    }
}
void fw_free(World *w) {
    if (!w) return;
    free(w->outputs);free(w->ghosts);free(w->active);free(w->dirty);
    free(w->marked);free(w->events);free(w);
}
World *fw_create(uint32_t *cells,size_t colonies) {
    if (!colonies || colonies>SIZE_MAX/(ROM_ROWS*P_FIELDS*sizeof(uint32_t))) return NULL;
    World *w=calloc(1,sizeof(World)); if (!w) return NULL;
    w->cells=cells;w->colonies=colonies;w->n=colonies*ROM_ROWS;
    w->outputs=malloc(w->n*P_FIELDS*sizeof(uint32_t));
    w->ghosts=calloc(2*colonies*P_FIELDS,sizeof(uint32_t));
    w->active=malloc(w->n*sizeof(size_t));w->dirty=malloc(w->n*sizeof(size_t));
    w->marked=calloc(w->n,1);
    if (!w->outputs||!w->ghosts||!w->active||!w->dirty||!w->marked) { fw_free(w);return NULL; }
    clear_ghosts(w);
    for (size_t p=0;p<w->n;++p) {
        uint32_t *c=cells+p*P_FIELDS;
        if (c[P_ADDRESS]!=p%ROM_ROWS) { fw_free(w);return NULL; }
        int active=0;
        for (int j=P_HEAD;j<P_ADDRESS;++j) active|=c[j]!=0;
        if (active) w->active[w->count++]=p;
    }
    return w;
}
static int enqueue(World *w,size_t colony,int track,const uint32_t *value) {
    if (w->used==w->capacity) {
        size_t cap=w->capacity?w->capacity*2:128;
        if (cap<w->capacity||cap>SIZE_MAX/sizeof(Event)) return -1;
        Event *q=realloc(w->events,cap*sizeof(Event));if (!q) return -1;
        w->events=q;w->capacity=cap;
    }
    Event *e=w->events+w->used++;
    e->due=w->now+(COLONY_CELLS-ROM_ROWS);e->colony=colony;e->track=track;
    memcpy(e->value,value,4*sizeof(uint32_t));
    return 0;
}
static void mark(World *w,size_t p,size_t *size) {
    if (!w->marked[p]) { w->marked[p]=1;w->dirty[(*size)++]=p; }
}
static uint64_t skippable(World *w,uint64_t remaining) {
    uint64_t delta=remaining;
    if (w->cursor<w->used) {
        uint64_t distance=w->events[w->cursor].due-w->now;
        if (distance<delta) delta=distance;
    }
    for (size_t i=0;i<w->count && delta;++i) {
        uint32_t *p=w->cells+w->active[i]*P_FIELDS,u[FIELDS];
        if (p[P_LP_VALID]||p[P_RP_VALID]) return 0;
        lift_projected(p,u);
        if (!waiting(u)) return 0;
        if (p[P_RD]<delta) delta=p[P_RD];
    }
    return delta;
}
int fw_run(World *w,uint64_t ticks,uint64_t *metrics,int permit_wait_skip) {
    if (!w || ticks>UINT64_MAX-w->now-(COLONY_CELLS-ROM_ROWS)) return -2;
    uint64_t before_l=w->literal,before_s=w->skipped,before_e=w->evaluations;
    uint64_t stop=w->now+ticks;
    while (w->now<stop) {
        uint64_t jump=permit_wait_skip?skippable(w,stop-w->now):0;
        if (jump) {
            for (size_t i=0;i<w->count;++i) w->cells[w->active[i]*P_FIELDS+P_RD]-=(uint32_t)jump;
            w->now+=jump;w->skipped+=jump;clear_ghosts(w);continue;
        }
        size_t size=0;
        while (w->cursor<w->used && w->events[w->cursor].due==w->now) {
            Event *e=w->events+w->cursor++;
            int right=e->track==P_LP_TARGET;
            memcpy(ghost(w,e->colony,right)+e->track,e->value,4*sizeof(uint32_t));
            mark(w,e->colony*ROM_ROWS+(right?ROM_ROWS-1:0),&size);
        }
        for (size_t i=0;i<w->count;++i) {
            size_t p=w->active[i],a=p%ROM_ROWS;
            uint32_t *c=w->cells+p*P_FIELDS;
            /* Dependency support of fp_local: a head travels only in its
               direction; each packet has its own directed track. Self remains
               necessary for writes, reflection and stale-field clearing. */
            int left=c[P_LP_VALID] || (c[P_HEAD] && c[P_DIRECTION] && a>0);
            int right=c[P_RP_VALID];
            if (c[P_HEAD] && !c[P_DIRECTION] && a+1<ROM_ROWS) {
                uint32_t u[FIELDS];lift_projected(c,u);
                right|=!waiting(u);
            }
            if (a && left) mark(w,p-1,&size);
            mark(w,p,&size);
            if (a+1<ROM_ROWS && right) mark(w,p+1,&size);
        }
        for (size_t i=0;i<size;++i) {
            size_t p=w->dirty[i],a=p%ROM_ROWS,c=p/ROM_ROWS;
            uint32_t *center=w->cells+p*P_FIELDS;
            const uint32_t *left=a?center-P_FIELDS:ghost(w,c,0);
            const uint32_t *right=a+1<ROM_ROWS?center+P_FIELDS:ghost(w,c,1);
            fp_local(left,center,right,w->outputs+i*P_FIELDS);
        }
        /* Preserve the exact first padding step as the next ghost. Events then
           provide the far ghost after the remaining ballistic traversal. */
        clear_ghosts(w);
        for (size_t c=0;c<w->colonies;++c) {
            uint32_t *first=w->cells+c*ROM_ROWS*P_FIELDS;
            uint32_t *last=first+(ROM_ROWS-1)*P_FIELDS;
            if (first[P_LP_VALID] && !first[P_LP_CROSS]) {
                uint32_t packet[4]={first[P_LP_TARGET],first[P_LP_BIT],1,1};
                if (enqueue(w,c?c-1:w->colonies-1,P_LP_TARGET,packet)) return -1;
                memcpy(ghost(w,c,0)+P_LP_TARGET,packet,sizeof(packet));
            }
            if (last[P_RP_VALID]) {
                if (enqueue(w,c+1==w->colonies?0:c+1,P_RP_TARGET,last+P_RP_TARGET)) return -1;
                memcpy(ghost(w,c,1)+P_RP_TARGET,last+P_RP_TARGET,4*sizeof(uint32_t));
            }
        }
        w->count=0;
        for (size_t i=0;i<size;++i) {
            size_t p=w->dirty[i];uint32_t *o=w->outputs+i*P_FIELDS;
            memcpy(w->cells+p*P_FIELDS,o,P_FIELDS*sizeof(uint32_t));
            if (o[P_HEAD]||o[P_LP_VALID]||o[P_RP_VALID]) w->active[w->count++]=p;
            w->marked[p]=0;
        }
        if (w->cursor==w->used) w->cursor=w->used=0;
        w->evaluations+=size;w->literal++;w->now++;
    }
    metrics[0]=ticks;metrics[1]=w->literal-before_l;metrics[2]=w->skipped-before_s;metrics[3]=w->evaluations-before_e;
    return 0;
}
uint64_t fw_time(const World *w) { return w->now; }
size_t fw_pending(const World *w) { return w->used-w->cursor; }
int fw_cell(const World *w,size_t colony,uint32_t address,uint32_t *out) {
    if (colony>=w->colonies || address>=COLONY_CELLS) return -1;
    if (address<ROM_ROWS) { memcpy(out,w->cells+(colony*ROM_ROWS+address)*P_FIELDS,P_FIELDS*sizeof(uint32_t));return 0; }
    memset(out,0,P_FIELDS*sizeof(uint32_t));out[P_ADDRESS]=address;
    uint64_t distance=COLONY_CELLS-ROM_ROWS;
    for (size_t i=w->cursor;i<w->used;++i) {
        const Event *e=w->events+i;
        uint64_t elapsed=w->now-(e->due-distance);
        if (!elapsed||elapsed>distance) continue;
        size_t location=e->track==P_LP_TARGET?e->colony:(e->colony?e->colony-1:w->colonies-1);
        uint32_t a=e->track==P_LP_TARGET?COLONY_CELLS-elapsed:ROM_ROWS-1+elapsed;
        if (location==colony && a==address) memcpy(out+e->track,e->value,4*sizeof(uint32_t));
    }
    return 0;
}
