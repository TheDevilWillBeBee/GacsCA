/* GPU local transition for the exact coherent, zero-flag physical prefix.
   The generated body is pinned to the same descriptor and ROM as the CPU.
   Small batch ABI: no hierarchy depth, host evaluator or shared CUDA backend. */
#include <cuda_runtime.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "holder_cuda_local_generated.h"

__device__ uint64_t read_packed(const uint64_t*row,int field){
 const unsigned offset=FIELD_OFFSETS[field],width=FIELD_WIDTHS[field],word=offset/64,shift=offset%64;
 uint64_t value=row[word]>>shift;
 if(shift+width>64)value|=row[word+1]<<(64-shift);
 return width==64?value:value&((UINT64_C(1)<<width)-1);
}
__device__ void write_packed(uint64_t*row,int field,uint64_t value){
 const unsigned offset=FIELD_OFFSETS[field],width=FIELD_WIDTHS[field],word=offset/64,shift=offset%64;
 if(width<64)value&=(UINT64_C(1)<<width)-1;
 row[word]|=value<<shift;
 if(shift+width>64)row[word+1]|=value>>(64-shift);
}
__global__ void local_batch(const uint64_t*input,uint64_t*output,const uint64_t*rom,size_t count){
 size_t index=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(index>=count)return;
 uint64_t neighborhood[11*FIELDS],out[FIELDS];
 for(int j=0;j<11;++j){
  const uint64_t*row=input+(index*11+j)*PACKED_WORDS;uint64_t*cell=neighborhood+j*FIELDS;
  uint64_t address=read_packed(row,P_ADDRESS);
  for(int k=0;k<7;++k)cell[STATIC_FIELDS[k]]=address<ROM_ROWS?rom[address*7+k]:0;
  if(address>=ROM_ROWS){cell[KIND]=address>=COLONY_CELLS-5?0:6;cell[INDEX]=address;cell[A]=address>=COLONY_CELLS-5?31:0;}
  for(int k=0;k<P_FIELDS;++k)cell[DYNAMIC_FIELDS[k]]=read_packed(row,k);
 }
 holder_prefix_local(neighborhood,out);
 uint64_t*target=output+index*PACKED_WORDS;
 for(int k=0;k<PACKED_WORDS;++k)target[k]=0;
 for(int k=0;k<P_FIELDS;++k)write_packed(target,k,out[DYNAMIC_FIELDS[k]]);
}
extern "C" int holder_cuda_local(const uint64_t*input,uint64_t*output,const uint64_t*rom,size_t count,uint64_t*allocated){
 if(!count||count>4096)return -1;
 const size_t in_bytes=count*11*PACKED_WORDS*8,out_bytes=count*PACKED_WORDS*8,rom_bytes=ROM_ROWS*7*8;
 *allocated=in_bytes+out_bytes+rom_bytes;
 if(*allocated>UINT64_C(64)*1024*1024)return -2;
 uint64_t *a=nullptr,*b=nullptr,*table=nullptr;cudaError_t e=cudaMalloc(&a,in_bytes);
 if(e==cudaSuccess)e=cudaMalloc(&b,out_bytes);
 if(e==cudaSuccess)e=cudaMalloc(&table,rom_bytes);
 if(e==cudaSuccess)e=cudaMemcpy(a,input,in_bytes,cudaMemcpyHostToDevice);
 if(e==cudaSuccess)e=cudaMemcpy(table,rom,rom_bytes,cudaMemcpyHostToDevice);
 if(e==cudaSuccess){local_batch<<<(unsigned)((count+63)/64),64>>>(a,b,table,count);e=cudaGetLastError();}
 if(e==cudaSuccess)e=cudaMemcpy(output,b,out_bytes,cudaMemcpyDeviceToHost);
 cudaFree(table);cudaFree(b);cudaFree(a);return (int)e;
}
