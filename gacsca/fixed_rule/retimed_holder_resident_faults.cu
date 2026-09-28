/* Full projected physical G = P F lift evolution around arbitrary exceptions.
   Reference is the existing resident coherent world. All actual exception rows
   remain on GPU. Only exact full-state equality removes an exception. */
#include "retimed_holder_resident_period.cu"
#include "retimed_holder_resident_faults_generated.h"
struct Faults{uint64_t *keys,*values,*nextkeys,*nextvalues,*candidates,*actual,*flags,*readpos,*readout,*work;size_t used;};
__device__ uint64_t raw_get(const uint64_t*row,unsigned field){unsigned o=R_OFFSETS[field],width=R_WIDTHS[field],s=o%64;uint64_t v=row[o/64]>>s;if(s+width>64)v|=row[o/64+1]<<(64-s);return width==64?v:v&((UINT64_C(1)<<width)-1);}
__device__ void raw_put(uint64_t*row,unsigned field,uint64_t v){unsigned o=R_OFFSETS[field],s=o%64,width=R_WIDTHS[field];if(width<64)v&=(UINT64_C(1)<<width)-1;row[o/64]|=v<<s;if(s+width>64)row[o/64+1]|=v>>(64-s);}
__device__ const uint64_t* exception(Faults e,uint64_t position){size_t lo=0,hi=e.used;while(lo<hi){size_t m=lo+(hi-lo)/2;if(e.keys[m]<position)lo=m+1;else hi=m;}return lo<e.used&&e.keys[lo]==position?e.values+lo*R_WORDS:nullptr;}
__device__ uint64_t base_raw(World w,uint64_t position,unsigned field){
 if(R_STATIC[field]>=0){uint64_t a=wrap((int64_t)(position%Q)+R_OFFSET[field],Q);return meta(w,a,R_STATIC[field]);}
 uint64_t source=wrap((int64_t)position+R_OFFSET[field],w.colonies*Q);unsigned k=R_LOGICAL[field];
 if(k==P_F1||k==P_F2||k==P_WF1||k==P_WF2)return physical_flag(w,source,k);
 return dyn(w,source,find(w,source),k);
}
__device__ void full_input(World w,Faults e,uint64_t pos,uint64_t*out,bool actual){const uint64_t*row=actual?exception(e,pos):nullptr;for(unsigned k=0;k<R_FIELDS;++k)out[k*WORKERS]=row?raw_get(row,k):base_raw(w,pos,k);}
__device__ void project_metadata(World w,uint64_t*out){uint64_t address=out[R_ADDRESS*WORKERS];for(unsigned k=0;k<R_FIELDS;++k)if(R_STATIC[k]>=0)out[k*WORKERS]=meta(w,wrap((int64_t)address+R_OFFSET[k],Q),R_STATIC[k]);}
__global__ void fault_prepare(World w,Faults e,size_t count){size_t worker=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
 uint64_t*in=e.work+worker,*out=in+15*R_FIELDS*WORKERS,*tmp=out+R_FIELDS*WORKERS;
 for(size_t i=worker;i<count;i+=WORKERS){uint64_t position=e.candidates[i],*saved=e.actual+i*R_WORDS;
  for(int j=-7;j<=7;++j)full_input(w,e,wrap((int64_t)position+j,w.colonies*Q),in+(j+7)*R_FIELDS*WORKERS,true);
  fault_full_local(in,out,tmp);project_metadata(w,out);
  for(unsigned k=0;k<R_WORDS;++k)saved[k]=0;for(unsigned k=0;k<R_FIELDS;++k)raw_put(saved,k,out[k*WORKERS]);
  for(int j=-7;j<=7;++j)full_input(w,e,wrap((int64_t)position+j,w.colonies*Q),in+(j+7)*R_FIELDS*WORKERS,false);
  fault_full_local(in,out,tmp);project_metadata(w,out);
  uint64_t different=0;for(unsigned k=0;k<R_FIELDS;++k)different|=raw_get(saved,k)!=out[k*WORKERS];e.flags[i]=different;
 }
}
__global__ void fault_commit(Faults e,size_t count){size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=count)return;uint64_t source=e.readpos[i];e.nextkeys[i]=e.candidates[source];for(unsigned k=0;k<R_WORDS;++k)e.nextvalues[i*R_WORDS+k]=e.actual[source*R_WORDS+k];}
__global__ void fault_read(World w,Faults e,size_t count){size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=count)return;uint64_t position=e.readpos[i],*out=e.readout+i*R_WORDS;const uint64_t*row=exception(e,position);for(unsigned k=0;k<R_WORDS;++k)out[k]=0;for(unsigned k=0;k<R_FIELDS;++k)raw_put(out,k,row?raw_get(row,k):base_raw(w,position,k));}
extern "C" void rf_free(void*handle){Faults*e=(Faults*)handle;if(!e)return;cudaFree(e->keys);cudaFree(e->values);cudaFree(e->nextkeys);cudaFree(e->nextvalues);cudaFree(e->candidates);cudaFree(e->actual);cudaFree(e->flags);cudaFree(e->readpos);cudaFree(e->readout);cudaFree(e->work);free(e);}
extern "C" int rf_create(void**handle,uint64_t*allocated){*handle=nullptr;Faults*e=(Faults*)calloc(1,sizeof(Faults));if(!e)return -1;
 *allocated=8*(R_CAPACITY*(5+3*R_WORDS)+R_READ*R_WORDS+R_WORKSPACE);
 cudaError_t error=alloc(&e->keys,R_CAPACITY);if(error==cudaSuccess)error=alloc(&e->values,R_CAPACITY*R_WORDS);
 if(error==cudaSuccess)error=alloc(&e->nextkeys,R_CAPACITY);if(error==cudaSuccess)error=alloc(&e->nextvalues,R_CAPACITY*R_WORDS);
 if(error==cudaSuccess)error=alloc(&e->candidates,R_CAPACITY);if(error==cudaSuccess)error=alloc(&e->actual,R_CAPACITY*R_WORDS);
 if(error==cudaSuccess)error=alloc(&e->flags,R_CAPACITY);if(error==cudaSuccess)error=alloc(&e->readpos,R_CAPACITY);
 if(error==cudaSuccess)error=alloc(&e->readout,R_READ*R_WORDS);if(error==cudaSuccess)error=alloc(&e->work,R_WORKSPACE);
 if(error!=cudaSuccess){rf_free(e);return (int)error;}*handle=e;return 0;
}
extern "C" int rf_upload(void*handle,const uint64_t*keys,const uint64_t*values,size_t count){Faults*e=(Faults*)handle;if(!e||count>R_CAPACITY)return -1;cudaError_t error=cudaSuccess;
 if(count){error=cudaMemcpy(e->nextkeys,keys,count*8,cudaMemcpyHostToDevice);if(error==cudaSuccess)error=cudaMemcpy(e->nextvalues,values,count*R_WORDS*8,cudaMemcpyHostToDevice);}
 if(error!=cudaSuccess)return (int)error;uint64_t*old=e->keys;e->keys=e->nextkeys;e->nextkeys=old;old=e->values;e->values=e->nextvalues;e->nextvalues=old;e->used=count;return 0;
}
extern "C" int rf_prepare(void*base,void*handle,const uint64_t*positions,size_t count,uint64_t*flags){World*w=(World*)base;Faults*e=(Faults*)handle;if(!w||!e||!count||count>R_CAPACITY)return -1;
 cudaError_t error=cudaMemcpy(e->candidates,positions,count*8,cudaMemcpyHostToDevice);
 if(error==cudaSuccess){fault_prepare<<<WORKERS/32,32>>>(*w,*e,count);error=cudaGetLastError();}
 if(error==cudaSuccess)error=cudaMemcpy(flags,e->flags,count*8,cudaMemcpyDeviceToHost);return (int)error;
}
extern "C" int rf_commit(void*handle,const uint64_t*selected,size_t count){Faults*e=(Faults*)handle;if(!e||count>R_CAPACITY)return -1;cudaError_t error=cudaSuccess;
 if(count){error=cudaMemcpy(e->readpos,selected,count*8,cudaMemcpyHostToDevice);if(error==cudaSuccess){fault_commit<<<(unsigned)((count+127)/128),128>>>(*e,count);error=cudaGetLastError();}if(error==cudaSuccess)error=cudaDeviceSynchronize();}
 if(error!=cudaSuccess)return (int)error;uint64_t*old=e->keys;e->keys=e->nextkeys;e->nextkeys=old;old=e->values;e->values=e->nextvalues;e->nextvalues=old;e->used=count;return 0;
}
extern "C" int rf_read(void*base,void*handle,const uint64_t*positions,size_t count,uint64_t*output){World*w=(World*)base;Faults*e=(Faults*)handle;if(!w||!e||!count||count>R_READ)return -1;
 cudaError_t error=cudaMemcpy(e->readpos,positions,count*8,cudaMemcpyHostToDevice);if(error==cudaSuccess){fault_read<<<(unsigned)((count+127)/128),128>>>(*w,*e,count);error=cudaGetLastError();}
 if(error==cudaSuccess)error=cudaMemcpy(output,e->readout,count*R_WORDS*8,cudaMemcpyDeviceToHost);return (int)error;
}
/* Rebase coherent MEM Data into the reference without changing actual state.
   Any changed background field is already present, with that exact value, in
   all five physical exception holders. Other fields remain in full exceptions. */
__global__ void absorb_data(World w,Faults e,size_t count){size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=count)return;
 uint64_t target=e.readpos[i];int64_t bank=bankrow(target%Q);bool coherent=bank>=0;uint64_t value=0;
 for(int d=-2;d<=2&&coherent;++d){uint64_t position=wrap((int64_t)target+d,w.colonies*Q);unsigned field=R_DATA_FIELDS[2-d];const uint64_t*row=exception(e,position);uint64_t current=row?raw_get(row,field):base_raw(w,position,field);if(d==-2)value=current;else coherent=current==value;}
 bool changed=coherent&&w.data[(target/Q)*BANK_ROWS+bank]!=value;
 if(changed)w.data[(target/Q)*BANK_ROWS+bank]=value;e.flags[i]=changed;
}
__global__ void normalize_faults(World w,Faults e){size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=e.used)return;uint64_t different=0;for(unsigned k=0;k<R_FIELDS;++k)different|=raw_get(e.values+i*R_WORDS,k)!=base_raw(w,e.keys[i],k);e.flags[i]=different;}
extern "C" int rf_absorb(void*base,void*handle,const uint64_t*positions,size_t count,uint64_t*changed){World*w=(World*)base;Faults*e=(Faults*)handle;if(!w||!e||!count||count>R_CAPACITY)return -1;
 cudaError_t error=cudaMemcpy(e->readpos,positions,count*8,cudaMemcpyHostToDevice);if(error==cudaSuccess){absorb_data<<<(unsigned)((count+127)/128),128>>>(*w,*e,count);error=cudaGetLastError();}if(error==cudaSuccess)error=cudaMemcpy(changed,e->flags,count*8,cudaMemcpyDeviceToHost);return (int)error;
}
extern "C" int rf_normalize(void*base,void*handle,uint64_t*flags){World*w=(World*)base;Faults*e=(Faults*)handle;if(!w||!e||!e->used)return -1;
 cudaError_t error=cudaMemcpy(e->candidates,e->keys,e->used*8,cudaMemcpyDeviceToDevice);if(error==cudaSuccess)error=cudaMemcpy(e->actual,e->values,e->used*R_WORDS*8,cudaMemcpyDeviceToDevice);
 if(error==cudaSuccess){normalize_faults<<<(unsigned)((e->used+127)/128),128>>>(*w,*e);error=cudaGetLastError();}if(error==cudaSuccess)error=cudaMemcpy(flags,e->flags,e->used*8,cudaMemcpyDeviceToHost);return (int)error;
}
