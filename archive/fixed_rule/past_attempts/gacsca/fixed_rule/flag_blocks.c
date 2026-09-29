/* Exact RLE of arbitrary nine-word flag blocks, including partial ring tail.
   This changes storage only. Physical bits still use fw_word's radius-five rule. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define Q UINT64_C(8388608)
#define U (128*Q)
#define M (Q/64)
#define B 9
#include "flag_word_kernel.h"
typedef struct {uint64_t end,f1[B],f2[B];} Run;
typedef struct {Run *a,*b;size_t used,capacity;uint8_t*s1,*s2;size_t colonies;uint64_t age,time,words,blocks,evaluations,literal,quiet,*critical;size_t nc;} World;
void fb_free(World*w){if(!w)return;free(w->a);free(w->b);free(w->s1);free(w->s2);free(w->critical);free(w);}
static int cmp(const void*a,const void*b){uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b;return x<y?-1:x>y;}
World *fb_create(const uint64_t*runs,size_t used,const uint8_t*s1,const uint8_t*s2,size_t colonies,uint64_t age){
 if(!used||!colonies||colonies>UINT64_MAX/M||age<96*Q-1||age>=U)return NULL;
 World*w=calloc(1,sizeof(World));if(!w)return NULL;w->capacity=used+32;w->used=used;w->colonies=colonies;w->age=age;w->words=colonies*M;w->blocks=(w->words+B-1)/B;
 w->a=malloc(w->capacity*sizeof(Run));w->b=malloc(w->capacity*sizeof(Run));w->s1=malloc(colonies);w->s2=malloc(colonies);w->critical=malloc((2*colonies+2)*sizeof(uint64_t));
 if(!w->a||!w->b||!w->s1||!w->s2||!w->critical){fb_free(w);return NULL;}
 memcpy(w->a,runs,used*sizeof(Run));memcpy(w->s1,s1,colonies);memcpy(w->s2,s2,colonies);
 uint64_t previous=0;for(size_t i=0;i<used;++i){if(w->a[i].end<=previous||w->a[i].end>w->blocks){fb_free(w);return NULL;}previous=w->a[i].end;}
 if(previous!=w->blocks){fb_free(w);return NULL;}
 for(size_t c=0;c<colonies;++c)if(s1[c]>1||s2[c]>1){fb_free(w);return NULL;}
 if(w->words%B)for(size_t j=w->words%B;j<B;++j)if(w->a[used-1].f1[j]||w->a[used-1].f2[j]){fb_free(w);return NULL;}
 for(size_t c=0;c<=colonies;++c){uint64_t p=c*M;if(p<w->words)w->critical[w->nc++]=p/B;if(p)w->critical[w->nc++]=(p-1)/B;}
 qsort(w->critical,w->nc,sizeof(uint64_t),cmp);size_t n=0;for(size_t i=0;i<w->nc;++i)if(!n||w->critical[i]!=w->critical[n-1])w->critical[n++]=w->critical[i];w->nc=n;
 return w;
}
static int reserve(World*w,size_t n){
 if(n<=w->capacity)return 0;
 size_t cap=w->capacity*2;if(cap<n)cap=n;Run*a=realloc(w->a,cap*sizeof(Run));if(!a)return -1;w->a=a;
 Run*b=realloc(w->b,cap*sizeof(Run));if(!b)return -1;w->b=b;w->capacity=cap;return 0;
}
static size_t at(World*w,uint64_t pos,size_t*cursor){while(*cursor+1<w->used&&w->a[*cursor].end<=pos)++*cursor;return *cursor;}
static int step(World*w,int*same){
 if(reserve(w,3*w->used+2*w->nc+8))return -1;
 size_t left=0,center=0,right=0,n=0,critical=0;uint64_t pos=0;
 while(pos<w->blocks){size_t c=at(w,pos,&center),l=pos?at(w,pos-1,&left):w->used-1,r=pos+1<w->blocks?at(w,pos+1,&right):0;
  uint64_t end=w->a[c].end,t=pos?w->a[l].end+1:1;if(t<end)end=t;
  t=pos+1<w->blocks?w->a[r].end-1:w->blocks;if(t<end)end=t;
  while(critical<w->nc&&w->critical[critical]<pos)++critical;
  if(critical<w->nc){t=w->critical[critical]==pos?pos+1:w->critical[critical];if(t<end)end=t;}
  Run out;out.end=end;
  for(size_t j=0;j<B;++j){uint64_t word=pos*B+j;if(word>=w->words){out.f1[j]=out.f2[j]=0;continue;}
   uint64_t lf1,lf2,rf1,rf2;
   if(!word){size_t k=(w->words-1)%B;lf1=w->a[w->used-1].f1[k];lf2=w->a[w->used-1].f2[k];}
   else if(j){lf1=w->a[c].f1[j-1];lf2=w->a[c].f2[j-1];}
   else{lf1=w->a[l].f1[B-1];lf2=w->a[l].f2[B-1];}
   if(word+1==w->words){rf1=w->a[0].f1[0];rf2=w->a[0].f2[0];}
   else if(j+1<B){rf1=w->a[c].f1[j+1];rf2=w->a[c].f2[j+1];}
   else{rf1=w->a[r].f1[0];rf2=w->a[r].f2[0];}
   uint64_t input[6]={lf1,lf2,w->a[c].f1[j],w->a[c].f2[j],rf1,rf2},output[2];
   size_t colony=(size_t)(word/M);uint64_t a=word%M;
   fw_word(input,output,a==0,a==M-1,w->s1[colony],w->s2[colony],window(w->age));out.f1[j]=output[0];out.f2[j]=output[1];++w->evaluations;
  }
  if(n&&!memcmp(w->b[n-1].f1,out.f1,2*B*sizeof(uint64_t)))w->b[n-1].end=end;else w->b[n++]=out;
  pos=end;
 }
 *same=n==w->used&&!memcmp(w->a,w->b,n*sizeof(Run));Run*swap=w->a;w->a=w->b;w->b=swap;w->used=n;++w->age;++w->time;++w->literal;return 0;
}
int fb_run(World*w,uint64_t ticks,int skip){
 if(!w||ticks>U-w->age)return -2;
 uint64_t stop=w->time+ticks;
 while(w->time<stop){int before=window(w->age),same=0;if(step(w,&same))return -1;
  if(skip&&same&&before==window(w->age)){uint64_t limit=w->age<96*Q?96*Q:(w->age<98*Q?98*Q:U),delta=limit-w->age;
   if(delta>stop-w->time)delta=stop-w->time;
   w->age+=delta;w->time+=delta;w->quiet+=delta;}}
 return 0;
}
size_t fb_size(World*w){return w->used;}
void fb_export(World*w,uint64_t*out){memcpy(out,w->a,w->used*sizeof(Run));}
void fb_info(World*w,uint64_t*out){out[0]=w->age%U;out[1]=w->time;out[2]=w->literal;out[3]=w->quiet;out[4]=w->evaluations;out[5]=w->used;}
