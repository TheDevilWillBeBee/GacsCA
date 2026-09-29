/* Exact unforced printed-rule physical flag projection on canonical geometry.
   Build header is mechanically extracted from frozen flag_words.c. No upper
   transition, depth parameter, or change to the physical rule occurs here. */
#include <cuda_runtime.h>
#include <stdint.h>
#define FLAG_INLINE __device__ __forceinline__
#define __builtin_popcountll __popcll
#include "flag_word_generated.h"
#undef __builtin_popcountll
constexpr int CORE=256, MAX_T=512, MAX_HALO=(5*MAX_T+63)/64+1;

__global__ void evolve(const uint64_t*src,uint64_t*dst,uint64_t words,int ticks,int shortcuts){
 __shared__ uint64_t memory[2][2*(CORE+2*MAX_HALO)];
 const int halo=(5*ticks+63)/64+1, width=CORE+2*halo;
 const int lane=threadIdx.x;
 const long long start=(long long)blockIdx.x*CORE-halo;
 for(int j=lane;j<width;j+=CORE){
  uint64_t pos=(uint64_t)((start+j+(long long)words)%(long long)words);
  memory[0][2*j]=src[2*pos];memory[0][2*j+1]=src[2*pos+1];
 }
 __syncthreads();
 // General local fixed-point certificate. Every inner-halo word is checked
 // by the actual physical transition, including geometric boundary masks.
 // The outer word is excluded; the remaining halo still exceeds 5*ticks bits.
 // A stationary inner halo therefore protects the core for this whole block.
 __shared__ int stable;
 if(lane==0)stable=shortcuts;
 __syncthreads();
 if(shortcuts){
  for(int j=lane+1;j<width-1;j+=CORE){
   uint64_t pos=(uint64_t)((start+j+(long long)words)%(long long)words);
   uint64_t out[2];fw_word(memory[0]+2*j-2,out,pos%M==0,pos%M==M-1,0,0,0);
   if(out[0]!=memory[0][2*j]||out[1]!=memory[0][2*j+1])atomicExch(&stable,0);
  }
 }
 __syncthreads();
 if(stable){uint64_t pos=(uint64_t)blockIdx.x*CORE+lane;dst[2*pos]=memory[0][2*(halo+lane)];dst[2*pos+1]=memory[0][2*(halo+lane)+1];return;}
 // An entire halo of homogeneous bits away from colony edges has a spatially
 // constant orbit. Test actual input; never assume that a front stays put.
 __shared__ int uniform;
 if(lane==0)uniform=shortcuts;
 __syncthreads();
 uint64_t f=memory[0][2*halo],g=memory[0][2*halo+1];
 for(int j=lane;j<width;j+=CORE){
  uint64_t pos=(uint64_t)((start+j+(long long)words)%(long long)words);
  if((f!=0&&f!=UINT64_MAX)||(g!=0&&g!=UINT64_MAX)||memory[0][2*j]!=f||memory[0][2*j+1]!=g||pos%M==0||pos%M==M-1)atomicExch(&uniform,0);
 }
 __syncthreads();
 if(uniform){uint64_t pos=(uint64_t)blockIdx.x*CORE+lane;dst[2*pos]=f;dst[2*pos+1]=f?g:0;return;}
 for(int t=0;t<ticks;++t){
  const int a=t&1,b=a^1;
  for(int j=lane;j<width;j+=CORE){
   uint64_t pos=(uint64_t)((start+j+(long long)words)%(long long)words);
   uint64_t in[6]={0,0,memory[a][2*j],memory[a][2*j+1],0,0},out[2];
   if(j){in[0]=memory[a][2*j-2];in[1]=memory[a][2*j-1];}
   if(j+1<width){in[4]=memory[a][2*j+2];in[5]=memory[a][2*j+3];}
   fw_word(in,out,pos%M==0,pos%M==M-1,0,0,0);
   memory[b][2*j]=out[0];memory[b][2*j+1]=out[1];
  }
  __syncthreads();
 }
 // Incorrect virtual boundary inputs cannot cross the 5*ticks-bit halo.
 uint64_t pos=(uint64_t)blockIdx.x*CORE+lane;
 dst[2*pos]=memory[ticks&1][2*(halo+lane)];dst[2*pos+1]=memory[ticks&1][2*(halo+lane)+1];
}
extern "C" int flag_cuda_run(const uint64_t*input,uint64_t*output,uint64_t words,uint64_t ticks,int block_ticks,int shortcuts){
 if(!words||words%M||block_ticks<1||block_ticks>MAX_T||words>UINT64_MAX/16)return -1;
 uint64_t*a=nullptr,*b=nullptr;size_t bytes=(size_t)words*2*sizeof(uint64_t);
 cudaError_t err=cudaMalloc(&a,bytes);if(err!=cudaSuccess)return (int)err;
 err=cudaMalloc(&b,bytes);if(err!=cudaSuccess){cudaFree(a);return (int)err;}
 err=cudaMemcpy(a,input,bytes,cudaMemcpyHostToDevice);
 for(uint64_t done=0;err==cudaSuccess&&done<ticks;){
  int dt=(int)((ticks-done<(uint64_t)block_ticks)?ticks-done:block_ticks);
  evolve<<<(unsigned)(words/CORE),CORE>>>(a,b,words,dt,shortcuts);
  err=cudaGetLastError();uint64_t*tmp=a;a=b;b=tmp;done+=dt;
 }
 if(err==cudaSuccess)err=cudaMemcpy(output,a,bytes,cudaMemcpyDeviceToHost);
 cudaFree(a);cudaFree(b);return (int)err;
}
