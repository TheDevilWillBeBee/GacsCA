/* Exact physical prefix through capture, stopping before the Wf window.
   Stored core + five tail buffers; the intervening zero-workspace gap carries
   ballistic packets. No upper transition or expression evaluator is called. */
#include "repair_b_prefix_kernel.h"
#include <limits.h>
typedef struct {uint64_t due;size_t colony;int track;uint64_t value[4];} Event;
typedef struct {
 uint64_t *cells,*outputs;size_t colonies,n,count,*active,*dirty,*seen;uint8_t *marked;
 uint64_t *ghosts;Event *events;size_t used,cursor,capacity;
 uint64_t now,motion,literal,quiet,scans,evaluations,epoch;int sig_dirty;
} World;
#define ROWS (ROM_ROWS+5)
#define GAP (COLONY_CELLS-ROWS)
static uint64_t age_now(World*w){return w->epoch+w->now;}
static uint64_t address_of(size_t a){return a<ROM_ROWS?a:COLONY_CELLS-5+a-ROM_ROWS;}
static size_t stored(World*w,size_t colony,int64_t address){
 if(address<0){address+=COLONY_CELLS;colony=colony?colony-1:w->colonies-1;}
 if(address>=(int64_t)COLONY_CELLS){address-=COLONY_CELLS;colony=colony+1==w->colonies?0:colony+1;}
 if(address<ROM_ROWS)return colony*ROWS+(size_t)address;
 if(address>=(int64_t)COLONY_CELLS-5)return colony*ROWS+ROM_ROWS+(size_t)(address-(COLONY_CELLS-5));
 return SIZE_MAX;
}
static int active_age(uint64_t a){return a<16*COLONY_CELLS||(a>=32*COLONY_CELLS&&a<48*COLONY_CELLS)||(a>=64*COLONY_CELLS&&a<80*COLONY_CELLS);}
static int reset_age(uint64_t a){return a==0||a==32*COLONY_CELLS||a==64*COLONY_CELLS;}
static int bulk_age(uint64_t a){return reset_age(a)||a==70*COLONY_CELLS||a==79*COLONY_CELLS-1;}
static uint64_t boundary_distance(uint64_t a){
 uint64_t points[]={0,16*COLONY_CELLS,32*COLONY_CELLS,48*COLONY_CELLS,64*COLONY_CELLS,70*COLONY_CELLS,79*COLONY_CELLS-1,79*COLONY_CELLS,80*COLONY_CELLS,96*COLONY_CELLS-1};
 uint64_t d=96*COLONY_CELLS-1-a;
 for(size_t i=0;i<sizeof(points)/sizeof(points[0]);++i)if(points[i]>a&&points[i]-a<d)d=points[i]-a;
 return d;
}
static uint64_t *ghost(World*w,size_t colony,int at_tail){return w->ghosts+(2*colony+at_tail)*P_FIELDS;}
static void clear_ghosts(World*w){memset(w->ghosts,0,2*w->colonies*P_FIELDS*sizeof(uint64_t));}
static void read_cell(World*w,size_t colony,int64_t address,uint64_t*out){
 if(address<0){address+=COLONY_CELLS;colony=colony?colony-1:w->colonies-1;}
 if(address>=(int64_t)COLONY_CELLS){address-=COLONY_CELLS;colony=colony+1==w->colonies?0:colony+1;}
 size_t p=stored(w,colony,address);
 if(p!=SIZE_MAX)memcpy(out,w->cells+p*P_FIELDS,P_FIELDS*sizeof(uint64_t));
 else if(address==ROM_ROWS)memcpy(out,ghost(w,colony,0),P_FIELDS*sizeof(uint64_t));
 else if(address==(int64_t)COLONY_CELLS-6)memcpy(out,ghost(w,colony,1),P_FIELDS*sizeof(uint64_t));
 else memset(out,0,P_FIELDS*sizeof(uint64_t));
 out[P_ADDRESS]=(uint64_t)address;out[P_AGE]=age_now(w);
}
static void neighborhood(World*w,size_t p,uint64_t*input){
 size_t colony=p/ROWS;int64_t a=(int64_t)address_of(p%ROWS);uint64_t record[P_FIELDS];
 for(int j=-5;j<=5;++j){read_cell(w,colony,a+j,record);lift_projected(record,input+(j+5)*FIELDS);}
}
void fw_free(World*w){if(!w)return;free(w->outputs);free(w->ghosts);free(w->active);free(w->dirty);free(w->seen);free(w->marked);free(w->events);free(w);}
World *fw_create(uint64_t*cells,size_t colonies){
 if(!colonies||colonies>SIZE_MAX/(ROWS*P_FIELDS*sizeof(uint64_t)))return NULL;
 World*w=calloc(1,sizeof(World));if(!w)return NULL;
 w->cells=cells;w->colonies=colonies;w->n=colonies*ROWS;w->epoch=cells[P_AGE];
 if(w->epoch>=96*COLONY_CELLS){free(w);return NULL;}
 w->outputs=malloc(w->n*P_FIELDS*sizeof(uint64_t));w->ghosts=calloc(2*colonies*P_FIELDS,sizeof(uint64_t));
 w->active=malloc(w->n*sizeof(size_t));w->dirty=malloc(w->n*sizeof(size_t));w->seen=malloc(colonies*sizeof(size_t));w->marked=calloc(w->n,1);
 if(!w->outputs||!w->ghosts||!w->active||!w->dirty||!w->seen||!w->marked){fw_free(w);return NULL;}
 for(size_t p=0;p<w->n;++p){uint64_t*c=cells+p*P_FIELDS;
  size_t colony=p/ROWS,a=p%ROWS;
  uint64_t left=(cells[(colony*ROWS+3)*P_FIELDS+P_SIGNAL]>>2)&1;
  uint64_t right=(cells[(colony*ROWS+ROM_ROWS+2)*P_FIELDS+P_SIGNAL]>>2)&1;
  uint64_t signal=a>=1&&a<=5?left<<(5-a):(a>=ROM_ROWS?right<<(4-(a-ROM_ROWS)):0);
  if(c[P_ADDRESS]!=address_of(p%ROWS)||c[P_AGE]!=w->epoch||c[P_F1]||c[P_F2]||c[P_WF1]||c[P_WF2]||c[P_SIGNAL]!=signal||(p%ROWS>=ROM_ROWS&&c[P_HEAD])){fw_free(w);return NULL;}
  int active=0;for(int j=P_HEAD;j<P_ADDRESS;++j)active|=c[j]!=0;
  if(active)w->active[w->count++]=p;
 }
 return w;
}
static int enqueue(World*w,size_t colony,int track,const uint64_t*value){
 if(w->used==w->capacity){size_t cap=w->capacity?w->capacity*2:128;Event*q=realloc(w->events,cap*sizeof(Event));if(!q)return -1;w->events=q;w->capacity=cap;}
 Event*e=w->events+w->used++;e->due=w->motion+GAP;e->colony=colony;e->track=track;memcpy(e->value,value,4*sizeof(uint64_t));return 0;
}
static void mark(World*w,size_t p,size_t*size){if(p!=SIZE_MAX&&!w->marked[p]){w->marked[p]=1;w->dirty[(*size)++]=p;}}
static uint64_t limit_jump(World*w,uint64_t remaining,int active){
 uint64_t delta=boundary_distance(age_now(w));if(remaining<delta)delta=remaining;
 if(active&&w->cursor<w->used){uint64_t d=w->events[w->cursor].due-w->motion;if(d<delta)delta=d;}
 return delta;
}
static int signals_fixed(World*w){
 for(size_t p=0;p<w->n;++p){uint64_t current=w->cells[p*P_FIELDS+P_SIGNAL];
  /* Only the five boundary holders carry the admitted coherent old/captured signal. */
  size_t a=p%ROWS;if(a>5&&a<ROM_ROWS)continue;
  uint64_t value=0,record[P_FIELDS];
  for(int d=-2;d<=2;++d){int votes=0;
   for(int e=-2;e<=2;++e){read_cell(w,p/ROWS,(int64_t)address_of(a)+d+e,record);votes+=(int)((record[P_SIGNAL]>>(2-e))&1);}
   value|=(uint64_t)(votes>=3)<<(d+2);
  }
  if(current!=value)return 0;
 }
 return 1;
}
static uint64_t quiet_jump(World*w,uint64_t limit){
 if(w->sig_dirty)return 0;
 for(size_t i=0;i<w->count&&limit;++i){uint64_t*p=w->cells+w->active[i]*P_FIELDS,u[FIELDS];
  if(p[P_LP_VALID]||p[P_RP_VALID])return 0;
  lift_projected(p,u);if(!waiting(u))return 0;if(p[P_RD]<limit)limit=p[P_RD];}
 return limit;
}
static uint64_t scan_jump(World*w,uint64_t limit){
 if(w->sig_dirty||!w->count||w->count>w->colonies)return 0;
 for(size_t c=0;c<w->colonies;++c)w->seen[c]=SIZE_MAX;
 for(size_t i=0;i<w->count&&limit;++i){size_t p=w->active[i],a=p%ROWS,colony=p/ROWS;uint64_t*c=w->cells+p*P_FIELDS;
  if(!c[P_HEAD]||c[P_LP_VALID]||c[P_RP_VALID]||a>=ROM_ROWS||w->seen[colony]!=SIZE_MAX)return 0;
  w->seen[colony]=p;uint64_t distance;
  if(c[P_DIRECTION])distance=a;
  else{uint64_t target=ROM_ROWS-1,x=UINT64_MAX;
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
static void move_heads(World*w,uint64_t distance){
 for(size_t i=0;i<w->count;++i){size_t p=w->active[i];uint64_t*c=w->cells+p*P_FIELDS;size_t q=c[P_DIRECTION]?p-distance:p+distance;uint64_t*d=w->cells+q*P_FIELDS;
  for(int field=P_HEAD;field<P_LP_TARGET;++field){d[field]=c[field];c[field]=0;}w->active[i]=q;}
}
int fw_run(World*w,uint64_t ticks,uint64_t*metrics,int shortcuts){
 if(!w||age_now(w)>96*COLONY_CELLS-1||ticks>96*COLONY_CELLS-1-age_now(w))return -2;
 uint64_t bl=w->literal,bq=w->quiet,bs=w->scans,be=w->evaluations,stop=w->now+ticks;
 while(w->now<stop){uint64_t age=age_now(w);int active=active_age(age),bulk=bulk_age(age),reset=reset_age(age);
  if(w->sig_dirty&&signals_fixed(w))w->sig_dirty=0;
  if(!bulk){uint64_t limit=limit_jump(w,stop-w->now,active),jump=0;
   if(shortcuts&1)jump=active?quiet_jump(w,limit):(w->sig_dirty?0:limit);
   if(jump){if(active){for(size_t i=0;i<w->count;++i)w->cells[w->active[i]*P_FIELDS+P_RD]-=jump;w->motion+=jump;}
    w->now+=jump;w->quiet+=jump;clear_ghosts(w);continue;}
   if(active&&(shortcuts&2)&&(jump=scan_jump(w,limit))){move_heads(w,jump);w->now+=jump;w->motion+=jump;w->scans+=jump;clear_ghosts(w);continue;}
  }
  size_t size=0;
  if(reset)w->cursor=w->used=0;
  while(active&&w->cursor<w->used&&w->events[w->cursor].due==w->motion){Event*e=w->events+w->cursor++;int tail=e->track==P_RP_TARGET;
   memcpy(ghost(w,e->colony,tail)+e->track,e->value,4*sizeof(uint64_t));mark(w,e->colony*ROWS+(tail?ROM_ROWS:ROM_ROWS-1),&size);}
  if(bulk){for(size_t p=0;p<w->n;++p)mark(w,p,&size);}
  else{
   for(size_t i=0;i<w->count;++i){size_t p=w->active[i],colony=p/ROWS;int64_t a=(int64_t)address_of(p%ROWS);uint64_t*c=w->cells+p*P_FIELDS;
    mark(w,p,&size);
    if(c[P_LP_VALID]||(c[P_HEAD]&&c[P_DIRECTION]))mark(w,stored(w,colony,a-1),&size);
    if(c[P_RP_VALID]||(c[P_HEAD]&&!c[P_DIRECTION]))mark(w,stored(w,colony,a+1),&size);
   }
   if(w->sig_dirty)for(size_t p=0;p<w->n;++p)if(w->cells[p*P_FIELDS+P_SIGNAL])for(int j=-4;j<=4;++j)mark(w,stored(w,p/ROWS,(int64_t)address_of(p%ROWS)+j),&size);
  }
  for(size_t i=0;i<size;++i){uint64_t input[11*FIELDS],out[FIELDS];neighborhood(w,w->dirty[i],input);ww_prefix_local(input,out);
   for(int j=0;j<P_FIELDS;++j)w->outputs[i*P_FIELDS+j]=out[dynamic_fields[j]];
   w->outputs[i*P_FIELDS+P_AGE]=w->epoch;
  }
  clear_ghosts(w);
  if(active&&!reset)for(size_t c=0;c<w->colonies;++c){uint64_t*last=w->cells+(c*ROWS+ROM_ROWS-1)*P_FIELDS,*tail=last+P_FIELDS;
   if(tail[P_LP_VALID]){if(enqueue(w,c,P_LP_TARGET,tail+P_LP_TARGET))return -1;}
   if(last[P_RP_VALID]){if(enqueue(w,c,P_RP_TARGET,last+P_RP_TARGET))return -1;}
  }
  w->count=0;
  for(size_t i=0;i<size;++i){size_t p=w->dirty[i];uint64_t*o=w->outputs+i*P_FIELDS;memcpy(w->cells+p*P_FIELDS,o,P_FIELDS*sizeof(uint64_t));
   if(o[P_HEAD]||o[P_LP_VALID]||o[P_RP_VALID])w->active[w->count++]=p;
   w->marked[p]=0;
  }
  if(age==79*COLONY_CELLS-1)w->sig_dirty=1;
  if(w->cursor==w->used)w->cursor=w->used=0;
  w->evaluations+=size;w->literal++;w->now++;w->motion+=active;
 }
 metrics[0]=ticks;metrics[1]=w->literal-bl;metrics[2]=w->quiet-bq;metrics[3]=w->scans-bs;metrics[4]=w->evaluations-be;return 0;
}
uint64_t fw_time(const World*w){return w->now;}
size_t fw_pending(const World*w){return w->used-w->cursor;}
int fw_cell(World*w,size_t colony,uint64_t address,uint64_t*out){
 if(colony>=w->colonies||address>=COLONY_CELLS)return -1;
 read_cell(w,colony,(int64_t)address,out);
 if(stored(w,colony,(int64_t)address)!=SIZE_MAX)return 0;
 for(size_t i=w->cursor;i<w->used;++i){Event*e=w->events+i;uint64_t elapsed=w->motion-(e->due-GAP);if(!elapsed||elapsed>GAP||e->colony!=colony)continue;
  uint64_t a=e->track==P_LP_TARGET?COLONY_CELLS-5-elapsed:ROM_ROWS-1+elapsed;
  if(a==address)memcpy(out+e->track,e->value,4*sizeof(uint64_t));}
 return 0;
}
