// Exact endpoint operator on the certified E_loc domain; not a literal tick.
// The instruction/metadata arrays are generated once from the one fixed ROM.
#include <cuda_runtime.h>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <utility>
#include "retimed_holder_endpoint_generated.h"
using u64=uint64_t;
struct World {size_t n;u64 *bank,*next,*raw,*signals,*nextsignals,*rom,*code;unsigned *status;};
__global__ void extract(World w){size_t col=blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.n)return;
 for(unsigned k=0;k<FIELDS;++k)w.raw[col*FIELDS+k]=w.bank[col*BANK+INFO_BASE+2*k];
 unsigned error=0;u64 *raw=w.raw+col*FIELDS;
 for(unsigned k=0;k<FIELDS;++k)if(WIDTHS[k]<64&&(raw[k]>>WIDTHS[k]))error=1;
 if(!error){u64 address=raw[ADDRESS];for(unsigned j=0;j<7;++j)for(unsigned k=0;k<7;++k)
  if(raw[j*7+k]!=w.rom[((address+Q+j-3)%Q)*7+k])error=2;}
 w.status[col]=error;
}
__global__ void terminal(World w){size_t col=blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.n)return;
 u64 *bank=w.next+col*BANK;for(unsigned k=0;k<BANK;++k)bank[k]=0;
 for(unsigned j=0;j<15;++j){size_t neighbor=(col+w.n+(j%w.n))%w.n;neighbor=(neighbor+w.n-(7%w.n))%w.n;
  for(unsigned k=0;k<FIELDS;++k){u64 value=w.raw[neighbor*FIELDS+k];unsigned a=RESERVED+4*(j*FIELDS+k);
   bank[a]=value;bank[a+1]=value;bank[a+2]=value;bank[a+3]=value;}}
 for(unsigned k=0;k<FIELDS;++k)bank[INFO_BASE+2*k]=w.raw[col*FIELDS+k];
 u64 loaded=Q;unsigned error=0;
 for(unsigned pc=0;pc<INSTRUCTIONS;++pc){const u64 *op=w.code+4*pc;u64 kind=op[0],a=op[1],b=op[2],d=op[3];
  switch(kind){
   case OP_LIT:bank[d]=a;break;
   case OP_NAND:bank[d]=~(bank[a]&bank[b]);break;
   case OP_ADD:bank[d]=bank[a]+bank[b];break;
   case OP_SHR:bank[d]=bank[b]<64?bank[a]>>bank[b]:0;break;
   case OP_EQ:bank[d]=(bank[a]==bank[b]);break;
   case OP_LT:bank[d]=(bank[a]<bank[b]);break;
   case OP_LOAD:loaded=bank[a];break;
   case OP_META:if(loaded>=Q||b>=7){error=3;}else bank[a]=w.rom[loaded*7+b];break;
   case OP_IF_THIRD:if(pc+1!=INSTRUCTIONS)error=4;break;
   default:error=5;
  }
  if(error)break;
 }
 for(unsigned k=0;k<FIELDS&&!error;++k)if(WIDTHS[k]<64&&(bank[INFO_BASE+2*k+1]>>WIDTHS[k]))error=6;
 w.nextsignals[2*col]=bank[INFO_BASE+2*FLAG2+1];w.nextsignals[2*col+1]=bank[INFO_BASE+2*FLAG1+1];
 w.status[col]=error;
}
__global__ void commit(World w){size_t col=blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.n)return;
 for(unsigned k=0;k<FIELDS;++k)w.bank[col*BANK+INFO_BASE+2*k]=w.bank[col*BANK+INFO_BASE+2*k+1];
}
static int status(World*w){std::vector<unsigned> values(w->n);if(cudaMemcpy(values.data(),w->status,w->n*sizeof(unsigned),cudaMemcpyDeviceToHost)!=cudaSuccess)return -1;for(unsigned value:values)if(value)return int(value);return 0;}
extern "C" void te_free(World*w){if(!w)return;cudaFree(w->bank);cudaFree(w->next);cudaFree(w->raw);cudaFree(w->signals);cudaFree(w->nextsignals);cudaFree(w->rom);cudaFree(w->code);cudaFree(w->status);delete w;}
extern "C" int te_create(size_t n,u64 budget,const u64*bank,const u64*signals,World**out,u64*bytes){
 if(!out||!bytes||!bank||!signals||!n||n>(1u<<20))return 1;*out=nullptr;
 u64 cost=8*(2*n*BANK+n*FIELDS+4*n+Q*7+INSTRUCTIONS*4)+4*n;*bytes=cost;if(cost>budget)return 2;
 World*w=new World{};w->n=n;
 #define ALLOC(field,count) if(cudaMalloc(&w->field,(count)*sizeof(*w->field))!=cudaSuccess){te_free(w);return 3;}
 ALLOC(bank,n*BANK) ALLOC(next,n*BANK) ALLOC(raw,n*FIELDS) ALLOC(signals,2*n) ALLOC(nextsignals,2*n) ALLOC(rom,Q*7) ALLOC(code,INSTRUCTIONS*4) ALLOC(status,n)
 #undef ALLOC
 if(cudaMemcpy(w->bank,bank,n*BANK*8,cudaMemcpyHostToDevice)!=cudaSuccess||cudaMemcpy(w->signals,signals,n*2*8,cudaMemcpyHostToDevice)!=cudaSuccess||cudaMemcpy(w->rom,ROM_INIT,sizeof(ROM_INIT),cudaMemcpyHostToDevice)!=cudaSuccess||cudaMemcpy(w->code,CODE_INIT,sizeof(CODE_INIT),cudaMemcpyHostToDevice)!=cudaSuccess){te_free(w);return 4;}
 *out=w;return 0;
}
extern "C" int te_precommit(World*w){if(!w)return -2;
 extract<<<(w->n+127)/128,128>>>(*w);int code=status(w);if(code)return 10+code;
 terminal<<<(w->n+127)/128,128>>>(*w);code=status(w);if(code)return 20+code;
 std::swap(w->bank,w->next);std::swap(w->signals,w->nextsignals);return 0;
}
extern "C" int te_commit(World*w){if(!w)return -2;commit<<<(w->n+127)/128,128>>>(*w);return cudaDeviceSynchronize()==cudaSuccess?0:1;}
extern "C" int te_read(World*w,u64*bank,u64*signals){if(!w||!bank||!signals)return 1;
 return cudaMemcpy(bank,w->bank,w->n*BANK*8,cudaMemcpyDeviceToHost)!=cudaSuccess||cudaMemcpy(signals,w->signals,w->n*2*8,cudaMemcpyDeviceToHost)!=cudaSuccess;
}
