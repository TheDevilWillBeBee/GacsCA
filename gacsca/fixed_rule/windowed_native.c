/* Physical rule with program fields removed. The ROM is a compiled constant,
   not a runtime input or level-selected table. fm_local is the complete
   unprojected controller/packet transition; Address itself is preserved. */
#include "window_core.c"
#include "projection_rom.h"

enum { P_BIT, P_HEAD, P_PHASE, P_PC, P_RA, P_RB, P_RD, P_VALUE,
       P_DIRECTION, P_LP_TARGET, P_LP_BIT, P_LP_CROSS, P_LP_VALID,
       P_RP_TARGET, P_RP_BIT, P_RP_CROSS, P_RP_VALID, P_ADDRESS, P_FIELDS };
static const int dynamic_fields[P_FIELDS-1] = {
    BIT,HEAD,PHASE,PC,RA,RB,RD,VALUE,DIRECTION,LP_TARGET,LP_BIT,LP_CROSS,LP_VALID,
    RP_TARGET,RP_BIT,RP_CROSS,RP_VALID
};
static const int static_fields[7] = {KIND,INDEX,A,B,D,FIRST,LAST};

static void lift_projected(const uint32_t *p, uint32_t *u) {
    uint32_t address=p[P_ADDRESS];
    u[ADDRESS]=address;
    if (address<ROM_ROWS) {
        for (int j=0;j<7;++j) u[static_fields[j]]=PROJECTED_ROM[address][j];
    } else {
        for (int j=0;j<7;++j) u[static_fields[j]]=0;
        u[INDEX]=address; u[KIND]=LOOP;
    }
    for (int j=0;j<P_FIELDS-1;++j) u[dynamic_fields[j]]=p[j];
}

void fp_local(const uint32_t *l,const uint32_t *c,const uint32_t *r,uint32_t *o) {
    uint32_t ul[FIELDS],uc[FIELDS],ur[FIELDS],out[FIELDS];
    lift_projected(l,ul); lift_projected(c,uc); lift_projected(r,ur);
    fm_local(ul,uc,ur,out);
    for (int j=0;j<P_FIELDS-1;++j) o[j]=out[dynamic_fields[j]];
    o[P_ADDRESS]=out[ADDRESS];
}

void fp_dense(const uint32_t *cells,uint32_t *out,size_t n) {
    for (size_t p=0;p<n;++p)
        fp_local(cells+((p+n-1)%n)*P_FIELDS,cells+p*P_FIELDS,
                 cells+((p+1)%n)*P_FIELDS,out+p*P_FIELDS);
}

int fp_run(uint32_t *cells,size_t n,uint64_t ticks,uint64_t *evaluations) {
    size_t *active=malloc(n*sizeof(size_t)),*dirty=malloc(n*sizeof(size_t));
    uint8_t *marked=calloc(n,sizeof(uint8_t));
    uint32_t *outputs=malloc(n*P_FIELDS*sizeof(uint32_t));
    int code=0;
    size_t count=0;
    *evaluations=0;
    if (!active||!dirty||!marked||!outputs) { code=-1; goto done; }
    for (size_t p=0;p<n;++p) {
        const uint32_t *c=cells+p*P_FIELDS;
        int live=0;
        for (int j=P_HEAD;j<P_ADDRESS;++j) live|=c[j]!=0;
        if (live) active[count++]=p;
    }
    for (uint64_t tick=0;tick<ticks;++tick) {
        size_t size=0;
        for (size_t i=0;i<count;++i) {
            size_t p=active[i],positions[3]={p?p-1:n-1,p,p+1==n?0:p+1};
            for (int j=0;j<3;++j) {
                size_t q=positions[j];
                if (!marked[q]) { marked[q]=1; dirty[size++]=q; }
            }
        }
        for (size_t i=0;i<size;++i) {
            size_t p=dirty[i],l=p?p-1:n-1,r=p+1==n?0:p+1;
            fp_local(cells+l*P_FIELDS,cells+p*P_FIELDS,cells+r*P_FIELDS,outputs+i*P_FIELDS);
        }
        count=0;
        for (size_t i=0;i<size;++i) {
            size_t p=dirty[i];
            const uint32_t *o=outputs+i*P_FIELDS;
            memcpy(cells+p*P_FIELDS,o,P_FIELDS*sizeof(uint32_t));
            if (o[P_HEAD]||o[P_LP_VALID]||o[P_RP_VALID]) active[count++]=p;
            marked[p]=0;
        }
        *evaluations+=size;
    }
 done:
    free(active); free(dirty); free(marked); free(outputs);
    return code;
}
