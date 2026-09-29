#include <cuda_runtime.h>
#include <stdint.h>
#include <stdlib.h>
#include "small_holder_resident_period_generated.h"
struct World{uint64_t *data,*rows,*nextrows,*counts,*candidates,*outputs,*status,*rom,*work,*stage,*readpos,*readout;size_t colonies;uint64_t age;};
__device__ uint64_t get(const uint64_t*r,unsigned field){unsigned o=FIELD_OFFSETS[field],width=FIELD_WIDTHS[field],word=o/64,s=o%64;uint64_t v=r[word]>>s;if(s+width>64)v|=r[word+1]<<(64-s);return width==64?v:v&((UINT64_C(1)<<width)-1);}
__device__ void put(uint64_t*r,unsigned field,uint64_t v){unsigned o=FIELD_OFFSETS[field],width=FIELD_WIDTHS[field],word=o/64,s=o%64;if(width<64)v&=(UINT64_C(1)<<width)-1;r[word]|=v<<s;if(s+width>64)r[word+1]|=v>>(64-s);}
__device__ int64_t bankrow(uint64_t a){return a<MEM_ROWS?(int64_t)a:a>=Q-5?(int64_t)(MEM_ROWS+a-(Q-5)):-1;}
__device__ uint64_t wrap(int64_t p,uint64_t n){return p<0?(uint64_t)(p+(int64_t)n):(uint64_t)p>=n?(uint64_t)p-n:(uint64_t)p;}
__device__ const uint64_t* find(World w,uint64_t pos){size_t col=pos/Q;uint64_t a=pos%Q,lo=0,hi=w.counts[col];const uint64_t*rows=w.rows+col*SLOTS*PACKED_WORDS;while(lo<hi){size_t m=lo+(hi-lo)/2;if(get(rows+m*PACKED_WORDS,P_ADDRESS)<a)lo=m+1;else hi=m;}return lo<w.counts[col]&&get(rows+lo*PACKED_WORDS,P_ADDRESS)==a?rows+lo*PACKED_WORDS:nullptr;}
__device__ uint64_t dyn(World w,uint64_t pos,const uint64_t*row,unsigned field){uint64_t a=pos%Q;if(field==P_ADDRESS)return a;if(field==P_AGE)return w.age;if(field==P_F1||field==P_F2||field==P_WF1||field==P_WF2)return 0;if(field==P_DATA){int64_t b=bankrow(a);return b<0?0:w.data[(pos/Q)*BANK_ROWS+b];}return row?get(row,field):0;}
__device__ uint64_t sig(World w,uint64_t pos){const uint64_t*row=find(w,pos);return row?get(row,P_SIGNAL):0;}
__device__ uint64_t signal_pattern(uint64_t a,uint64_t left,uint64_t right){return a>=1&&a<=5?left<<(5-a):a>=Q-5?right<<(Q-1-a):0;}
__device__ bool signal_shape(World w,size_t col,bool suffix){uint64_t left=(sig(w,col*Q+3)>>2)&1,right=(sig(w,col*Q+Q-3)>>2)&1;
 if(suffix&&(left||right!=((sig(w,Q-3)>>2)&1)))return false;
 for(size_t i=0;i<w.counts[col];++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;uint64_t a=get(row,P_ADDRESS);if(get(row,P_SIGNAL)!=signal_pattern(a,left,right))return false;if(suffix)for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)if(get(row,k))return false;}
 for(uint64_t a=1;a<=5;++a)if(sig(w,col*Q+a)!=signal_pattern(a,left,right))return false;
 for(uint64_t a=Q-5;a<Q;++a)if(sig(w,col*Q+a)!=signal_pattern(a,left,right))return false;
 return true;
}
__device__ uint64_t physical_flag(World w,uint64_t pos,unsigned field){if(w.age<PREFIX_LIMIT)return 0;uint64_t a=pos%Q,right=(sig(w,(pos/Q)*Q+Q-3)>>2)&1;if(!right)return 0;if(field==P_WF1)return w.age>=WF_START&&w.age<WF_END&&a>=Q-5;if(field!=P_F1||w.age<=WF_START)return 0;
 if(w.age<=WF_END){uint64_t moved=3*(w.age-WF_START-1),lo=moved>=Q-8?0:Q-8-moved;return a>=lo;}
 uint64_t moved=2*(w.age-WF_END),hi=moved>=Q?0:Q-moved;return a<hi;
}
__global__ void domain_check(World w){size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col<w.colonies)w.status[3*col+2]=(w.age>=PREFIX_LIMIT&&!signal_shape(w,col,true));}
static int domain(World*w){if(w->age<PREFIX_LIMIT)return 0;domain_check<<<(unsigned)((w->colonies+127)/128),128>>>(*w);cudaError_t e=cudaGetLastError();uint64_t*status=(uint64_t*)malloc(w->colonies*3*8);if(!status)return -3;if(e==cudaSuccess)e=cudaMemcpy(status,w->status,w->colonies*3*8,cudaMemcpyDeviceToHost);bool bad=false;for(size_t i=0;e==cudaSuccess&&i<w->colonies;++i)bad|=status[3*i+2]!=0;free(status);return e!=cudaSuccess?(int)e:bad?-5:0;}
__device__ void input(World w,uint64_t pos,uint64_t*out){uint64_t a=pos%Q;const uint64_t*row=find(w,pos);for(unsigned k=0;k<7;++k)out[STATIC_FIELDS[k]*WORKERS]=a<ROM_ROWS?w.rom[a*7+k]:k==0?(a>=Q-5?0:6):k==1?a:k==2&&a>=Q-5?31:0;for(unsigned k=0;k<P_FIELDS;++k)out[DYNAMIC_FIELDS[k]*WORKERS]=dyn(w,pos,row,k);}
__device__ bool active(const uint64_t*row){for(unsigned k=0;k<ACTIVE_FIELDS_COUNT;++k)if(get(row,ACTIVE_FIELDS[k]))return true;return false;}
__device__ void mark(World w,size_t col,uint64_t a){uint64_t*n=w.status+col*3,*list=w.candidates+col*CANDIDATES;size_t i=0;while(i<*n&&list[i]<a)++i;if(i<*n&&list[i]==a)return;if(*n>=CANDIDATES){n[2]=1;return;}for(size_t j=*n;j>i;--j)list[j]=list[j-1];list[i]=a;++*n;}
__global__ void prepare(World w){size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.colonies)return;w.status[3*col]=w.status[3*col+1]=w.status[3*col+2]=0;uint64_t size=w.colonies*Q;
 for(int dc=-1;dc<=1;++dc){size_t source=(size_t)wrap((int64_t)col+dc,w.colonies);for(size_t i=0;i<w.counts[source];++i){const uint64_t*row=w.rows+(source*SLOTS+i)*PACKED_WORDS;uint64_t p=source*Q+get(row,P_ADDRESS);for(int j=-5;j<=5;++j){uint64_t target=wrap((int64_t)p+j,size);if(target/Q==col)mark(w,col,target%Q);}}}
 if(w.age==0||w.age==RESET1||w.age==RESET2||w.age==VOTE0||w.age==WF_START||w.age==RESET4)mark(w,col,0);
 if(w.age==CAPTURE-1){for(uint64_t a=1;a<=5;++a)mark(w,col,a);for(uint64_t a=Q-5;a<Q;++a)mark(w,col,a);}
}
__global__ void evaluate(World w){size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;uint64_t*in=w.work+worker,*out=in+11*FIELDS*WORKERS,*tmp=out+FIELDS*WORKERS;
 for(size_t index=worker;index<w.colonies*CANDIDATES;index+=WORKERS){size_t col=index/CANDIDATES,i=index%CANDIDATES;if(i>=w.status[3*col]||w.status[3*col+2])continue;uint64_t pos=col*Q+w.candidates[index];for(int j=-5;j<=5;++j)input(w,wrap((int64_t)pos+j,w.colonies*Q),in+(j+5)*FIELDS*WORKERS);resident_prefix_local(in,out,tmp);uint64_t*target=w.outputs+index*PACKED_WORDS;for(unsigned k=0;k<PACKED_WORDS;++k)target[k]=0;for(unsigned k=0;k<P_FIELDS;++k)put(target,k,out[DYNAMIC_FIELDS[k]*WORKERS]);}
}
__global__ void validate(World w){size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.colonies||w.status[3*col+2])return;size_t count=0;for(size_t i=0;i<w.status[3*col];++i){const uint64_t*row=w.outputs+(col*CANDIDATES+i)*PACKED_WORDS;count+=active(row);if(w.age>=PREFIX_LIMIT)for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)if(get(row,k))w.status[3*col+2]=1;if(bankrow(get(row,P_ADDRESS))<0&&get(row,P_DATA))w.status[3*col+2]=1;}w.status[3*col+1]=count;if(count>SLOTS)w.status[3*col+2]=1;}
__global__ void bulk_data(World w){size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=w.colonies*BANK_ROWS)return;size_t col=i/BANK_ROWS,b=i%BANK_ROWS;uint64_t a=b<MEM_ROWS?b:Q-5+b-MEM_ROWS,mask=a<ROM_ROWS?w.rom[a*7+2]:31;
 if(w.age==PERIOD-1){if(a>0&&a<MEM_ROWS&&(mask&64))w.data[i]=w.data[i+1];return;}
 if((w.age==VOTE0||w.age==RESET4)&&a>0&&a<MEM_ROWS&&(mask&32)){uint64_t x=w.data[i-1],y=w.data[i+1],z=w.data[i+2];w.data[i]=(x&y)|(x&z)|(y&z);return;}
 if(w.age==VOTE0)return;
 int stage=w.age==0?0:w.age==RESET1?1:w.age==RESET2?2:w.age==WF_START?3:4;if(!a||((mask>>stage)&1))w.data[col*BANK_ROWS+b]=0;
}
__global__ void commit(World w){size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.colonies)return;size_t count=0;for(size_t i=0;i<w.status[3*col];++i){const uint64_t*row=w.outputs+(col*CANDIDATES+i)*PACKED_WORDS;int64_t b=bankrow(get(row,P_ADDRESS));if(b>=0)w.data[col*BANK_ROWS+b]=get(row,P_DATA);if(active(row)){uint64_t*target=w.nextrows+(col*SLOTS+count++)*PACKED_WORDS;for(unsigned k=0;k<PACKED_WORDS;++k)target[k]=row[k];}}w.counts[col]=count;}
__global__ void upload_info(World w,size_t first,size_t count){size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=count*INFO_WORDS)return;w.data[(first+i/INFO_WORDS)*BANK_ROWS+INFO_POSITIONS[i%INFO_WORDS]]=w.stage[i];}
__global__ void initial_data(World w,size_t first,size_t count){size_t col=first+(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col>=first+count)return;for(size_t i=0;i<w.counts[col];++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;int64_t b=bankrow(get(row,P_ADDRESS));if(b>=0)w.data[col*BANK_ROWS+b]=get(row,P_DATA);}}
__global__ void read_cells(World w,size_t count){size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=count)return;uint64_t pos=w.readpos[i],*out=w.readout+i*PACKED_WORDS;const uint64_t*row=find(w,pos);for(unsigned k=0;k<PACKED_WORDS;++k)out[k]=0;for(unsigned k=0;k<P_FIELDS;++k)put(out,k,(k==P_F1||k==P_F2||k==P_WF1||k==P_WF2)?physical_flag(w,pos,k):dyn(w,pos,row,k));}
extern "C" void rp_free(void*handle){World*w=(World*)handle;if(!w)return;cudaFree(w->data);cudaFree(w->rows);cudaFree(w->nextrows);cudaFree(w->counts);cudaFree(w->candidates);cudaFree(w->outputs);cudaFree(w->status);cudaFree(w->rom);cudaFree(w->work);cudaFree(w->stage);cudaFree(w->readpos);cudaFree(w->readout);free(w);}
static cudaError_t alloc(uint64_t**p,size_t n){return cudaMalloc(p,n*8);}
extern "C" int rp_create(size_t colonies,uint64_t age,uint64_t budget,const uint64_t*rom,void**handle,uint64_t*allocated){*handle=nullptr;if(!colonies||colonies>UINT64_C(1)<<20||age>=PREFIX_LIMIT)return -1;*allocated=8*(colonies*(BANK_ROWS+2*SLOTS*PACKED_WORDS+1+CANDIDATES+CANDIDATES*PACKED_WORDS+3)+ROM_ROWS*7+WORKSPACE_WORDS+CHUNK*INFO_WORDS+READ_CAPACITY*(1+PACKED_WORDS));if(*allocated>budget||budget>UINT64_C(8)*1024*1024*1024)return -2;
 World*w=(World*)calloc(1,sizeof(World));if(!w)return -3;w->colonies=colonies;w->age=age;cudaError_t e=alloc(&w->data,colonies*BANK_ROWS);
 if(e==cudaSuccess)e=alloc(&w->rows,colonies*SLOTS*PACKED_WORDS);if(e==cudaSuccess)e=alloc(&w->nextrows,colonies*SLOTS*PACKED_WORDS);if(e==cudaSuccess)e=alloc(&w->counts,colonies);
 if(e==cudaSuccess)e=alloc(&w->candidates,colonies*CANDIDATES);if(e==cudaSuccess)e=alloc(&w->outputs,colonies*CANDIDATES*PACKED_WORDS);if(e==cudaSuccess)e=alloc(&w->status,colonies*3);
 if(e==cudaSuccess)e=alloc(&w->rom,ROM_ROWS*7);if(e==cudaSuccess)e=alloc(&w->work,WORKSPACE_WORDS);if(e==cudaSuccess)e=alloc(&w->stage,CHUNK*INFO_WORDS);if(e==cudaSuccess)e=alloc(&w->readpos,READ_CAPACITY);if(e==cudaSuccess)e=alloc(&w->readout,READ_CAPACITY*PACKED_WORDS);
 if(e==cudaSuccess)e=cudaMemset(w->data,0,colonies*BANK_ROWS*8);if(e==cudaSuccess)e=cudaMemset(w->counts,0,colonies*8);if(e==cudaSuccess)e=cudaMemcpy(w->rom,rom,ROM_ROWS*7*8,cudaMemcpyHostToDevice);
 if(e!=cudaSuccess){rp_free(w);return (int)e;}*handle=w;return 0;
}
extern "C" int rp_info(void*handle,size_t first,size_t count,const uint64_t*rows){World*w=(World*)handle;if(!w||!count||count>CHUNK||first+count>w->colonies)return -1;cudaError_t e=cudaMemcpy(w->stage,rows,count*INFO_WORDS*8,cudaMemcpyHostToDevice);if(e==cudaSuccess){upload_info<<<(unsigned)((count*INFO_WORDS+127)/128),128>>>(*w,first,count);e=cudaGetLastError();}if(e==cudaSuccess)e=cudaDeviceSynchronize();return (int)e;}
extern "C" int rp_initial(void*handle,size_t first,size_t count,const uint64_t*rows,const uint64_t*counts){World*w=(World*)handle;if(!w||count>CHUNK||first+count>w->colonies)return -1;cudaError_t e=cudaMemcpy(w->rows+first*SLOTS*PACKED_WORDS,rows,count*SLOTS*PACKED_WORDS*8,cudaMemcpyHostToDevice);if(e==cudaSuccess)e=cudaMemcpy(w->counts+first,counts,count*8,cudaMemcpyHostToDevice);if(e==cudaSuccess){initial_data<<<(unsigned)((count+127)/128),128>>>(*w,first,count);e=cudaGetLastError();}if(e==cudaSuccess)e=cudaDeviceSynchronize();return (int)e;}
extern "C" int rp_step(void*handle,uint64_t*metrics){World*w=(World*)handle;if(!w)return -1;int guard=domain(w);if(guard)return guard;unsigned blocks=(unsigned)((w->colonies+127)/128);prepare<<<blocks,128>>>(*w);cudaError_t e=cudaGetLastError();if(e==cudaSuccess){evaluate<<<WORKERS/32,32>>>(*w);e=cudaGetLastError();}if(e==cudaSuccess){validate<<<blocks,128>>>(*w);e=cudaGetLastError();}
 uint64_t*status=(uint64_t*)malloc(w->colonies*3*8);if(!status)return -3;if(e==cudaSuccess)e=cudaMemcpy(status,w->status,w->colonies*3*8,cudaMemcpyDeviceToHost);metrics[0]=metrics[1]=metrics[2]=0;bool bad=false;for(size_t i=0;e==cudaSuccess&&i<w->colonies;++i){metrics[0]+=status[3*i];metrics[1]+=status[3*i+1];if(status[3*i+1]>metrics[2])metrics[2]=status[3*i+1];bad|=status[3*i+2]!=0;}free(status);if(e!=cudaSuccess)return (int)e;if(bad)return -4;
 if(w->age==0||w->age==RESET1||w->age==RESET2||w->age==VOTE0||w->age==WF_START||w->age==RESET4||w->age==PERIOD-1){bulk_data<<<(unsigned)((w->colonies*BANK_ROWS+127)/128),128>>>(*w);e=cudaGetLastError();}if(e==cudaSuccess){commit<<<blocks,128>>>(*w);e=cudaGetLastError();}if(e==cudaSuccess)e=cudaDeviceSynchronize();if(e!=cudaSuccess)return (int)e;uint64_t*old=w->rows;w->rows=w->nextrows;w->nextrows=old;w->age=(w->age+1)%PERIOD;return 0;}
extern "C" int rp_read(void*handle,const uint64_t*positions,size_t count,uint64_t*out){World*w=(World*)handle;if(!w||!count||count>READ_CAPACITY)return -1;cudaError_t e=cudaMemcpy(w->readpos,positions,count*8,cudaMemcpyHostToDevice);if(e==cudaSuccess){read_cells<<<(unsigned)((count+127)/128),128>>>(*w,count);e=cudaGetLastError();}if(e==cudaSuccess)e=cudaMemcpy(out,w->readout,count*PACKED_WORDS*8,cudaMemcpyDeviceToHost);return (int)e;}
/* Exact shared physical time jumps. No upper transition is evaluated here. */
static bool active_age(uint64_t a){return a<END0||(a>=RESET1&&a<END1)||(a>=RESET2&&a<END2)||(a>=WF_START&&a<END3)||(a>=RESET4&&a<END4);}
static bool bulk_age(uint64_t a){return a==0||a==RESET1||a==RESET2||a==VOTE0||a==CAPTURE-1||a==PREFIX_LIMIT||a==WF_START||a==RESET4||a==PERIOD-1;}
static uint64_t boundary_distance(uint64_t a){const uint64_t points[]={0,END0,RESET1,END1,RESET2,VOTE0,CAPTURE-1,CAPTURE,END2,PREFIX_LIMIT,WF_START,WF_END,END3,RESET4,END4,PERIOD-1,PERIOD};uint64_t d=PERIOD-a;for(unsigned i=0;i<sizeof(points)/sizeof(points[0]);++i)if(points[i]>a&&points[i]-a<d)d=points[i]-a;return d;}
__device__ uint64_t meta(World w,uint64_t a,int k){return a<ROM_ROWS?w.rom[a*7+k]:k==0?(a>=Q-5?0:6):k==1?a:k==2&&a>=Q-5?31:0;}
__device__ bool waiting(World w,const uint64_t*row){uint64_t a=get(row,P_ADDRESS);return get(row,P_HEAD)&&!get(row,P_DIRECTION)&&get(row,P_PHASE)==0&&meta(w,a,0)==10&&meta(w,a,1)==get(row,P_PC)&&get(row,P_RD)>0;}
__global__ void jump_limit(World w,uint64_t limit,bool moving){size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.colonies)return;uint64_t heads=0;bool stationary=signal_shape(w,col,w.age>=PREFIX_LIMIT);if(!stationary)limit=0;
 for(size_t i=0;i<w.counts[col]&&limit;++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;uint64_t a=get(row,P_ADDRESS);if(!moving)continue;
  if(get(row,P_HEAD)){if(a>=ROM_ROWS||++heads>1){limit=0;break;}uint64_t distance;
   if(waiting(w,row))distance=get(row,P_RD);
   else if(get(row,P_DIRECTION))distance=a;
   else{uint64_t target=ROM_ROWS-1,x=UINT64_MAX,phase=get(row,P_PHASE),pc=get(row,P_PC),ra=get(row,P_RA),rb=get(row,P_RB),rd=get(row,P_RD);
    if(phase==0&&pc<ROM_ROWS-MEM_ROWS-1)x=MEM_ROWS+pc;
    else if((phase==1||phase==4||phase==5)&&ra<MEM_ROWS)x=ra;
    else if(phase==2&&rb<MEM_ROWS)x=rb;
    else if(phase==3&&rd<MEM_ROWS)x=rd;
    else if(phase==6&&get(row,P_VALUE)&&rd<ROM_ROWS)x=rd;
    if(x>=a&&x<target)target=x;distance=target-a;
   }
   if(distance<limit)limit=distance;
  }else for(unsigned k=P_PHASE;k<P_LP_TARGET;++k)if(get(row,k))limit=0;
  for(unsigned dir=0;dir<2;++dir){unsigned track=dir?P_LP_TARGET:P_RP_TARGET;if(!get(row,track+3)){for(unsigned k=0;k<3;++k)if(get(row,track+k))limit=0;continue;}
   uint64_t distance=dir?a:Q-1-a,target=get(row,track);bool mem=target<MEM_ROWS||(target>=Q-5&&target<Q);
   if(!get(row,track+2)&&mem){if(dir&&target<a&&a-target-1<distance)distance=a-target-1;if(!dir&&target>a&&target-a-1<distance)distance=target-a-1;}
   if(distance<limit)limit=distance;
  }
 }
 w.status[3*col]=limit;
}
__device__ uint64_t* destination(World w,size_t col,uint64_t a,size_t*count){uint64_t*base=w.nextrows+col*SLOTS*PACKED_WORDS;size_t i=0;while(i<*count&&get(base+i*PACKED_WORDS,P_ADDRESS)<a)++i;if(i<*count&&get(base+i*PACKED_WORDS,P_ADDRESS)==a)return base+i*PACKED_WORDS;if(*count>=SLOTS){w.status[3*col+2]=1;return nullptr;}for(size_t j=*count;j>i;--j)for(unsigned k=0;k<PACKED_WORDS;++k)base[j*PACKED_WORDS+k]=base[(j-1)*PACKED_WORDS+k];uint64_t*out=base+i*PACKED_WORDS;for(unsigned k=0;k<PACKED_WORDS;++k)out[k]=0;put(out,P_ADDRESS,a);++*count;return out;}
__global__ void move_records(World w,uint64_t delta){size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col>=w.colonies)return;size_t count=0;w.status[3*col+2]=0;
 for(size_t i=0;i<w.counts[col];++i){const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;uint64_t a=get(row,P_ADDRESS);
  if(get(row,P_SIGNAL)){uint64_t*out=destination(w,col,a,&count);if(!out)return;put(out,P_SIGNAL,get(row,P_SIGNAL));}
  if(get(row,P_HEAD)){bool wait=waiting(w,row);uint64_t target=wait?a:get(row,P_DIRECTION)?a-delta:a+delta;uint64_t*out=destination(w,col,target,&count);if(!out)return;for(unsigned k=P_HEAD;k<P_LP_TARGET;++k)put(out,k,k==P_RD&&wait?get(row,k)-delta:get(row,k));}
  for(unsigned dir=0;dir<2;++dir){unsigned track=dir?P_LP_TARGET:P_RP_TARGET;if(get(row,track+3)){uint64_t*out=destination(w,col,dir?a-delta:a+delta,&count);if(!out)return;for(unsigned k=0;k<4;++k)put(out,track+k,get(row,track+k));}}
 }
 w.status[3*col+1]=count;
}
__global__ void commit_counts(World w){size_t col=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(col<w.colonies)w.counts[col]=w.status[3*col+1];}
extern "C" int rp_jump(void*handle,uint64_t requested,uint64_t*jump){*jump=0;World*w=(World*)handle;if(!w)return -1;int guard=domain(w);if(guard)return guard;if(!requested||bulk_age(w->age))return 0;uint64_t limit=boundary_distance(w->age);if(requested<limit)limit=requested;bool moving=active_age(w->age);unsigned blocks=(unsigned)((w->colonies+127)/128);
 jump_limit<<<blocks,128>>>(*w,limit,moving);cudaError_t e=cudaGetLastError();uint64_t*status=(uint64_t*)malloc(w->colonies*3*8);if(!status)return -3;if(e==cudaSuccess)e=cudaMemcpy(status,w->status,w->colonies*3*8,cudaMemcpyDeviceToHost);for(size_t i=0;e==cudaSuccess&&i<w->colonies;++i)if(status[3*i]<limit)limit=status[3*i];if(e!=cudaSuccess||!limit){free(status);return (int)e;}
 if(moving){move_records<<<blocks,128>>>(*w,limit);e=cudaGetLastError();if(e==cudaSuccess)e=cudaMemcpy(status,w->status,w->colonies*3*8,cudaMemcpyDeviceToHost);bool bad=false;for(size_t i=0;e==cudaSuccess&&i<w->colonies;++i)bad|=status[3*i+2]!=0;if(e!=cudaSuccess||bad){free(status);return (int)e;}commit_counts<<<blocks,128>>>(*w);e=cudaGetLastError();if(e==cudaSuccess)e=cudaDeviceSynchronize();if(e!=cudaSuccess){free(status);return (int)e;}uint64_t*old=w->rows;w->rows=w->nextrows;w->nextrows=old;}
 free(status);w->age=(w->age+limit)%PERIOD;*jump=limit;return 0;
}

extern "C" int rp_bank(void*handle,size_t col,const uint64_t*bank){World*w=(World*)handle;if(!w||col>=w->colonies)return -1;return (int)cudaMemcpy(w->data+col*BANK_ROWS,bank,BANK_ROWS*8,cudaMemcpyHostToDevice);}
extern "C" int rp_restore_age(void*handle,uint64_t age){World*w=(World*)handle;if(!w||age>=PERIOD)return -1;uint64_t old=w->age;w->age=age;int code=domain(w);if(code)w->age=old;return code;}
