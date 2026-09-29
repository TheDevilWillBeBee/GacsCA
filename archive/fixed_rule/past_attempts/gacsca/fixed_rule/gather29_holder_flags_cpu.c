/* Explicit candidate-B packed physical four-flag projection on canonical geometry.
   A run stores repeated pairs of 64-bit physical F1/F2 words. Each output bit
   reads only its radius-five old neighborhood. Uniform word interiors can be
   evaluated once, but no assumed front speed or upper transition is used. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#define Q UINT64_C(16384)
#define U UINT64_C(536870912)
#define WF_START UINT64_C(114000000)
#define WF_END UINT64_C(114032768)
#define M (Q/64)
typedef struct {uint64_t end,f1,f2;} Run;
typedef struct {Run *a,*b;size_t used,capacity;uint8_t *s1,*s2;size_t colonies;uint64_t age,time,words,evaluations,literal,quiet;} World;
static int window(uint64_t age){return age>=WF_START&&age<WF_END;}
static uint64_t count2(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e){
 uint64_t s=a^b^c,k=(a&b)|(a&c)|(b&c),l=(s&d)|(s&e)|(d&e);return k|l;
}
static uint64_t count3(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e){
 uint64_t s=a^b^c,k=(a&b)|(a&c)|(b&c),l=(s&d)|(s&e)|(d&e);return (k&l)|((s^d^e)&(k|l));
}
static uint64_t count4(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e){
 uint64_t s=a^b^c,k=(a&b)|(a&c)|(b&c),l=(s&d)|(s&e)|(d&e);return k&l;
}
void fw_word(const uint64_t *in,uint64_t *out,int first,int last,int sig1,int sig2,int on){
 uint64_t f=in[2],g=in[3],rr[5],ll[5],inside[5];
 for(int j=1;j<=5;++j){rr[j-1]=(f>>j)|(in[4]<<(64-j));if(last)rr[j-1]&=UINT64_MAX>>j;
  ll[j-1]=(g<<j)|(in[1]>>(64-j));inside[j-1]=first?(ll[j-1]&(UINT64_MAX<<j)):ll[j-1];
}
 uint64_t nextf=count3(rr[0],rr[1],rr[2],rr[3],rr[4])|(f&count2(rr[0],rr[1],rr[2],rr[3],rr[4]));
 if(on&&last&&sig1)nextf|=UINT64_MAX<<56;
 uint64_t d4=0;
 if(on&&first&&sig2){uint64_t wf=(~f)&31;
  for(int p=0;p<8;++p){int lo=p>5?p-5:0;uint64_t mask=31&(~UINT64_C(0)<<lo);
   if(__builtin_popcountll(wf&mask)>=3)d4|=UINT64_C(1)<<p;}}
 uint64_t on2=count4(inside[0],inside[1],inside[2],inside[3],inside[4])|(nextf&count4(ll[0],ll[1],ll[2],ll[3],ll[4]))|d4;
 uint64_t erase=(~nextf&~count2(inside[0],inside[1],inside[2],inside[3],inside[4]))|(nextf&~(ll[0]|ll[1]|ll[2]|ll[3]|ll[4]));
 out[0]=nextf;out[1]=d4|(g&~erase)|(~g&on2);
}
void fw_free(World*w){if(!w)return;free(w->a);free(w->b);free(w->s1);free(w->s2);free(w);}
World *fw_create(const uint64_t *runs,size_t used,const uint8_t*s1,const uint8_t*s2,size_t colonies,uint64_t age){
 if(!used||!colonies||colonies>64||age>=U)return NULL;
 World*w=calloc(1,sizeof(World));if(!w)return NULL;w->capacity=used+32;w->used=used;w->colonies=colonies;w->age=age;w->words=colonies*M;
 w->a=malloc(w->capacity*sizeof(Run));w->b=malloc(w->capacity*sizeof(Run));w->s1=malloc(colonies);w->s2=malloc(colonies);
 if(!w->a||!w->b||!w->s1||!w->s2){fw_free(w);return NULL;}
 memcpy(w->a,runs,used*sizeof(Run));memcpy(w->s1,s1,colonies);memcpy(w->s2,s2,colonies);
 uint64_t previous=0;for(size_t i=0;i<used;++i){if(w->a[i].end<=previous||w->a[i].end>w->words){fw_free(w);return NULL;}previous=w->a[i].end;}
 if(previous!=w->words){fw_free(w);return NULL;}
 for(size_t c=0;c<colonies;++c)if(s1[c]>1||s2[c]>1){fw_free(w);return NULL;}
 return w;
}
static int reserve(World*w,size_t n){
 if(n<=w->capacity)return 0;
 size_t cap=w->capacity*2;if(cap<n)cap=n;
 Run *a=realloc(w->a,cap*sizeof(Run));if(!a)return -1;w->a=a;
 Run *b=realloc(w->b,cap*sizeof(Run));if(!b)return -1;w->b=b;w->capacity=cap;return 0;
}
static size_t at(World*w,uint64_t position,size_t*cursor){while(*cursor+1<w->used&&w->a[*cursor].end<=position)++*cursor;return *cursor;}
static int step(World*w,int*same){
 if(reserve(w,3*w->used+4*w->colonies+8))return -1;
 size_t left=0,center=0,right=0,n=0;uint64_t pos=0;
 while(pos<w->words){
  size_t c=at(w,pos,&center),l=pos?at(w,pos-1,&left):w->used-1,r=pos+1<w->words?at(w,pos+1,&right):0;
  uint64_t end=w->a[c].end,t=pos?w->a[l].end+1:1;if(t<end)end=t;
  t=pos+1<w->words?w->a[r].end-1:w->words;if(t<end)end=t;
  uint64_t offset=pos%M;t=offset==0||offset==M-1?pos+1:pos+M-1-offset;if(t<end)end=t;
  uint64_t input[6]={w->a[l].f1,w->a[l].f2,w->a[c].f1,w->a[c].f2,w->a[r].f1,w->a[r].f2},output[2];
  size_t colony=(size_t)(pos/M);fw_word(input,output,offset==0,offset==M-1,w->s1[colony],w->s2[colony],window(w->age));
  if(n&&w->b[n-1].f1==output[0]&&w->b[n-1].f2==output[1])w->b[n-1].end=end;
  else{w->b[n].end=end;w->b[n].f1=output[0];w->b[n].f2=output[1];++n;}
  ++w->evaluations;pos=end;
 }
 *same=n==w->used&&!memcmp(w->a,w->b,n*sizeof(Run));Run*swap=w->a;w->a=w->b;w->b=swap;w->used=n;++w->age;++w->time;++w->literal;return 0;
}
int fw_run(World*w,uint64_t ticks,int skip){
 if(!w||ticks>U-w->age)return -2;
 uint64_t stop=w->time+ticks;
 while(w->time<stop){int before=window(w->age),same=0;if(step(w,&same))return -1;
  if(skip&&same&&before==window(w->age)){
   uint64_t limit=w->age<WF_START?WF_START:(w->age<WF_END?WF_END:U),delta=limit-w->age;
   if(delta>stop-w->time)delta=stop-w->time;
   w->age+=delta;w->time+=delta;w->quiet+=delta;
  }
 }
 return 0;
}
size_t fw_size(World*w){return w->used;}
void fw_export(World*w,uint64_t*out){memcpy(out,w->a,w->used*sizeof(Run));}
void fw_info(World*w,uint64_t*out){out[0]=w->age%U;out[1]=w->time;out[2]=w->literal;out[3]=w->quiet;out[4]=w->evaluations;out[5]=w->used;}
