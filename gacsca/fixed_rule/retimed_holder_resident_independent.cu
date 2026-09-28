/* Independent physical controller clocks between common causal barriers.
   Reuse the SAME generated local procedure and resident representation.
   No represented upper transition, instruction interpreter, or depth dispatch. */
#include "retimed_holder_resident_period.cu"

__device__ void independent_input(World w,size_t col,uint64_t a,const uint64_t *head,
                                  uint64_t head_at,uint64_t age,uint64_t *out){
 uint64_t pos=col*Q+a;const uint64_t*row=find(w,pos);
 for(unsigned k=0;k<7;++k)out[STATIC_FIELDS[k]*WORKERS]=meta(w,a,k);
 for(unsigned k=0;k<P_FIELDS;++k){uint64_t v=0;
  if(k==P_ADDRESS)v=a;
  else if(k==P_AGE)v=age;
  else if(k==P_DATA){int64_t b=bankrow(a);if(b>=0)v=w.data[col*BANK_ROWS+b];}
  else if(k==P_SIGNAL)v=row?get(row,P_SIGNAL):0;
  else if(a==head_at&&k>=P_HEAD&&k<P_LP_TARGET)v=head[k-P_HEAD];
  out[DYNAMIC_FIELDS[k]*WORKERS]=v;
 }
}

__device__ uint64_t independent_distance(World w,uint64_t a,const uint64_t*h){
 const unsigned H=P_HEAD;
 if(h[P_DIRECTION-H])return a;
 if(h[P_PHASE-H]==0&&meta(w,a,0)==10&&meta(w,a,1)==h[P_PC-H]&&h[P_RD-H])return h[P_RD-H];
 uint64_t target=ROM_ROWS-1,x=UINT64_MAX,phase=h[P_PHASE-H];
 if(phase==0&&h[P_PC-H]<ROM_ROWS-MEM_ROWS-1)x=MEM_ROWS+h[P_PC-H];
 else if((phase==1||phase==4||phase==5)&&h[P_RA-H]<MEM_ROWS)x=h[P_RA-H];
 else if(phase==2&&h[P_RB-H]<MEM_ROWS)x=h[P_RB-H];
 else if(phase==3&&h[P_RD-H]<MEM_ROWS)x=h[P_RD-H];
 else if(phase==6&&h[P_VALUE-H]&&h[P_RD-H]<ROM_ROWS)x=h[P_RD-H];
 if(x>=a&&x<target)target=x;
 return target-a;
}

__global__ void independent_run(World w,uint64_t ticks,uint64_t event_budget){
 size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
 uint64_t *in=w.work+worker,*out=in+11*FIELDS*WORKERS,*tmp=out+FIELDS*WORKERS;
 for(size_t col=worker;col<w.colonies;col+=WORKERS){
  uint64_t h[P_LP_TARGET-P_HEAD]={0},where=0,heads=0,elapsed=0,events=0,evaluations=0;
  bool bad=!signal_shape(w,col,w.age>=PREFIX_LIMIT);
  w.status[3*col]=w.status[3*col+1]=w.status[3*col+2]=0;
  for(size_t i=0;i<w.counts[col];++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;
   for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)bad|=get(row,k)!=0;
   if(get(row,P_HEAD)){++heads;where=get(row,P_ADDRESS);bad|=where>=ROM_ROWS;
    for(unsigned k=P_HEAD;k<P_LP_TARGET;++k)h[k-P_HEAD]=get(row,k);
   }else for(unsigned k=P_PHASE;k<P_LP_TARGET;++k)bad|=get(row,k)!=0;
  }
  bad|=heads>1;
  while(!bad&&elapsed<ticks&&h[0]){
   uint64_t jump=independent_distance(w,where,h),remaining=ticks-elapsed;
   if(jump>remaining)jump=remaining;
   if(jump){
    bool wait=!h[P_DIRECTION-P_HEAD]&&h[P_PHASE-P_HEAD]==0&&meta(w,where,0)==10&&meta(w,where,1)==h[P_PC-P_HEAD]&&h[P_RD-P_HEAD]>0;
    if(wait)h[P_RD-P_HEAD]-=jump;
    else if(h[P_DIRECTION-P_HEAD])where-=jump;
    else where+=jump;
    elapsed+=jump;continue;
   }
   if(events>=event_budget){bad=true;break;}
   uint64_t next[P_LP_TARGET-P_HEAD]={0},next_at=0,next_heads=0;
   uint64_t data[3]={0},points[3]={0};unsigned used=0;
   for(int delta=-1;delta<=1&&!bad;++delta){
    int64_t a=(int64_t)where+delta;
    // Canonical first/last reflect the only head inside the ROM core.
    if(a<0||a>=(int64_t)ROM_ROWS)continue;
    for(int j=-5;j<=5;++j){int64_t neighbor=a+j;size_t source_col=col;
     if(neighbor<0){neighbor+=Q;source_col=col?col-1:w.colonies-1;}
     // ROM_ROWS+5 < Q: no right-colony mutable Data can be read.
     independent_input(w,source_col,(uint64_t)neighbor,h,source_col==col?where:UINT64_MAX,w.age+elapsed,in+(j+5)*FIELDS*WORKERS);
    }
    resident_prefix_local(in,out,tmp);++evaluations;
    for(unsigned k=LP_TARGET;k<ADDRESS;++k)bad|=out[k*WORKERS]!=0;
    if(out[HEAD*WORKERS]){++next_heads;next_at=(uint64_t)a;
     for(unsigned k=P_HEAD;k<P_LP_TARGET;++k)next[k-P_HEAD]=out[DYNAMIC_FIELDS[k]*WORKERS];
    }else for(unsigned k=P_PHASE;k<P_LP_TARGET;++k)bad|=out[DYNAMIC_FIELDS[k]*WORKERS]!=0;
    points[used]=(uint64_t)a;data[used++]=out[DATA*WORKERS];
   }
   bad|=next_heads>1;
   if(bad)break;
   for(unsigned i=0;i<used;++i){int64_t b=bankrow(points[i]);if(b>=0)w.data[col*BANK_ROWS+b]=data[i];else if(data[i])bad=true;}
   for(unsigned k=0;k<P_LP_TARGET-P_HEAD;++k)h[k]=next[k];
   where=next_at;++events;++elapsed;
  }
  size_t count=0;
  if(!bad){
   // Stationary Signal holders retain their actual locations and values.
   for(size_t i=0;i<w.counts[col];++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;
    uint64_t signal=get(row,P_SIGNAL);if(signal){uint64_t*target=destination(w,col,get(row,P_ADDRESS),&count);if(!target){bad=true;break;}put(target,P_SIGNAL,signal);}
   }
   if(h[0]&&!bad){uint64_t*target=destination(w,col,where,&count);if(!target)bad=true;
    else for(unsigned k=P_HEAD;k<P_LP_TARGET;++k)put(target,k,h[k-P_HEAD]);}
  }
  w.status[3*col]=events;w.status[3*col+1]=count;w.status[3*col+2]|=bad;
  w.candidates[col*CANDIDATES]=evaluations;
 }
}

extern "C" int ri_run(void*handle,uint64_t ticks,uint64_t event_budget,uint64_t budget,uint64_t*metrics){
 World*w=(World*)handle;
 if(!w||!ticks||!event_budget||bulk_age(w->age)||!active_age(w->age)||ticks>boundary_distance(w->age)||ROM_ROWS+5>=Q)return -1;
 if(w->colonies*BANK_ROWS*8>budget)return -2;
 int guard=domain(w);if(guard)return guard;
 World staged=*w;staged.data=nullptr;cudaError_t e=alloc(&staged.data,w->colonies*BANK_ROWS);
 if(e==cudaSuccess)e=cudaMemcpy(staged.data,w->data,w->colonies*BANK_ROWS*8,cudaMemcpyDeviceToDevice);
 if(e==cudaSuccess){independent_run<<<WORKERS/32,32>>>(staged,ticks,event_budget);e=cudaGetLastError();}
 uint64_t*status=(uint64_t*)malloc(w->colonies*4*8);if(!status){cudaFree(staged.data);return -3;}
 if(e==cudaSuccess)e=cudaMemcpy(status,w->status,w->colonies*3*8,cudaMemcpyDeviceToHost);
 if(e==cudaSuccess)e=cudaMemcpy2D(status+3*w->colonies,8,w->candidates,CANDIDATES*8,8,w->colonies,cudaMemcpyDeviceToHost);
 bool bad=false;metrics[0]=metrics[1]=metrics[2]=metrics[3]=0;
 for(size_t col=0;e==cudaSuccess&&col<w->colonies;++col){bad|=status[3*col+2]!=0;metrics[0]+=status[3*col];metrics[3]+=status[3*w->colonies+col];if(status[3*col]>metrics[1])metrics[1]=status[3*col];}
 free(status);
 if(e!=cudaSuccess||bad){cudaFree(staged.data);return e!=cudaSuccess?(int)e:-4;}
 commit_counts<<<(unsigned)((w->colonies+127)/128),128>>>(*w);e=cudaGetLastError();
 if(e==cudaSuccess)e=cudaDeviceSynchronize();
 if(e!=cudaSuccess){cudaFree(staged.data);return (int)e;}
 uint64_t*old=w->data;w->data=staged.data;cudaFree(old);
 old=w->rows;w->rows=w->nextrows;w->nextrows=old;
 w->age+=ticks;metrics[2]=w->colonies*BANK_ROWS*8;
 return 0;
}
