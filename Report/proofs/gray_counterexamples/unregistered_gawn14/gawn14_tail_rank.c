/* Exact finite right-end native tail of unchanged GAWN2, not a new rule.
 * The separately written proof supplies closure and the two-label reduction.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "../unregistered_gawn10/gawn10_two_offset_projection.c"

typedef struct {
 uint32_t states,max_rank,maximizer,nonzero_cycles,cycle_state,cycle_length;
 uint64_t native_comparisons;
} TailResult;

static uint32_t tail_next(uint32_t state,unsigned delta){
 const uint32_t mask=(1u<<delta)-1u,g=state&mask,f=state>>delta;
 uint32_t ng=0,nf=0;
 for(unsigned p=0;p<delta;p++){
  const unsigned k=p<5?p:5,first=p-k;
  const unsigned lc=__builtin_popcount((g>>first)&((1u<<k)-1u));
  const unsigned rc=__builtin_popcount((g>>(p+1))&31u);
  const unsigned rf=__builtin_popcount((f>>(p+1))&31u);
  const int left=lc>=3,right=rc>=3;
  const int mismatch=right?(k-lc>=3):(lc>=3);
  const int flag=mismatch||rf>=3||(((f>>p)&1u)&&rf>=2);
  nf|=(uint32_t)flag<<p;ng|=(uint32_t)(flag?left:right)<<p;
 }
 return ng|(nf<<delta);
}

/* Compare a whole tail with the separately frozen native C transition.
 * Arbitrary left Flag1 bits are included; they cannot enter a right quorum.
 */
static int compare_native(uint32_t state,unsigned delta,uint32_t expected,
                          uint64_t *comparisons){
 const uint32_t mask=(1u<<delta)-1u,g=state&mask,f=state>>delta;
 uint32_t actual=0;
 for(unsigned p=0;p<delta;p++){
  Site row[17];memset(row,0,sizeof(row));
  for(int j=-8;j<=8;j++){
   const int t=(int)p+j;
   if(t>=0&&t<(int)delta){row[j+8].foreign=(g>>t)&1u;row[j+8].f1=(f>>t)&1u;}
   else if(t<0)row[j+8].f1=((state+(uint32_t)(-t)*13u)>>((-t)%13))&1u;
  }
  const Site out=transition(row,8,Q-(int)delta+(int)p,(int)delta);
  if(out.f2||out.wf1||out.wf2)return -1;
  actual|=(uint32_t)out.foreign<<p;actual|=(uint32_t)out.f1<<(delta+p);
  (*comparisons)++;
 }
 return actual==expected?0:-2;
}

int gawn14_tail_graph(unsigned delta,uint32_t *next,uint16_t *rank,TailResult *r){
 if(delta<1||delta>12||!next||!rank||!r)return -1;
 const uint32_t n=1u<<(2*delta);memset(r,0,sizeof(*r));r->states=n;
 memset(rank,255,n*sizeof(*rank));rank[0]=0;
 for(uint32_t s=0;s<n;s++){
  next[s]=tail_next(s,delta);
  /* Exhaustive native comparison through delta8, deterministic larger sample. */
  if(delta<=8||s<128||s+128>=n||s%4093==0){
   const int err=compare_native(s,delta,next[s],&r->native_comparisons);
   if(err)return -10+err;
  }
 }
 if(next[0]!=0)return -2;
 uint8_t *color=calloc(n,sizeof(*color));uint32_t *stack=malloc(n*sizeof(*stack));
 if(!color||!stack){free(color);free(stack);return -3;}color[0]=2;
 for(uint32_t s=1;s<n;s++)if(!color[s]){
  uint32_t v=s,len=0;
  while(!color[v]){color[v]=1;stack[len++]=v;v=next[v];}
  if(color[v]==1){
   r->nonzero_cycles=1;r->cycle_state=v;r->cycle_length=1;
   for(uint32_t t=next[v];t!=v;t=next[t])r->cycle_length++;
   free(color);free(stack);return 1;
  }
  uint32_t distance=rank[v];
  while(len){v=stack[--len];distance++;if(distance>=65535){free(color);free(stack);return -4;}
   rank[v]=(uint16_t)distance;color[v]=2;
   if(distance>r->max_rank){r->max_rank=distance;r->maximizer=v;}
  }
 }
 for(uint32_t s=1;s<n;s++)if(!rank[s]||rank[s]!=rank[next[s]]+1){free(color);free(stack);return -5;}
 free(color);free(stack);return 0;
}

/* Independent point interface for Python's literal formula and pulse probes. */
uint32_t gawn14_point(uint32_t state,unsigned delta){
 if(delta<1||delta>12||state>=(1u<<(2*delta)))return UINT32_MAX;
 return tail_next(state,delta);
}
