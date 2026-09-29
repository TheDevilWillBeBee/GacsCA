// Literal G = pi F iota. Every input dependency is within radius seven.
#include <cuda_runtime.h>
#include <cstdint>
#include <utility>
#include "compact16_holder_dense_generated.h"
using u64=uint64_t;
struct World {size_t n;u64 *a,*b,*rom,*work;};
__global__ void step(World w){
 size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
 if(worker>=WORKERS)return;
 u64*in=w.work+worker,*out=in+15*FIELDS*WORKERS,*tmp=out+FIELDS*WORKERS;
 for(size_t pos=worker;pos<w.n;pos+=WORKERS){
  for(unsigned j=0;j<15;++j){
   size_t source=(pos+w.n+j%w.n)%w.n;source=(source+w.n-7%w.n)%w.n;
   for(unsigned k=0;k<FIELDS;++k)in[(j*FIELDS+k)*WORKERS]=w.a[source*FIELDS+k];
  }
  dense_full_local(in,out,tmp);
  u64 address=out[ADDRESS*WORKERS];
  for(unsigned k=0;k<FIELDS;++k){
   u64 value=out[k*WORKERS];
   if(k<49)value=w.rom[((address+Q+k/7-3)%Q)*7+k%7];
   w.b[pos*FIELDS+k]=value;
  }
 }
}
extern "C" void dg_free(World*w){if(!w)return;cudaFree(w->a);cudaFree(w->b);cudaFree(w->rom);cudaFree(w->work);delete w;}
extern "C" int dg_create(size_t n,const u64*raw,const u64*rom,u64 budget,World**out,u64*bytes){
 if(!out||!bytes||!raw||!rom||!n||n>(1u<<24))return 1;*out=nullptr;
 *bytes=8*(2*n*FIELDS+Q*7+WORKSPACE);if(*bytes>budget)return 2;
 World*w=new World{};w->n=n;
 #define ALLOC(name,count) if(cudaMalloc(&w->name,(count)*sizeof(u64))!=cudaSuccess){dg_free(w);return 3;}
 ALLOC(a,n*FIELDS) ALLOC(b,n*FIELDS) ALLOC(rom,Q*7) ALLOC(work,WORKSPACE)
 #undef ALLOC
 if(cudaMemcpy(w->a,raw,n*FIELDS*8,cudaMemcpyHostToDevice)!=cudaSuccess||cudaMemcpy(w->rom,rom,Q*7*8,cudaMemcpyHostToDevice)!=cudaSuccess){dg_free(w);return 4;}
 *out=w;return 0;
}
extern "C" int dg_run(World*w,u64 ticks){
 if(!w||ticks>65536)return 1;
 for(u64 t=0;t<ticks;++t){step<<<(WORKERS+63)/64,64>>>(*w);if(cudaGetLastError()!=cudaSuccess)return 2;std::swap(w->a,w->b);}
 return cudaDeviceSynchronize()==cudaSuccess?0:3;
}
extern "C" int dg_read(World*w,u64*out){if(!w||!out)return 1;return cudaMemcpy(out,w->a,w->n*FIELDS*8,cudaMemcpyDeviceToHost)==cudaSuccess?0:2;}
