/* Physical gather acceleration: controller events plus actual ballistic mail.
   No upper transition. Source Info is read at each real TRANSMIT event.
   Only protected foreign-history/Signal-buffer deliveries may be deferred; any controller
   access there rejects the entire staged batch. */
#include "compact16_holder_resident_independent.cu"
#define PACKETS 32
struct Packet {uint64_t birth,address,track,target,data,remaining;};
__device__ bool protected_target(uint64_t a){return a<Q&&PROTECTED[a];}

__device__ bool add_packet(Packet*packets,uint64_t*count,size_t col,uint64_t birth,uint64_t a,unsigned track,const uint64_t*words){
 if(!words[3])return !(words[0]||words[1]||words[2]);
 if(!protected_target(words[0])||*count>=PACKETS)return false;
 packets[col*PACKETS+(*count)++]={birth,a,track,words[0],words[1],words[2]};return true;
}
__device__ bool protected_access(World w,uint64_t a,const uint64_t*h){
 if(!protected_target(a)||h[P_DIRECTION-P_HEAD]||meta(w,a,0)!=0)return false;
 uint64_t phase=h[P_PHASE-P_HEAD];
 return ((phase==1||phase==4||phase==5)&&h[P_RA-P_HEAD]==a)||
        (phase==2&&h[P_RB-P_HEAD]==a)||(phase==3&&h[P_RD-P_HEAD]==a);
}
__global__ void gather_heads(World w,uint64_t ticks,uint64_t event_budget,Packet*packets,uint64_t*packet_counts){
 size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
 uint64_t*in=w.work+worker,*out=in+11*FIELDS*WORKERS,*tmp=out+FIELDS*WORKERS;
 for(size_t col=worker;col<w.colonies;col+=WORKERS){
  uint64_t h[P_LP_TARGET-P_HEAD]={0},where=0,heads=0,elapsed=0,events=0,evaluations=0,pc=0;
  bool bad=!signal_shape(w,col,false);
  w.status[3*col]=w.status[3*col+1]=w.status[3*col+2]=0;
  for(size_t i=0;i<w.counts[col];++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;uint64_t a=get(row,P_ADDRESS);
   for(unsigned track=P_LP_TARGET;track<=P_RP_TARGET;track+=4){uint64_t words[4];for(unsigned k=0;k<4;++k)words[k]=get(row,track+k);bad|=!add_packet(packets,&pc,col,0,a,track,words);}
   if(get(row,P_HEAD)){++heads;where=a;bad|=a>=ROM_ROWS;for(unsigned k=P_HEAD;k<P_LP_TARGET;++k)h[k-P_HEAD]=get(row,k);}
   else for(unsigned k=P_PHASE;k<P_LP_TARGET;++k)bad|=get(row,k)!=0;
  }
  bad|=heads>1;
  while(!bad&&elapsed<ticks&&h[0]){
   uint64_t jump=independent_distance(w,where,h);if(jump>ticks-elapsed)jump=ticks-elapsed;
   if(jump){
    bool wait=!h[P_DIRECTION-P_HEAD]&&h[P_PHASE-P_HEAD]==0&&meta(w,where,0)==10&&meta(w,where,1)==h[P_PC-P_HEAD]&&h[P_RD-P_HEAD]>0;
    if(wait)h[P_RD-P_HEAD]-=jump;else if(h[P_DIRECTION-P_HEAD])where-=jump;else where+=jump;
    elapsed+=jump;continue;
   }
   if(events>=event_budget||protected_access(w,where,h)){bad=true;break;}
   uint64_t next[P_LP_TARGET-P_HEAD]={0},next_at=0,next_heads=0,data[3]={0},points[3]={0};unsigned used=0;
   for(int delta=-1;delta<=1&&!bad;++delta){int64_t a=(int64_t)where+delta;if(a<0||a>=(int64_t)ROM_ROWS)continue;
    for(int j=-5;j<=5;++j){int64_t neighbor=a+j;size_t source_col=col;
     if(neighbor<0){neighbor+=Q;source_col=col?col-1:w.colonies-1;}
     independent_input(w,source_col,(uint64_t)neighbor,h,source_col==col?where:UINT64_MAX,w.age+elapsed,in+(j+5)*FIELDS*WORKERS);
    }
    resident_prefix_local(in,out,tmp);++evaluations;
    for(unsigned track=P_LP_TARGET;track<=P_RP_TARGET;track+=4){uint64_t words[4];for(unsigned k=0;k<4;++k)words[k]=out[DYNAMIC_FIELDS[track+k]*WORKERS];bad|=!add_packet(packets,&pc,col,elapsed+1,(uint64_t)a,track,words);}
    if(out[HEAD*WORKERS]){++next_heads;next_at=(uint64_t)a;for(unsigned k=P_HEAD;k<P_LP_TARGET;++k)next[k-P_HEAD]=out[DYNAMIC_FIELDS[k]*WORKERS];}
    else for(unsigned k=P_PHASE;k<P_LP_TARGET;++k)bad|=out[DYNAMIC_FIELDS[k]*WORKERS]!=0;
    points[used]=(uint64_t)a;data[used++]=out[DATA*WORKERS];
   }
   bad|=next_heads>1;if(bad)break;
   for(unsigned i=0;i<used;++i){int64_t b=bankrow(points[i]);if(b>=0)w.data[col*BANK_ROWS+b]=data[i];else if(data[i])bad=true;}
   for(unsigned k=0;k<P_LP_TARGET-P_HEAD;++k)h[k]=next[k];where=next_at;++events;++elapsed;
  }
  size_t count=0;
  if(!bad){
   for(size_t i=0;i<w.counts[col];++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;uint64_t signal=get(row,P_SIGNAL);
    if(signal){uint64_t*target=destination(w,col,get(row,P_ADDRESS),&count);if(!target){bad=true;break;}put(target,P_SIGNAL,signal);}
   }
   if(h[0]&&!bad){uint64_t*target=destination(w,col,where,&count);if(!target)bad=true;else for(unsigned k=P_HEAD;k<P_LP_TARGET;++k)put(target,k,h[k-P_HEAD]);}
  }
  packet_counts[col]=pc;w.status[3*col]=events;w.status[3*col+1]=count;w.status[3*col+2]|=bad;w.candidates[col*CANDIDATES]=evaluations;
 }
}
__device__ uint64_t arrival(Packet p){
 int64_t d=(int64_t)(p.remaining*Q)+(p.track==P_LP_TARGET?(int64_t)p.address-(int64_t)p.target:(int64_t)p.target-(int64_t)p.address);
 return d>0?(uint64_t)d:UINT64_MAX;
}
__device__ uint64_t lifetime(Packet p){uint64_t drop=p.remaining*Q+(p.track==P_LP_TARGET?p.address+1:Q-p.address),hit=arrival(p);return hit<drop?hit:drop;}
__device__ uint64_t phase(Packet p,size_t source,uint64_t size){int64_t x=(int64_t)(source*Q+p.address)+(p.track==P_LP_TARGET?(int64_t)p.birth:-(int64_t)p.birth);x%=(int64_t)size;return x<0?(uint64_t)(x+(int64_t)size):(uint64_t)x;}
__device__ size_t colony_shift(size_t source,int64_t d,size_t n){int64_t x=((int64_t)source+d)%(int64_t)n;return x<0?(size_t)(x+(int64_t)n):(size_t)x;}
__device__ bool delivered(Packet p,size_t source,size_t dest,size_t n,uint64_t ticks){return p.birth+arrival(p)>=p.birth&&arrival(p)<=ticks-p.birth&&colony_shift(source,p.track==P_LP_TARGET?-(int64_t)p.remaining:(int64_t)p.remaining,n)==dest;}
__global__ void gather_mail(World w,uint64_t ticks,const Packet*packets,const uint64_t*counts){
 size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.colonies||w.status[3*col+2])return;
 size_t span=w.colonies<15?w.colonies:15,first=colony_shift(col,-7,w.colonies);bool bad=false;size_t count=w.status[3*col+1];
 // Same-track ballistic world-lines collide only when an extant packet is
 // overwritten by a later birth. Check before publishing any staged state.
 for(size_t i=0;i<counts[col];++i){Packet a=packets[col*PACKETS+i];
  for(size_t s=0;s<span;++s){size_t source=(first+s)%w.colonies;
   for(size_t j=0;j<counts[source];++j){if(source==col&&j==i)continue;Packet b=packets[source*PACKETS+j];
    if(a.track==b.track&&a.birth>=b.birth&&a.birth<b.birth+lifetime(b)&&phase(a,col,w.colonies*Q)==phase(b,source,w.colonies*Q))bad=true;
   }
  }
 }
 for(size_t s=0;s<span;++s){size_t source=(first+s)%w.colonies;
  for(size_t i=0;i<counts[source];++i){Packet a=packets[source*PACKETS+i];uint64_t elapsed=ticks-a.birth;
   if(delivered(a,source,col,w.colonies,ticks)){
    bool winner=true;uint64_t time=a.birth+arrival(a);
    for(size_t t=0;t<span&&winner;++t){size_t other=(first+t)%w.colonies;
     for(size_t j=0;j<counts[other];++j){Packet b=packets[other*PACKETS+j];if(b.target!=a.target||!delivered(b,other,col,w.colonies,ticks))continue;
      uint64_t when=b.birth+arrival(b);if(when>time||(when==time&&b.track==P_RP_TARGET&&a.track==P_LP_TARGET)){winner=false;break;}
     }
    }
    if(winner){int64_t b=bankrow(a.target);if(b<0)bad=true;else w.data[col*BANK_ROWS+b]=a.data;}
   }
   if(elapsed<lifetime(a)){
    int64_t moved=(int64_t)(source*Q+a.address)+(a.track==P_LP_TARGET?-(int64_t)elapsed:(int64_t)elapsed);
    moved%=(int64_t)(w.colonies*Q);if(moved<0)moved+=(int64_t)(w.colonies*Q);
    if((uint64_t)moved/Q==col){uint64_t*row=destination(w,col,(uint64_t)moved%Q,&count);if(!row){bad=true;continue;}
     if(get(row,(unsigned)a.track+3)){bad=true;continue;}
     uint64_t crossed=a.track==P_LP_TARGET?(elapsed+Q-1-a.address)/Q:(elapsed+a.address)/Q;
     put(row,(unsigned)a.track,a.target);put(row,(unsigned)a.track+1,a.data);put(row,(unsigned)a.track+2,a.remaining-crossed);put(row,(unsigned)a.track+3,1);
    }
   }
  }
 }
 w.status[3*col+1]=count;w.status[3*col+2]|=bad;
}
extern "C" int rg_run(void*handle,uint64_t ticks,uint64_t event_budget,uint64_t budget,uint64_t*metrics){
 World*w=(World*)handle;
 if(!w||!ticks||ticks>8*Q||!event_budget||w->age>=CAPTURE-1||bulk_age(w->age)||!active_age(w->age)||ticks>boundary_distance(w->age))return -1;
 uint64_t extra=w->colonies*(BANK_ROWS*8+PACKETS*sizeof(Packet)+8);if(extra>budget)return -2;
 World staged=*w;staged.data=nullptr;Packet*packets=nullptr;uint64_t*counts=nullptr;
 cudaError_t e=alloc(&staged.data,w->colonies*BANK_ROWS);
 if(e==cudaSuccess)e=cudaMalloc(&packets,w->colonies*PACKETS*sizeof(Packet));if(e==cudaSuccess)e=alloc(&counts,w->colonies);
 if(e==cudaSuccess)e=cudaMemcpy(staged.data,w->data,w->colonies*BANK_ROWS*8,cudaMemcpyDeviceToDevice);
 if(e==cudaSuccess){gather_heads<<<WORKERS/32,32>>>(staged,ticks,event_budget,packets,counts);e=cudaGetLastError();}
 if(e==cudaSuccess){gather_mail<<<(unsigned)((w->colonies+127)/128),128>>>(staged,ticks,packets,counts);e=cudaGetLastError();}
 uint64_t*status=(uint64_t*)malloc(w->colonies*4*8);if(!status){cudaFree(staged.data);cudaFree(packets);cudaFree(counts);return -3;}
 if(e==cudaSuccess)e=cudaMemcpy(status,w->status,w->colonies*3*8,cudaMemcpyDeviceToHost);
 if(e==cudaSuccess)e=cudaMemcpy2D(status+3*w->colonies,8,w->candidates,CANDIDATES*8,8,w->colonies,cudaMemcpyDeviceToHost);
 bool bad=false;metrics[0]=metrics[1]=metrics[2]=metrics[3]=0;
 for(size_t col=0;e==cudaSuccess&&col<w->colonies;++col){bad|=status[3*col+2]!=0;metrics[0]+=status[3*col];metrics[3]+=status[3*w->colonies+col];if(status[3*col]>metrics[1])metrics[1]=status[3*col];}
 free(status);cudaFree(packets);cudaFree(counts);
 if(e!=cudaSuccess||bad){cudaFree(staged.data);return e!=cudaSuccess?(int)e:-4;}
 commit_counts<<<(unsigned)((w->colonies+127)/128),128>>>(*w);e=cudaGetLastError();if(e==cudaSuccess)e=cudaDeviceSynchronize();
 if(e!=cudaSuccess){cudaFree(staged.data);return (int)e;}
 uint64_t*old=w->data;w->data=staged.data;cudaFree(old);old=w->rows;w->rows=w->nextrows;w->nextrows=old;
 w->age+=ticks;metrics[2]=extra;return 0;
}
