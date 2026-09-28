// Tile the same complete endpoint operator over raw or canonical image storage.
#include <cuda_runtime.h>
#include <cstdint>
#include <vector>
#include "retimed_holder_endpoint_tiles_generated.h"
using u64=uint64_t;
struct Source {u64 n,age;int kind;u64 *values,*signals;};
struct Window {size_t n,capacity;u64 *raw,*next,*nextsignals,*rom,*code;unsigned *status;};
__device__ u64 signal_word(u64 a,u64 left,u64 right){return a>=1&&a<=5?left<<(5-a):a>=Q-5?right<<(Q-1-a):0;}
__device__ u64 data(Source s,u64 pos){pos%=s.n;u64 col=pos/Q,a=pos%Q;return a<MEMORY?s.values[col*BANK+a]:a>=Q-5?s.values[col*BANK+MEMORY+a-(Q-5)]:0;}
__device__ u64 field(Source s,const u64*rom,u64 pos,unsigned k){pos%=s.n;if(!s.kind)return s.values[pos*FIELDS+k];
 u64 col=pos/Q,a=pos%Q;if(k<49)return rom[((a+Q+k/7-3)%Q)*7+k%7];
 if(k==ADDRESS)return a;if(k==RAW_AGE)return s.age;if(k==RAW_SIGNAL)return signal_word(a,s.signals[2*col],s.signals[2*col+1]);
 for(unsigned j=0;j<5;++j)if(k==DATA_FIELDS[j])return data(s,(pos+s.n+j-2)%s.n);
 return 0;
}
__global__ void gather(Source s,Window w,u64 start){size_t i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=w.n+14)return;
 u64 pos=(start+s.n+(i%s.n))%s.n;pos=(pos+s.n-(7%s.n))%s.n;unsigned error=0;u64*raw=w.raw+i*FIELDS;
 for(unsigned k=0;k<FIELDS;++k){raw[k]=field(s,w.rom,pos,k);if(WIDTHS[k]<64&&(raw[k]>>WIDTHS[k]))error=1;}
 if(!error)for(unsigned j=0;j<7;++j)for(unsigned k=0;k<7;++k)if(raw[j*7+k]!=w.rom[((raw[ADDRESS]+Q+j-3)%Q)*7+k])error=2;
 w.status[i]=error;
}
// GENERATED_TERMINAL
__global__ void tile_commit(Window w){size_t col=blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.n)return;for(unsigned k=0;k<FIELDS;++k)w.next[col*BANK+INFO_BASE+2*k]=w.next[col*BANK+INFO_BASE+2*k+1];}
__global__ void encode_initial(Source input,Source image){size_t col=blockIdx.x*blockDim.x+threadIdx.x;if(col>=input.n)return;for(unsigned k=0;k<FIELDS;++k)image.values[col*BANK+INFO_BASE+2*k]=input.values[col*FIELDS+k];}
__global__ void cells(Source s,Window w,u64 start,size_t n,u64*out){size_t i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=n)return;for(unsigned k=0;k<FIELDS;++k)out[i*FIELDS+k]=field(s,w.rom,(start+i)%s.n,k);}
__global__ void collect(Window w,Source output,u64 start){size_t i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=w.n)return;for(unsigned k=0;k<FIELDS;++k)output.values[(start+i)*FIELDS+k]=w.next[i*BANK+INFO_BASE+2*k];}
__global__ void decode(Source input,Source output,Window w){size_t i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=output.n)return;for(unsigned k=0;k<FIELDS;++k)output.values[i*FIELDS+k]=field(input,w.rom,i*Q+INFO_BASE+2*k,DATA_PRIMARY);}
static int sync(){return cudaDeviceSynchronize()==cudaSuccess?0:1;}
static int status(Window*w,size_t n){std::vector<unsigned>values(n);if(cudaMemcpy(values.data(),w->status,n*4,cudaMemcpyDeviceToHost)!=cudaSuccess)return -1;for(unsigned x:values)if(x)return int(x);return 0;}
extern "C" void tt_source_free(Source*s){if(!s)return;cudaFree(s->values);cudaFree(s->signals);delete s;}
static int allocate_source(size_t n,int kind,u64 age,u64 budget,Source**out,u64*bytes){if(!n||n>(1ULL<<30))return 1;u64 words=kind?n*(BANK+2):n*FIELDS;*bytes=words*8;if(*bytes>budget)return 2;
 Source*s=new Source{};s->kind=kind;s->n=kind?n*Q:n;s->age=age;
 if(cudaMalloc(&s->values,n*(kind?BANK:FIELDS)*8)!=cudaSuccess){tt_source_free(s);return 3;}
 if(kind&&cudaMalloc(&s->signals,n*2*8)!=cudaSuccess){tt_source_free(s);return 3;}*out=s;return 0;
}
extern "C" int tt_raw(size_t n,const u64*values,u64 budget,Source**out,u64*bytes){int code=allocate_source(n,0,0,budget,out,bytes);if(code)return code;if(values&&cudaMemcpy((*out)->values,values,n*FIELDS*8,cudaMemcpyHostToDevice)!=cudaSuccess){tt_source_free(*out);*out=nullptr;return 4;}return 0;}
extern "C" int tt_initial(Source*input,u64 budget,Source**out,u64*bytes){if(!input||input->kind)return 1;int code=allocate_source(input->n,1,0,budget,out,bytes);if(code)return code;
 if(cudaMemset((*out)->values,0,input->n*BANK*8)!=cudaSuccess||cudaMemset((*out)->signals,0,input->n*2*8)!=cudaSuccess){tt_source_free(*out);*out=nullptr;return 4;}
 encode_initial<<<(input->n+127)/128,128>>>(*input,**out);return sync();
}
extern "C" void tt_free(Window*w){if(!w)return;cudaFree(w->raw);cudaFree(w->next);cudaFree(w->nextsignals);cudaFree(w->rom);cudaFree(w->code);cudaFree(w->status);delete w;}
extern "C" int tt_create(size_t capacity,u64 budget,Window**out,u64*bytes){if(!capacity||capacity>(1u<<20))return 1;*bytes=8*((capacity+14)*FIELDS+capacity*(BANK+2)+Q*7+INSTRUCTIONS*4)+4*(capacity+14);if(*bytes>budget)return 2;
 Window*w=new Window{};w->capacity=capacity;w->n=capacity;
 #define ALLOC(member,count) if(cudaMalloc(&w->member,(count)*sizeof(*w->member))!=cudaSuccess){tt_free(w);return 3;}
 ALLOC(raw,(capacity+14)*FIELDS) ALLOC(next,capacity*BANK) ALLOC(nextsignals,capacity*2) ALLOC(rom,Q*7) ALLOC(code,INSTRUCTIONS*4) ALLOC(status,capacity+14)
 #undef ALLOC
 if(cudaMemcpy(w->rom,ROM_INIT,sizeof(ROM_INIT),cudaMemcpyHostToDevice)!=cudaSuccess||cudaMemcpy(w->code,CODE_INIT,sizeof(CODE_INIT),cudaMemcpyHostToDevice)!=cudaSuccess){tt_free(w);return 4;}*out=w;return 0;
}
extern "C" int tt_evaluate(Window*w,Source*s,u64 start,size_t n,int committed){if(!w||!s||!n||n>w->capacity||start>=s->n||n>s->n-start)return 1;w->n=n;
 gather<<<(n+14+127)/128,128>>>(*s,*w,start);int code=status(w,n+14);if(code)return 10+code;
 terminal<<<(n+127)/128,128>>>(*w);code=status(w,n);if(code)return 20+code;
 if(committed){tile_commit<<<(n+127)/128,128>>>(*w);if(sync())return 30;}return 0;
}
extern "C" int tt_read(Window*w,u64*bank,u64*signals){if(!w)return 1;return cudaMemcpy(bank,w->next,w->n*BANK*8,cudaMemcpyDeviceToHost)!=cudaSuccess||cudaMemcpy(signals,w->nextsignals,w->n*2*8,cudaMemcpyDeviceToHost)!=cudaSuccess;}
extern "C" int tt_freeze(Window*w,u64 age,u64 budget,Source**out,u64*bytes){if(!w)return 1;int code=allocate_source(w->n,1,age,budget,out,bytes);if(code)return code;if(cudaMemcpy((*out)->values,w->next,w->n*BANK*8,cudaMemcpyDeviceToDevice)!=cudaSuccess||cudaMemcpy((*out)->signals,w->nextsignals,w->n*2*8,cudaMemcpyDeviceToDevice)!=cudaSuccess){tt_source_free(*out);*out=nullptr;return 4;}return 0;}
extern "C" int tt_cells(Window*w,Source*s,u64 start,size_t n,u64*out){if(!w||!s||!n||n>w->capacity+14)return 1;cells<<<(n+127)/128,128>>>(*s,*w,start,n,w->raw);return cudaMemcpy(out,w->raw,n*FIELDS*8,cudaMemcpyDeviceToHost)!=cudaSuccess;}
extern "C" int tt_collect(Window*w,Source*s,u64 start){if(!w||!s||s->kind||start>s->n||w->n>s->n-start)return 1;collect<<<(w->n+127)/128,128>>>(*w,*s,start);return sync();}
extern "C" int tt_decode(Window*w,Source*s,u64 budget,Source**out,u64*bytes){if(!w||!s||s->n%Q)return 1;int code=allocate_source(s->n/Q,0,0,budget,out,bytes);if(code)return code;decode<<<((s->n/Q)+127)/128,128>>>(*s,**out,*w);return sync();}
