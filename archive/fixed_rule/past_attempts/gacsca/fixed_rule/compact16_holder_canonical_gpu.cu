// Canonical geometry only; all non-geometry raw fields remain arbitrary.
#include <cuda_runtime.h>
#include <cstdint>
#include <utility>
#include "compact16_holder_canonical_generated.h"
using u64=uint64_t;
struct World{size_t n;u64 *a,*b,*rom,*work,*voted,*next,*flags,*signal;};
__device__ size_t wrap(long long pos,size_t n){return (pos+(long long)n)%n;}
__device__ u64 raw(World w,long long pos,unsigned k){return w.a[wrap(pos,w.n)*FIELDS+k];}
__device__ u64 majority(u64 a,u64 b,u64 c,u64 d,u64 e){return (a&b&c)|(((a&b)|(a&c)|(b&c))&(d|e))|((a|b|c)&d&e);}
__global__ void gather(World w){
 size_t pos=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(pos>=w.n)return;
 for(unsigned k=0;k<PROC;++k){u64 v[5];for(int d=-2;d<=2;++d)v[d+2]=raw(w,(long long)pos+d,49+(2-d)*PROC+k);w.voted[pos*PROC+k]=majority(v[0],v[1],v[2],v[3],v[4]);}
 unsigned signal=0;for(int d=-2;d<=2;++d)signal+=(raw(w,(long long)pos+d,F_SIGNAL)>>(2-d))&1;w.signal[pos]=signal>=3;
 int address=pos%Q;unsigned right=0,left=0,left_raw=0,wf1=0,wf2=0;
 for(int j=-5;j<=5;++j){bool inside=address+j>=0&&address+j<Q;
  if(inside){wf1+=raw(w,(long long)pos+j,F_W2_WF1);wf2+=raw(w,(long long)pos+j,F_W2_WF2);}
  if(j>0&&inside)right+=raw(w,(long long)pos+j,F_F1);
  if(j<0){unsigned flag=raw(w,(long long)pos+j,F_F2);left_raw+=flag;if(inside)left+=flag;}
 }
 bool f1=wf1>=3||right>=3||(raw(w,pos,F_F1)&&right>=2);
 bool on=left>=4||(f1&&left_raw>=4)||wf2>=3;
 bool erase=(!f1&&left<=1)||(f1&&left_raw==0);
 w.flags[2*pos]=f1;w.flags[2*pos+1]=raw(w,pos,F_F2)?(wf2>=3||!erase):on;
}
__global__ void compute(World w){
 size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(worker>=WORKERS)return;
 u64*in=w.work+worker,*out=in+5*CORE*WORKERS,*tmp=out+CORE*WORKERS;
 for(size_t pos=worker;pos<w.n;pos+=WORKERS){
  for(unsigned k=0;k<5*CORE;++k)in[k*WORKERS]=0;
  for(int j=-2;j<=2;++j){size_t target=wrap((long long)pos+j,w.n);unsigned offset=(j+2)*CORE;
   in[(offset+C_ADDRESS)*WORKERS]=target%Q;in[(offset+C_AGE)*WORKERS]=w.a[pos*FIELDS+F_AGE];
   if(j>=-1&&j<=1){
    for(unsigned k=0;k<PROC;++k)in[(offset+proc_core[k])*WORKERS]=w.voted[target*PROC+k];
    for(unsigned k=0;k<7;++k)in[(offset+static_core[k])*WORKERS]=w.rom[(target%Q)*7+k];
   }else if(j==2)in[(offset+C_DATA)*WORKERS]=w.voted[target*PROC];
  }
  canonical_clock(in,out,tmp);
  for(unsigned k=0;k<PROC;++k)w.next[pos*PROC+k]=out[proc_core[k]*WORKERS];
 }
}
__global__ void scatter(World w){
 size_t pos=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(pos>=w.n)return;
 int address=pos%Q;u64 age=(w.a[pos*FIELDS+F_AGE]+1)%U;u64*dest=w.b+pos*FIELDS;
 for(unsigned k=0;k<49;++k)dest[k]=w.rom[((address+Q+k/7-3)%Q)*7+k%7];
 u64 signal=0;
 for(int d=-2;d<=2;++d){size_t target=wrap((long long)pos+d,w.n);unsigned a=target%Q;
  for(unsigned k=0;k<PROC;++k)dest[49+(d+2)*PROC+k]=(k>=10&&w.flags[2*pos])?0:w.next[target*PROC+k];
  bool value=w.signal[target];if(age==CAPTURE&&(address+d==3||address+d==Q-3))value=w.voted[pos*PROC]&1;
  signal|=(u64)value<<(d+2);u64 wf1=0,wf2=0;
  if(age>=WF_START&&age<WF_END){
   if(a>=Q-5)wf1=w.signal[target-a+Q-3];
   if(a<=4&&!w.flags[2*target])wf2=w.signal[target-a+3];
  }
  dest[F_W0_WF1+2*(d+2)]=wf1;dest[F_W0_WF1+2*(d+2)+1]=wf2;
 }
 dest[F_ADDRESS]=address;dest[F_AGE]=age;dest[F_F1]=w.flags[2*pos];dest[F_F2]=w.flags[2*pos+1];dest[F_SIGNAL]=signal;
}
extern "C" void cf_free(World*w){if(!w)return;cudaFree(w->a);cudaFree(w->b);cudaFree(w->rom);cudaFree(w->work);cudaFree(w->voted);cudaFree(w->next);cudaFree(w->flags);cudaFree(w->signal);delete w;}
extern "C" int cf_create(size_t n,const u64*raw,const u64*rom,u64 budget,World**out,u64*bytes){
 if(!out||!bytes||!raw||!rom||!n||n%Q||n>(1u<<24))return 1;*out=nullptr;
 *bytes=8*(2*n*FIELDS+2*n*PROC+3*n+Q*7+WORKSPACE);if(*bytes>budget)return 2;
 World*w=new World{};w->n=n;
 #define ALLOC(name,count) if(cudaMalloc(&w->name,(count)*sizeof(u64))!=cudaSuccess){cf_free(w);return 3;}
 ALLOC(a,n*FIELDS) ALLOC(b,n*FIELDS) ALLOC(rom,Q*7) ALLOC(work,WORKSPACE)
 ALLOC(voted,n*PROC) ALLOC(next,n*PROC) ALLOC(flags,2*n) ALLOC(signal,n)
 #undef ALLOC
 if(cudaMemcpy(w->a,raw,n*FIELDS*8,cudaMemcpyHostToDevice)!=cudaSuccess||cudaMemcpy(w->rom,rom,Q*7*8,cudaMemcpyHostToDevice)!=cudaSuccess){cf_free(w);return 4;}
 *out=w;return 0;
}
extern "C" int cf_run(World*w,u64 ticks){
 if(!w||ticks>65536)return 1;
 for(u64 t=0;t<ticks;++t){
  gather<<<(w->n+127)/128,128>>>(*w);compute<<<(WORKERS+63)/64,64>>>(*w);scatter<<<(w->n+127)/128,128>>>(*w);
  if(cudaGetLastError()!=cudaSuccess)return 2;std::swap(w->a,w->b);
 }
 return cudaDeviceSynchronize()==cudaSuccess?0:3;
}
extern "C" int cf_read(World*w,u64*out){if(!w||!out)return 1;return cudaMemcpy(out,w->a,w->n*FIELDS*8,cudaMemcpyDeviceToHost)==cudaSuccess?0:2;}
