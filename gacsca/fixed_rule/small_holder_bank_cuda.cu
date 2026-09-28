/* Complete fixed physical rule over bank + arbitrary raw exceptions. */
#include <cuda_runtime.h>
#include <stdint.h>
#include <stdlib.h>
#include "small_holder_bank_generated.h"
struct Bank {
 uint64_t *data,*lk,*lv,*rk,*rv,*rom,*positions,*output;
 uint64_t sites,age; size_t nl,nr;
};
__device__ uint64_t lookup(const uint64_t *keys,const uint64_t *values,size_t n,uint64_t key,uint64_t fallback){
 size_t lo=0,hi=n;
 while(lo<hi){size_t mid=lo+(hi-lo)/2;if(keys[mid]<key)lo=mid+1;else hi=mid;}
 return lo<n&&keys[lo]==key?values[lo]:fallback;
}
__device__ uint64_t shifted(uint64_t position,int delta,uint64_t sites){
 if(delta<0)return position<(uint64_t)(-delta)?sites-(uint64_t)(-delta)+position:position-(uint64_t)(-delta);
 return position+(uint64_t)delta>=sites?position+(uint64_t)delta-sites:position+(uint64_t)delta;
}
__device__ uint64_t logical(Bank b,uint64_t position,int field){
 uint64_t address=position%Q;
 uint64_t fallback=field==L_ADDRESS?address:field==L_AGE?b.age:0;
 if(field==L_DATA&&address<MEM_ROWS)fallback=b.data[(position/Q)*MEM_ROWS+address];
 return lookup(b.lk,b.lv,b.nl,position*LOGICAL_FIELDS+field,fallback);
}
__device__ uint64_t physical(Bank b,uint64_t position,int field){
 uint64_t value;
 if(RAW_STATIC[field]>=0){
  uint64_t address=shifted(logical(b,position,L_ADDRESS),RAW_OFFSET[field],Q);
  int selector=RAW_STATIC[field];
  value=address<ROM_ROWS?b.rom[address*7+selector]:selector==0?(address>=Q-5?0:6):selector==1?address:selector==2&&address>=Q-5?31:0;
 }else value=logical(b,shifted(position,RAW_OFFSET[field],b.sites),RAW_LOGICAL[field]);
 return lookup(b.rk,b.rv,b.nr,position*RAW_FIELDS+field,value);
}
__global__ void evaluate(Bank b,size_t count,int reconstruct){
 size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=count)return;
 uint64_t position=b.positions[i],*out=b.output+i*RAW_FIELDS;
 if(reconstruct){for(int k=0;k<RAW_FIELDS;++k)out[k]=physical(b,position,k);return;}
 uint64_t neighborhood[15*RAW_FIELDS];
 for(int j=-7;j<=7;++j)for(int k=0;k<RAW_FIELDS;++k)neighborhood[(j+7)*RAW_FIELDS+k]=physical(b,shifted(position,j,b.sites),k);
 bank_physical_local(neighborhood,out);
}
extern "C" void bank_free(void *handle){
 Bank*b=(Bank*)handle;if(!b)return;
 cudaFree(b->data);cudaFree(b->lk);cudaFree(b->lv);cudaFree(b->rk);cudaFree(b->rv);cudaFree(b->rom);cudaFree(b->positions);cudaFree(b->output);free(b);
}
static cudaError_t upload(uint64_t **target,const uint64_t *source,size_t words){
 if(!words){*target=nullptr;return cudaSuccess;}
 cudaError_t e=cudaMalloc(target,words*8);if(e==cudaSuccess)e=cudaMemcpy(*target,source,words*8,cudaMemcpyHostToDevice);return e;
}
extern "C" int bank_create(const uint64_t*data,const uint64_t*lk,const uint64_t*lv,size_t nl,const uint64_t*rk,const uint64_t*rv,size_t nr,const uint64_t*rom,uint64_t colonies,uint64_t age,void**handle,uint64_t*allocated){
 *handle=nullptr;
 *allocated=8*(colonies*MEM_ROWS+2*nl+2*nr+ROM_ROWS*7+MAX_BATCH*(1+RAW_FIELDS));
 if(!colonies||*allocated>UINT64_C(64)*1024*1024)return -1;
 Bank*b=(Bank*)calloc(1,sizeof(Bank));if(!b)return -2;
 b->sites=colonies*Q;b->age=age;b->nl=nl;b->nr=nr;
 cudaError_t e=upload(&b->data,data,colonies*MEM_ROWS);
 if(e==cudaSuccess)e=upload(&b->lk,lk,nl);if(e==cudaSuccess)e=upload(&b->lv,lv,nl);
 if(e==cudaSuccess)e=upload(&b->rk,rk,nr);if(e==cudaSuccess)e=upload(&b->rv,rv,nr);
 if(e==cudaSuccess)e=upload(&b->rom,rom,ROM_ROWS*7);
 if(e==cudaSuccess)e=cudaMalloc(&b->positions,MAX_BATCH*8);
 if(e==cudaSuccess)e=cudaMalloc(&b->output,MAX_BATCH*RAW_FIELDS*8);
 if(e!=cudaSuccess){bank_free(b);return (int)e;}*handle=b;return 0;
}
extern "C" int bank_evaluate(void*handle,const uint64_t*positions,size_t count,uint64_t*output,int reconstruct){
 if(!handle||!count||count>MAX_BATCH)return -1;Bank*b=(Bank*)handle;
 cudaError_t e=cudaMemcpy(b->positions,positions,count*8,cudaMemcpyHostToDevice);
 if(e==cudaSuccess){evaluate<<<(unsigned)((count+31)/32),32>>>(*b,count,reconstruct);e=cudaGetLastError();}
 if(e==cudaSuccess)e=cudaMemcpy(output,b->output,count*RAW_FIELDS*8,cudaMemcpyDeviceToHost);return (int)e;
}
