#include <cuda_runtime.h>
#include <cstdint>
#include <utility>
#include "generated.h"
using u64=uint64_t;

struct World {size_t n;u64 *a,*b,*work;};

__global__ void step(World w){
 size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
 if(worker>=WORKERS)return;
 u64*in=w.work+worker;
 u64*out=in+15*FIELDS*WORKERS;
 u64*tmp=out+FIELDS*WORKERS;
 for(size_t pos=worker;pos<w.n;pos+=WORKERS){
  for(unsigned j=0;j<15;++j){
   size_t source=(pos+w.n+j-7)%w.n;
   for(unsigned k=0;k<FIELDS;++k)
    in[(j*FIELDS+k)*WORKERS]=w.a[source*FIELDS+k];
  }
  fixed_local(in,out,tmp);
  for(unsigned k=0;k<FIELDS;++k)w.b[pos*FIELDS+k]=out[k*WORKERS];
 }
}

extern "C" void fr_free(World*w){
 if(!w)return;
 cudaFree(w->a);cudaFree(w->b);cudaFree(w->work);delete w;
}

extern "C" int fr_create(size_t n,const u64*raw,u64 budget,
                           World**out,u64*bytes){
 if(!out||!bytes||!raw||n<15||n>(1u<<24))return 1;
 *out=nullptr;
 *bytes=8*(2*n*FIELDS+WORKSPACE_WORDS);
 if(*bytes>budget)return 2;
 World*w=new World{};w->n=n;
 #define ALLOC(name,count) if(cudaMalloc(&w->name,(count)*sizeof(u64))!=cudaSuccess){fr_free(w);return 3;}
 ALLOC(a,n*FIELDS) ALLOC(b,n*FIELDS) ALLOC(work,WORKSPACE_WORDS)
 #undef ALLOC
 if(cudaMemcpy(w->a,raw,n*FIELDS*8,cudaMemcpyHostToDevice)!=cudaSuccess){fr_free(w);return 4;}
 *out=w;return 0;
}

extern "C" int fr_run(World*w,u64 ticks){
 if(!w||ticks>(1u<<20))return 1;
 for(u64 t=0;t<ticks;++t){
  step<<<(WORKERS+63)/64,64>>>(*w);
  if(cudaGetLastError()!=cudaSuccess)return 2;
  std::swap(w->a,w->b);
 }
 return cudaDeviceSynchronize()==cudaSuccess?0:3;
}

extern "C" int fr_read(World*w,u64*out){
 if(!w||!out)return 1;
 return cudaMemcpy(out,w->a,w->n*FIELDS*8,cudaMemcpyDeviceToHost)==cudaSuccess?0:2;
}
