/* Exact physical CA representation on canonical healthy structure.
   The local clock is included in the described rule. This executor represents
   uniform Age, ballistic mail, and head travel through cells with no action.
   It never calls a simulated transition or evaluates the upper description. */
#include "clock_world_kernel.h"
#include <limits.h>

typedef struct { uint64_t due; size_t colony; int track; uint64_t value[4]; } Event;
typedef struct {
 uint64_t *cells,*outputs,*ghosts;
 size_t colonies,n,count,*active,*dirty,*seen;
 uint8_t *marked;
 Event *events;size_t used,cursor,capacity;
 uint64_t now,motion,literal,quiet,scans,evaluations,epoch;
} World;
static uint64_t age_now(World *w){return (w->epoch+w->now)%STRUCT_PERIOD;}
static int active_age(uint64_t a){return a<16*COLONY_CELLS || (a>=32*COLONY_CELLS&&a<48*COLONY_CELLS) || (a>=64*COLONY_CELLS&&a<80*COLONY_CELLS) || (a>=96*COLONY_CELLS&&a<104*COLONY_CELLS) || (a>=112*COLONY_CELLS&&a<120*COLONY_CELLS);}
static int reset_age(uint64_t a){return a==0||a==32*COLONY_CELLS||a==64*COLONY_CELLS||a==96*COLONY_CELLS||a==112*COLONY_CELLS;}
static int bulk_age(uint64_t a){return reset_age(a)||a==72*COLONY_CELLS||a==STRUCT_PERIOD-1;}
static uint64_t boundary_distance(uint64_t a){
 uint64_t points[]={0,16*COLONY_CELLS,32*COLONY_CELLS,48*COLONY_CELLS,64*COLONY_CELLS,72*COLONY_CELLS,80*COLONY_CELLS,96*COLONY_CELLS,98*COLONY_CELLS,104*COLONY_CELLS,112*COLONY_CELLS,120*COLONY_CELLS,STRUCT_PERIOD-1,STRUCT_PERIOD};
 uint64_t d=STRUCT_PERIOD-a;
 for(size_t i=0;i<sizeof(points)/sizeof(points[0]);++i)if(points[i]>a&&points[i]-a<d)d=points[i]-a;
 return d;
}
static uint64_t *ghost(World *w,size_t colony,int right){return w->ghosts+(2*colony+right)*P_FIELDS;}
static void clear_ghosts(World *w){
 memset(w->ghosts,0,2*w->colonies*P_FIELDS*sizeof(uint64_t));
 for(size_t c=0;c<w->colonies;++c){ghost(w,c,0)[P_ADDRESS]=COLONY_CELLS-1;ghost(w,c,1)[P_ADDRESS]=ROM_ROWS;}
}
void fw_free(World *w){if(!w)return;free(w->outputs);free(w->ghosts);free(w->active);free(w->dirty);free(w->seen);free(w->marked);free(w->events);free(w);}
World *fw_create(uint64_t *cells,size_t colonies){
 if(!colonies||colonies>SIZE_MAX/(ROM_ROWS*P_FIELDS*sizeof(uint64_t)))return NULL;
 World *w=calloc(1,sizeof(World));if(!w)return NULL;
 w->cells=cells;w->colonies=colonies;w->n=colonies*ROM_ROWS;w->epoch=cells[P_AGE];
 w->outputs=malloc(w->n*P_FIELDS*sizeof(uint64_t));w->ghosts=calloc(2*colonies*P_FIELDS,sizeof(uint64_t));
 w->active=malloc(w->n*sizeof(size_t));w->dirty=malloc(w->n*sizeof(size_t));w->seen=malloc(colonies*sizeof(size_t));w->marked=calloc(w->n,1);
 if(!w->outputs||!w->ghosts||!w->active||!w->dirty||!w->seen||!w->marked){fw_free(w);return NULL;}
 clear_ghosts(w);
 for(size_t p=0;p<w->n;++p){
  uint64_t *c=cells+p*P_FIELDS;
  if(c[P_ADDRESS]!=p%ROM_ROWS||c[P_AGE]!=w->epoch||c[P_F1]||c[P_F2]||c[P_WF1]||c[P_WF2]){fw_free(w);return NULL;}
  int active=0;for(int j=P_HEAD;j<P_ADDRESS;++j)active|=c[j]!=0;
  if(active)w->active[w->count++]=p;
 }
 return w;
}
static int enqueue(World *w,size_t colony,int track,const uint64_t *value){
 if(w->used==w->capacity){size_t cap=w->capacity?w->capacity*2:128;if(cap<w->capacity||cap>SIZE_MAX/sizeof(Event))return -1;
  Event *q=realloc(w->events,cap*sizeof(Event));if(!q)return -1;w->events=q;w->capacity=cap;}
 Event *e=w->events+w->used++;e->due=w->motion+(COLONY_CELLS-ROM_ROWS);e->colony=colony;e->track=track;memcpy(e->value,value,4*sizeof(uint64_t));return 0;
}
static void mark(World *w,size_t p,size_t *size){if(!w->marked[p]){w->marked[p]=1;w->dirty[(*size)++]=p;}}
static uint64_t limit_jump(World *w,uint64_t remaining,int active){
 uint64_t delta=boundary_distance(age_now(w));if(remaining<delta)delta=remaining;
 if(active&&w->cursor<w->used){uint64_t d=w->events[w->cursor].due-w->motion;if(d<delta)delta=d;}
 return delta;
}
static uint64_t quiet_jump(World *w,uint64_t limit){
 for(size_t i=0;i<w->count&&limit;++i){uint64_t *p=w->cells+w->active[i]*P_FIELDS,u[FIELDS];
  if(p[P_LP_VALID]||p[P_RP_VALID])return 0;
  lift_projected(p,u);if(!waiting(u))return 0;if(p[P_RD]<limit)limit=p[P_RD];}
 return limit;
}
static uint64_t scan_jump(World *w,uint64_t limit){
 if(!w->count||w->count>w->colonies)return 0;
 for(size_t c=0;c<w->colonies;++c)w->seen[c]=SIZE_MAX;
 for(size_t i=0;i<w->count&&limit;++i){
  size_t p=w->active[i],a=p%ROM_ROWS,colony=p/ROM_ROWS;uint64_t *c=w->cells+p*P_FIELDS;
  if(!c[P_HEAD]||c[P_LP_VALID]||c[P_RP_VALID]||w->seen[colony]!=SIZE_MAX)return 0;
  w->seen[colony]=p;uint64_t distance;
  if(c[P_DIRECTION])distance=a;
  else{
   uint64_t target=ROM_ROWS-1,x=UINT64_MAX;
   switch(c[P_PHASE]){
    case 0:if(c[P_PC]<PROGRAM_ROWS)x=MEMORY_ROWS+c[P_PC];break;
    case 1:case 4:case 5:if(c[P_RA]<MEMORY_ROWS)x=c[P_RA];break;
    case 2:if(c[P_RB]<MEMORY_ROWS)x=c[P_RB];break;
    case 3:if(c[P_RD]<MEMORY_ROWS)x=c[P_RD];break;
    case 6:if(c[P_VALUE]&&c[P_RD]<ROM_ROWS)x=c[P_RD];break;
   }
   if(x>=a&&x<target)target=x;
   distance=target-a;
  }
  if(distance<limit)limit=distance;
 }
 return limit;
}
static void move_heads(World *w,uint64_t distance){
 for(size_t i=0;i<w->count;++i){size_t p=w->active[i];uint64_t *c=w->cells+p*P_FIELDS;
  size_t q=c[P_DIRECTION]?p-distance:p+distance;uint64_t *d=w->cells+q*P_FIELDS;
  for(int field=P_HEAD;field<P_LP_TARGET;++field){d[field]=c[field];c[field]=0;}w->active[i]=q;
 }
}
int fw_run(World *w,uint64_t ticks,uint64_t *metrics,int shortcuts){
 if(!w||ticks>UINT64_MAX-w->now-(COLONY_CELLS-ROM_ROWS))return -2;
 uint64_t bl=w->literal,bq=w->quiet,bs=w->scans,be=w->evaluations,stop=w->now+ticks;
 while(w->now<stop){
  uint64_t age=age_now(w);int active=active_age(age),bulk=bulk_age(age),reset=reset_age(age);
  if(!bulk){
   uint64_t limit=limit_jump(w,stop-w->now,active),jump=0;
   if(shortcuts&1)jump=active?quiet_jump(w,limit):limit;
   if(jump){
    if(active){for(size_t i=0;i<w->count;++i)w->cells[w->active[i]*P_FIELDS+P_RD]-=jump;w->motion+=jump;}
    w->now+=jump;w->quiet+=jump;clear_ghosts(w);continue;
   }
   if(active&&(shortcuts&2)&&(jump=scan_jump(w,limit))){move_heads(w,jump);w->now+=jump;w->motion+=jump;w->scans+=jump;clear_ghosts(w);continue;}
  }
  size_t size=0;
  if(reset)w->cursor=w->used=0;
  while(active&&w->cursor<w->used&&w->events[w->cursor].due==w->motion){Event *e=w->events+w->cursor++;int right=e->track==P_LP_TARGET;
   memcpy(ghost(w,e->colony,right)+e->track,e->value,4*sizeof(uint64_t));mark(w,e->colony*ROM_ROWS+(right?ROM_ROWS-1:0),&size);}
  if(bulk){for(size_t p=0;p<w->n;++p)mark(w,p,&size);}
  else for(size_t i=0;i<w->count;++i){
   size_t p=w->active[i],a=p%ROM_ROWS;uint64_t *c=w->cells+p*P_FIELDS;
   int left=c[P_LP_VALID]||(c[P_HEAD]&&c[P_DIRECTION]&&a>0),right=c[P_RP_VALID];
   if(c[P_HEAD]&&!c[P_DIRECTION]&&a+1<ROM_ROWS){uint64_t u[FIELDS];lift_projected(c,u);right|=!waiting(u);}
   if(a&&left)mark(w,p-1,&size);
   mark(w,p,&size);
   if(a+1<ROM_ROWS&&right)mark(w,p+1,&size);
  }
  for(size_t i=0;i<size;++i){
   size_t p=w->dirty[i],a=p%ROM_ROWS,c=p/ROM_ROWS;uint64_t *center=w->cells+p*P_FIELDS;
   const uint64_t *left=a?center-P_FIELDS:ghost(w,c,0),*right=a+1<ROM_ROWS?center+P_FIELDS:ghost(w,c,1);
   const uint64_t *right2=a+2<ROM_ROWS?center+2*P_FIELDS:ghost(w,c,1);
   fp_local(left,center,right,right2,w->outputs+i*P_FIELDS,age);w->outputs[i*P_FIELDS+P_AGE]=w->epoch;
  }
  clear_ghosts(w);
  if(active&&!reset)for(size_t c=0;c<w->colonies;++c){
   uint64_t *first=w->cells+c*ROM_ROWS*P_FIELDS,*last=first+(ROM_ROWS-1)*P_FIELDS;
   if(first[P_LP_VALID]&&first[P_LP_REMAINING]>0){uint64_t packet[4]={first[P_LP_TARGET],first[P_LP_DATA],first[P_LP_REMAINING]-1,1};
    if(enqueue(w,c?c-1:w->colonies-1,P_LP_TARGET,packet))return -1;
    memcpy(ghost(w,c,0)+P_LP_TARGET,packet,sizeof(packet));}
   if(last[P_RP_VALID]){if(enqueue(w,c+1==w->colonies?0:c+1,P_RP_TARGET,last+P_RP_TARGET))return -1;
    memcpy(ghost(w,c,1)+P_RP_TARGET,last+P_RP_TARGET,4*sizeof(uint64_t));}
  }
  w->count=0;
  for(size_t i=0;i<size;++i){size_t p=w->dirty[i];uint64_t *o=w->outputs+i*P_FIELDS;memcpy(w->cells+p*P_FIELDS,o,P_FIELDS*sizeof(uint64_t));
   if(o[P_HEAD]||o[P_LP_VALID]||o[P_RP_VALID])w->active[w->count++]=p;
   w->marked[p]=0;}
  if(w->cursor==w->used)w->cursor=w->used=0;
  w->evaluations+=size;w->literal++;w->now++;w->motion+=active;
 }
 metrics[0]=ticks;metrics[1]=w->literal-bl;metrics[2]=w->quiet-bq;metrics[3]=w->scans-bs;metrics[4]=w->evaluations-be;return 0;
}
uint64_t fw_time(const World *w){return w->now;}
size_t fw_pending(const World *w){return w->used-w->cursor;}
int fw_cell(const World *w,size_t colony,uint64_t address,uint64_t *out){
 if(colony>=w->colonies||address>=COLONY_CELLS)return -1;
 if(address<ROM_ROWS){memcpy(out,w->cells+(colony*ROM_ROWS+address)*P_FIELDS,P_FIELDS*sizeof(uint64_t));out[P_AGE]=(w->epoch+w->now)%STRUCT_PERIOD;return 0;}
 memset(out,0,P_FIELDS*sizeof(uint64_t));out[P_ADDRESS]=address;out[P_AGE]=(w->epoch+w->now)%STRUCT_PERIOD;
 uint64_t distance=COLONY_CELLS-ROM_ROWS;
 for(size_t i=w->cursor;i<w->used;++i){const Event *e=w->events+i;uint64_t elapsed=w->motion-(e->due-distance);if(!elapsed||elapsed>distance)continue;
  size_t location=e->track==P_LP_TARGET?e->colony:(e->colony?e->colony-1:w->colonies-1);
  uint64_t a=e->track==P_LP_TARGET?COLONY_CELLS-elapsed:ROM_ROWS-1+elapsed;
  if(location==colony&&a==address)memcpy(out+e->track,e->value,4*sizeof(uint64_t));}
 return 0;
}
