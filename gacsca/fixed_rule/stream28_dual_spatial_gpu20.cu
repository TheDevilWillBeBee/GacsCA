/* Literal radius-one spatial successor of the fixed dual-pass own-rule.
   Static gates/routes are retained in encoded physical rows on device. */
#include <cuda_runtime.h>
#include <cstdint>
#include <cstdlib>
#include <utility>
using u64=uint64_t;
constexpr unsigned Q=8192,FIELDS=267,GATES=3,ROUTES=38,PERIOD=65536;
constexpr unsigned GATE0=6,ROUTE0=GATE0+GATES*7,DYNAMIC=ROUTE0+ROUTES*6;
static_assert(DYNAMIC==255);
struct Packet {u64 valid,target,arg,gate,value;};
struct Dyn {u64 active,source,arg0,arg1,ready,result,done,collision;Packet mail;};
static_assert(sizeof(Dyn)==13*sizeof(u64));
struct World {size_t n;u64 age,*static_rows,*events,*values,*counts;Dyn *a,*b;};

__device__ __forceinline__ u64 fld(const u64*rows,size_t i,unsigned k){
 return rows[i*FIELDS+k];
}
__device__ __forceinline__ bool marked(u64 op){
 return op==0||op==7||op==8||op==9||op==10||op==12||op==13;
}
__device__ __forceinline__ u64 base(u64 op){
 return op==0?1:op==7?2:op==8?3:op==9?4:op==10?5:op==12?11:op==13?14:op;
}
__device__ __forceinline__ u64 arithmetic(u64 op,u64 a,u64 b){
 switch(op){
 case 1:return ~(a&b);
 case 2:return a+b;
 case 3:return b<64?a>>b:0;
 case 4:return a==b;
 case 5:return a<b;
 case 6:case 14:return a&b;
 default:return 0;
 }
}

__global__ void initialize(World w){
 size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=w.n)return;
 Dyn d{};d.active=fld(w.static_rows,i,3);
 d.source=fld(w.static_rows,i,DYNAMIC);
 d.arg0=fld(w.static_rows,i,DYNAMIC+1);
 d.arg1=fld(w.static_rows,i,DYNAMIC+2);
 d.ready=fld(w.static_rows,i,DYNAMIC+3);
 d.result=fld(w.static_rows,i,DYNAMIC+4);
 d.done=fld(w.static_rows,i,DYNAMIC+5);
 d.mail={fld(w.static_rows,i,DYNAMIC+6),fld(w.static_rows,i,DYNAMIC+7),
         fld(w.static_rows,i,DYNAMIC+8),fld(w.static_rows,i,DYNAMIC+9),
         fld(w.static_rows,i,DYNAMIC+10)};
 d.collision=fld(w.static_rows,i,DYNAMIC+11);
 w.a[i]=d;
}

__global__ void advance(World w,const Dyn*old,Dyn*next,u64 age){
 size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=w.n)return;
 Dyn d=old[i];const u64*st=w.static_rows;
 u64 address=fld(st,i,0),kind=fld(st,i,2);
 if(kind==3&&age==0){d.source=0;d.done=0;}
 if(kind==2&&age==0){
  d.source=0;d.active=0;
  d.arg0=fld(st,i,GATE0+4);d.arg1=fld(st,i,GATE0+5);
  d.ready=fld(st,i,GATE0+6);d.result=0;d.done=0;
 }else if(kind==2&&d.active<2){
  u64 when=fld(st,i,4+(unsigned)d.active);
  if(when&&when==age){
   unsigned next_slot=(unsigned)d.active+1;
   unsigned spec=GATE0+7*next_slot;
   if(!fld(st,i,spec))d.collision=1;
   else{
    d.active=next_slot;d.arg0=fld(st,i,spec+4);
    d.arg1=fld(st,i,spec+5);d.ready=fld(st,i,spec+6);
    d.result=0;d.done=0;
   }
  }
 }
 u64 compute_ready=d.ready;
 Packet left=old[i?i-1:w.n-1].mail;
 Packet right=old[i+1<w.n?i+1:0].mail;
 bool from_left=left.valid&&left.gate!=3;
 bool from_right=right.valid&&right.gate==3;
 if(from_left&&from_right)d.collision=1;
 Packet packet=from_left?left:from_right?right:Packet{};
 if(packet.valid&&kind==2&&packet.target==address){
  if(packet.gate==d.active){
   u64 bit=u64(1)<<packet.arg;
   u64 old_arg=packet.arg?d.arg1:d.arg0;
   if((d.ready&bit)&&old_arg!=packet.value)d.collision=1;
   if(packet.arg)d.arg1=packet.value;else d.arg0=packet.value;
   d.ready|=bit;packet={};
   atomicAdd((unsigned long long*)w.counts,1ULL);
  }
 }else if(packet.valid&&kind==3&&packet.target==address){
  if(d.done&&d.source!=packet.value)d.collision=1;
  d.source=packet.value;d.done=1;
  w.events[i]=age;w.values[i]=packet.value;
  packet={};atomicAdd((unsigned long long*)w.counts,1ULL);
 }
 Packet emitted{};
 if(kind==1||kind==2){
  for(unsigned route=0;route<ROUTES;++route){
   unsigned offset=ROUTE0+route*6;
   if(!fld(st,i,offset)||fld(st,i,offset+5)!=age)continue;
   u64 value=0,source_slot=fld(st,i,offset+4);
   if(kind==1)value=old[i].source;
   else if(fld(st,i,offset+3)==3&&
           marked(fld(st,i,GATE0+7*source_slot+1)))value=old[i].source;
   else if(source_slot==d.active&&d.done)value=d.result;
   else{d.collision=1;continue;}
   if(emitted.valid)d.collision=1;
   else emitted={1,fld(st,i,offset+1),fld(st,i,offset+2),
                 fld(st,i,offset+3),value};
  }
 }
 if(packet.valid&&emitted.valid)d.collision=1;
 d.mail=packet.valid?packet:emitted;
 if(kind==2&&!d.done){
  unsigned spec=GATE0+7*(unsigned)d.active;
  if(fld(st,i,spec)){
   u64 encoded=fld(st,i,spec+1),op=base(encoded);
   if(op==11){d.result=fld(st,i,spec+2);d.done=1;}
   else if(compute_ready==3){
    d.result=arithmetic(op,d.arg0,d.arg1);d.done=1;
   }
   if(d.done){
    atomicAdd((unsigned long long*)(w.counts+1),1ULL);
    if(marked(encoded))d.source=d.result;
   }
  }
 }
 next[i]=d;
}

extern "C" void se_free(World*w){
 if(!w)return;
 cudaFree(w->static_rows);cudaFree(w->a);cudaFree(w->b);
 cudaFree(w->events);cudaFree(w->values);cudaFree(w->counts);
 free(w);
}
extern "C" int se_create(size_t n,const u64*rows,u64 budget,
                           World**out,u64*bytes){
 if(!out||!bytes||!rows||n<3||n>(1u<<24))return 1;
 *out=nullptr;
 *bytes=n*(FIELDS*8+2*sizeof(Dyn)+16)+16;
 if(*bytes>budget)return 2;
 World*w=(World*)calloc(1,sizeof(World));if(!w)return 3;
 w->n=n;w->age=rows[1];
 #define ALLOC(name,count) if(cudaMalloc(&w->name,(count))!=cudaSuccess){se_free(w);return 4;}
 ALLOC(static_rows,n*FIELDS*8) ALLOC(a,n*sizeof(Dyn)) ALLOC(b,n*sizeof(Dyn))
 ALLOC(events,n*8) ALLOC(values,n*8) ALLOC(counts,16)
 #undef ALLOC
 cudaError_t e=cudaMemcpy(w->static_rows,rows,n*FIELDS*8,cudaMemcpyHostToDevice);
 if(e==cudaSuccess)e=cudaMemset(w->events,0,n*8);
 if(e==cudaSuccess)e=cudaMemset(w->values,0,n*8);
 if(e==cudaSuccess)e=cudaMemset(w->counts,0,16);
 if(e==cudaSuccess){initialize<<<(unsigned)((n+127)/128),128>>>(*w);e=cudaGetLastError();}
 if(e==cudaSuccess)e=cudaDeviceSynchronize();
 if(e!=cudaSuccess){se_free(w);return 5;}
 *out=w;return 0;
}
extern "C" int se_run(World*w,u64 ticks){
 if(!w||ticks>PERIOD)return 1;
 for(u64 t=0;t<ticks;++t){
  u64 next_age=(w->age+1)&(PERIOD-1);
  advance<<<(unsigned)((w->n+127)/128),128>>>(*w,w->a,w->b,next_age);
  if(cudaGetLastError()!=cudaSuccess)return 2;
  std::swap(w->a,w->b);w->age=next_age;
 }
 return cudaDeviceSynchronize()==cudaSuccess?0:3;
}
extern "C" int se_read(World*w,u64*dyn,u64*events,u64*values,u64*counts){
 if(!w||!dyn||!events||!values||!counts)return 1;
 cudaError_t e=cudaMemcpy(dyn,w->a,w->n*sizeof(Dyn),cudaMemcpyDeviceToHost);
 if(e==cudaSuccess)e=cudaMemcpy(events,w->events,w->n*8,cudaMemcpyDeviceToHost);
 if(e==cudaSuccess)e=cudaMemcpy(values,w->values,w->n*8,cudaMemcpyDeviceToHost);
 if(e==cudaSuccess)e=cudaMemcpy(counts,w->counts,16,cudaMemcpyDeviceToHost);
 return e==cudaSuccess?0:2;
}
