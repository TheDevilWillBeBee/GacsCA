/* Exact canonical-geometry projection of the fixed holder's flag transition.
   Each output bit reads five old physical bits on either side. */
#include <cuda_runtime.h>
#include <stdint.h>
#include <stdlib.h>
#include "small_holder_flags_generated.h"
struct Flags{uint64_t *a,*b;uint8_t *right,*left;size_t colonies,words;uint64_t age;cudaGraph_t graph[2];cudaGraphExec_t exec[2];};
__device__ uint64_t count2(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e){uint64_t s=a^b^c,k=(a&b)|(a&c)|(b&c),l=(s&d)|(s&e)|(d&e);return k|l;}
__device__ uint64_t count3(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e){uint64_t s=a^b^c,k=(a&b)|(a&c)|(b&c),l=(s&d)|(s&e)|(d&e);return (k&l)|((s^d^e)&(k|l));}
__device__ uint64_t count4(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e){uint64_t s=a^b^c,k=(a&b)|(a&c)|(b&c),l=(s&d)|(s&e)|(d&e);return k&l;}
__global__ void flag_step(const uint64_t*old,uint64_t*next,const uint8_t*right,const uint8_t*left,size_t words,bool on){
 size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=words)return;
 size_t before=i?i-1:words-1,after=i+1<words?i+1:0,offset=i%WORDS_PER_COLONY,col=i/WORDS_PER_COLONY;
 uint64_t f=old[2*i],g=old[2*i+1],rr[5],ll[5],inside[5];
 for(int j=1;j<=5;++j){rr[j-1]=(f>>j)|(old[2*after]<<(64-j));if(offset==WORDS_PER_COLONY-1)rr[j-1]&=UINT64_MAX>>j;
  ll[j-1]=(g<<j)|(old[2*before+1]>>(64-j));inside[j-1]=offset==0?ll[j-1]&(UINT64_MAX<<j):ll[j-1];}
 uint64_t nf=count3(rr[0],rr[1],rr[2],rr[3],rr[4])|(f&count2(rr[0],rr[1],rr[2],rr[3],rr[4]));
 if(on&&offset==WORDS_PER_COLONY-1&&right[col])nf|=UINT64_MAX<<56;
 uint64_t force=0;
 if(on&&offset==0&&left[col]){uint64_t wf=(~f)&31;for(int bit=0;bit<8;++bit){int lo=bit>5?bit-5:0;uint64_t mask=31&(~UINT64_C(0)<<lo);if(__popcll(wf&mask)>=3)force|=UINT64_C(1)<<bit;}}
 uint64_t born=count4(inside[0],inside[1],inside[2],inside[3],inside[4])|(nf&count4(ll[0],ll[1],ll[2],ll[3],ll[4]))|force;
 uint64_t erase=(~nf&~count2(inside[0],inside[1],inside[2],inside[3],inside[4]))|(nf&~(ll[0]|ll[1]|ll[2]|ll[3]|ll[4]));
 next[2*i]=nf;next[2*i+1]=force|(g&~erase)|(~g&born);
}
extern "C" void sf_free(void*ptr){Flags*w=(Flags*)ptr;if(!w)return;for(int k=0;k<2;++k){if(w->exec[k])cudaGraphExecDestroy(w->exec[k]);if(w->graph[k])cudaGraphDestroy(w->graph[k]);}cudaFree(w->a);cudaFree(w->b);cudaFree(w->right);cudaFree(w->left);free(w);}
extern "C" int sf_create(size_t colonies,uint64_t age,const uint8_t*right,const uint8_t*left,const uint64_t*initial,void**handle){
 *handle=nullptr;if(!colonies||colonies>128||age<WF_START-1||age>=PERIOD)return -1;
 Flags*w=(Flags*)calloc(1,sizeof(Flags));if(!w)return -2;w->colonies=colonies;w->words=colonies*WORDS_PER_COLONY;w->age=age;
 cudaError_t e=cudaMalloc(&w->a,w->words*16);if(e==cudaSuccess)e=cudaMalloc(&w->b,w->words*16);if(e==cudaSuccess)e=cudaMalloc(&w->right,colonies);if(e==cudaSuccess)e=cudaMalloc(&w->left,colonies);
 if(e==cudaSuccess)e=cudaMemcpy(w->a,initial,w->words*16,cudaMemcpyHostToDevice);if(e==cudaSuccess)e=cudaMemcpy(w->right,right,colonies,cudaMemcpyHostToDevice);if(e==cudaSuccess)e=cudaMemcpy(w->left,left,colonies,cudaMemcpyHostToDevice);
 cudaStream_t stream=nullptr;if(e==cudaSuccess)e=cudaStreamCreate(&stream);
 for(int on=0;on<2&&e==cudaSuccess;++on){e=cudaStreamBeginCapture(stream,cudaStreamCaptureModeThreadLocal);
  for(int k=0;k<GRAPH_TICKS&&e==cudaSuccess;++k){flag_step<<<(unsigned)((w->words+127)/128),128,0,stream>>>(k%2?w->b:w->a,k%2?w->a:w->b,w->right,w->left,w->words,on);e=cudaGetLastError();}
  if(e==cudaSuccess)e=cudaStreamEndCapture(stream,&w->graph[on]);if(e==cudaSuccess)e=cudaGraphInstantiate(&w->exec[on],w->graph[on],nullptr,nullptr,0);
 }
 if(stream)cudaStreamDestroy(stream);if(e!=cudaSuccess){sf_free(w);return (int)e;}*handle=w;return 0;
}
extern "C" int sf_read(void*ptr,uint64_t*out){Flags*w=(Flags*)ptr;if(!w)return -1;return (int)cudaMemcpy(out,w->a,w->words*16,cudaMemcpyDeviceToHost);}
extern "C" int sf_run(void*ptr,uint64_t ticks){Flags*w=(Flags*)ptr;if(!w||ticks>PERIOD-w->age)return -1;cudaError_t e=cudaSuccess;uint64_t remaining=ticks;
 while(remaining&&e==cudaSuccess){bool on=w->age>=WF_START&&w->age<WF_END;uint64_t boundary=w->age<WF_START?WF_START:w->age<WF_END?WF_END:PERIOD;
  uint64_t amount=remaining<boundary-w->age?remaining:boundary-w->age,done=0;
  for(;done+GRAPH_TICKS<=amount&&e==cudaSuccess;done+=GRAPH_TICKS)e=cudaGraphLaunch(w->exec[on],0);
  /* Graphs bind a/b pointers. Odd residual lengths use a copy, never swap them. */
  for(;done<amount&&e==cudaSuccess;++done){flag_step<<<(unsigned)((w->words+127)/128),128>>>(w->a,w->b,w->right,w->left,w->words,on);e=cudaGetLastError();if(e==cudaSuccess)e=cudaMemcpyAsync(w->a,w->b,w->words*16,cudaMemcpyDeviceToDevice);}
  if(e==cudaSuccess){w->age+=amount;remaining-=amount;}
 }
 if(e==cudaSuccess)e=cudaDeviceSynchronize();return (int)e;
}
