#include <cuda_runtime.h>
#include <stdint.h>
#include <stdlib.h>
#include "small_holder_periodic_bounded_generated.h"
struct World {uint64_t *bg,*nextbg,*positions,*rows,*candidates,*nextrows,*flags,*selected,*readpos,*readout,*workspace;size_t period,count,prepared;uint64_t sites;};
__device__ uint64_t shift(uint64_t x,int j,uint64_t n){
 if(j<0){uint64_t d=(uint64_t)(-j)%n;return x<d?n-d+x:x-d;}
 uint64_t d=(uint64_t)j%n;return x+d>=n?x+d-n:x+d;
}
__device__ uint64_t word(const uint64_t *row,int field){
 unsigned offset=OFFSETS[field],width=WIDTHS[field],w=offset/64,s=offset%64;
 uint64_t v=row[w]>>s;if(s+width>64)v|=row[w+1]<<(64-s);return width==64?v:v&((UINT64_C(1)<<width)-1);
}
__device__ void pack(const uint64_t*raw,uint64_t*out){
 for(int w=0;w<PACKED_WORDS;++w)out[w]=0;
 for(int i=0;i<RAW_FIELDS;++i){unsigned offset=OFFSETS[i],width=WIDTHS[i],w=offset/64,s=offset%64;uint64_t v=raw[i*WORKERS];if(width<64)v&=(UINT64_C(1)<<width)-1;out[w]|=v<<s;if(s+width>64)out[w+1]|=v>>(64-s);}
}
__device__ const uint64_t*cell(World w,uint64_t position){
 size_t lo=0,hi=w.count;while(lo<hi){size_t m=lo+(hi-lo)/2;if(w.positions[m]<position)lo=m+1;else hi=m;}
 return lo<w.count&&w.positions[lo]==position?w.rows+lo*PACKED_WORDS:w.bg+(position%w.period)*PACKED_WORDS;
}
__global__ void background_step(World w){
 size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
 uint64_t*in=w.workspace+worker,*out=w.workspace+15*RAW_FIELDS*WORKERS+worker,*tmp=out+RAW_FIELDS*WORKERS;
 for(size_t i=worker;i<w.period;i+=WORKERS){
  for(int j=-7;j<=7;++j){const uint64_t*row=w.bg+shift(i,j,w.period)*PACKED_WORDS;for(int k=0;k<RAW_FIELDS;++k)in[((j+7)*RAW_FIELDS+k)*WORKERS]=word(row,k);}
  periodic_physical_local(in,out,tmp);pack(out,w.nextbg+i*PACKED_WORDS);
 }
}
__global__ void exception_step(World w,size_t n){
 size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
 uint64_t*in=w.workspace+worker,*out=w.workspace+15*RAW_FIELDS*WORKERS+worker,*tmp=out+RAW_FIELDS*WORKERS;
 for(size_t i=worker;i<n;i+=WORKERS){
  uint64_t position=w.candidates[i];
  for(int j=-7;j<=7;++j){const uint64_t*row=cell(w,shift(position,j,w.sites));for(int k=0;k<RAW_FIELDS;++k)in[((j+7)*RAW_FIELDS+k)*WORKERS]=word(row,k);}
  periodic_physical_local(in,out,tmp);uint64_t*target=w.nextrows+i*PACKED_WORDS;pack(out,target);
  const uint64_t*base=w.nextbg+(position%w.period)*PACKED_WORDS;uint64_t mismatch=0;
  for(int k=0;k<PACKED_WORDS;++k)mismatch|=target[k]^base[k];w.flags[i]=mismatch!=0;
 }
}
__global__ void compact(World w,size_t n){
 size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=n)return;size_t from=w.selected[i];
 w.positions[i]=w.candidates[from];for(int k=0;k<PACKED_WORDS;++k)w.rows[i*PACKED_WORDS+k]=w.nextrows[from*PACKED_WORDS+k];
}
__global__ void read_cells(World w,size_t n){
 size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=n)return;const uint64_t*source=cell(w,w.readpos[i]);
 for(int k=0;k<PACKED_WORDS;++k)w.readout[i*PACKED_WORDS+k]=source[k];
}
extern "C" void periodic_free(void*handle){
 World*w=(World*)handle;if(!w)return;
 cudaFree(w->bg);cudaFree(w->nextbg);cudaFree(w->positions);cudaFree(w->rows);cudaFree(w->candidates);cudaFree(w->nextrows);cudaFree(w->flags);cudaFree(w->selected);cudaFree(w->readpos);cudaFree(w->readout);cudaFree(w->workspace);free(w);
}
static cudaError_t alloc(uint64_t**p,size_t words){return cudaMalloc(p,words*8);}
extern "C" int periodic_create(const uint64_t*bg,size_t period,uint64_t sites,const uint64_t*positions,const uint64_t*rows,size_t count,void**handle,uint64_t*allocated){
 *handle=nullptr;*allocated=8*(2*period*PACKED_WORDS+2*CAPACITY*PACKED_WORDS+4*CAPACITY+READ_CAPACITY*(1+PACKED_WORDS)+WORKSPACE_WORDS);
 if(!period||sites<period||sites%period||count>CAPACITY||*allocated>UINT64_C(64)*1024*1024)return -1;
 World*w=(World*)calloc(1,sizeof(World));if(!w)return -2;w->period=period;w->sites=sites;w->count=count;
 cudaError_t e=alloc(&w->bg,period*PACKED_WORDS);
 if(e==cudaSuccess)e=alloc(&w->nextbg,period*PACKED_WORDS);
 if(e==cudaSuccess)e=alloc(&w->positions,CAPACITY);if(e==cudaSuccess)e=alloc(&w->rows,CAPACITY*PACKED_WORDS);
 if(e==cudaSuccess)e=alloc(&w->candidates,CAPACITY);if(e==cudaSuccess)e=alloc(&w->nextrows,CAPACITY*PACKED_WORDS);
 if(e==cudaSuccess)e=alloc(&w->flags,CAPACITY);if(e==cudaSuccess)e=alloc(&w->selected,CAPACITY);
 if(e==cudaSuccess)e=alloc(&w->readpos,READ_CAPACITY);if(e==cudaSuccess)e=alloc(&w->readout,READ_CAPACITY*PACKED_WORDS);
 if(e==cudaSuccess)e=alloc(&w->workspace,WORKSPACE_WORDS);
 if(e==cudaSuccess)e=cudaMemcpy(w->bg,bg,period*PACKED_WORDS*8,cudaMemcpyHostToDevice);
 if(e==cudaSuccess&&count)e=cudaMemcpy(w->positions,positions,count*8,cudaMemcpyHostToDevice);
 if(e==cudaSuccess&&count)e=cudaMemcpy(w->rows,rows,count*PACKED_WORDS*8,cudaMemcpyHostToDevice);
 if(e!=cudaSuccess){periodic_free(w);return (int)e;}*handle=w;return 0;
}
extern "C" int periodic_prepare(void*handle,const uint64_t*positions,size_t count,uint64_t*flags){
 if(!handle||count>CAPACITY)return -1;World*w=(World*)handle;cudaError_t e=cudaSuccess;
 if(count)e=cudaMemcpy(w->candidates,positions,count*8,cudaMemcpyHostToDevice);
 if(e==cudaSuccess){background_step<<<WORKERS/32,32>>>(*w);e=cudaGetLastError();}
 if(e==cudaSuccess&&count){exception_step<<<WORKERS/32,32>>>(*w,count);e=cudaGetLastError();}
 if(e==cudaSuccess&&count)e=cudaMemcpy(flags,w->flags,count*8,cudaMemcpyDeviceToHost);
 if(e==cudaSuccess)e=cudaDeviceSynchronize();w->prepared=count;return (int)e;
}
extern "C" int periodic_commit(void*handle,const uint64_t*selected,size_t count){
 if(!handle)return -1;World*w=(World*)handle;if(count>w->prepared)return -2;cudaError_t e=cudaSuccess;
 if(count)e=cudaMemcpy(w->selected,selected,count*8,cudaMemcpyHostToDevice);
 if(e==cudaSuccess&&count){compact<<<(unsigned)((count+127)/128),128>>>(*w,count);e=cudaGetLastError();}
 if(e==cudaSuccess)e=cudaDeviceSynchronize();if(e!=cudaSuccess)return (int)e;
 uint64_t*old=w->bg;w->bg=w->nextbg;w->nextbg=old;w->count=count;w->prepared=0;return 0;
}
extern "C" int periodic_read(void*handle,const uint64_t*positions,size_t count,uint64_t*out){
 if(!handle||!count||count>READ_CAPACITY)return -1;World*w=(World*)handle;
 cudaError_t e=cudaMemcpy(w->readpos,positions,count*8,cudaMemcpyHostToDevice);
 if(e==cudaSuccess){read_cells<<<(unsigned)((count+127)/128),128>>>(*w,count);e=cudaGetLastError();}
 if(e==cudaSuccess)e=cudaMemcpy(out,w->readout,count*PACKED_WORDS*8,cudaMemcpyDeviceToHost);return (int)e;
}
