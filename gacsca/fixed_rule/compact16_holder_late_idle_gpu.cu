// Borrowed World ABI and exact fixed constants from the canonical executor.
#include "compact16_holder_canonical_gpu.cu"
__global__ void idle_check(World w,u64 age,unsigned*bad){
 size_t pos=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(pos>=w.n)return;
 bool valid=w.a[pos*FIELDS+F_AGE]==age&&w.a[pos*FIELDS+F_ADDRESS]==pos%Q;
 valid=valid&&!w.a[pos*FIELDS+F_F1]&&!w.a[pos*FIELDS+F_F2];
 for(int d=-2;d<=2;++d){size_t target=wrap((long long)pos+d,w.n);
  valid=valid&&!w.a[pos*FIELDS+F_W0_WF1+2*(d+2)]&&!w.a[pos*FIELDS+F_W0_WF1+2*(d+2)+1];
  valid=valid&&w.a[pos*FIELDS+49+(d+2)*PROC]==w.a[target*FIELDS+49+2*PROC];
  for(unsigned k=1;k<PROC;++k)valid=valid&&!w.a[pos*FIELDS+49+(d+2)*PROC+k];
  valid=valid&&((w.a[pos*FIELDS+F_SIGNAL]>>(d+2))&1)==((w.a[target*FIELDS+F_SIGNAL]>>2)&1);
 }
 if(!valid)atomicOr(bad,1u);
}
__global__ void idle_age(World w,u64 ticks){size_t pos=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(pos<w.n)w.a[pos*FIELDS+F_AGE]+=ticks;}
extern "C" int idle_run(World*w,u64 ticks,u64 age){
 if(!w||age>=U||ticks>=U||age+ticks>=U)return 1;
 unsigned*bad=nullptr;if(cudaMalloc(&bad,4)!=cudaSuccess)return 3;
 if(cudaMemset(bad,0,4)!=cudaSuccess){cudaFree(bad);return 3;}
 idle_check<<<(w->n+127)/128,128>>>(*w,age,bad);unsigned hostbad=0;
 cudaError_t error=cudaMemcpy(&hostbad,bad,4,cudaMemcpyDeviceToHost);cudaFree(bad);
 if(error!=cudaSuccess)return 3;if(hostbad)return 2;
 idle_age<<<(w->n+127)/128,128>>>(*w,ticks);return cudaDeviceSynchronize()==cudaSuccess?0:3;
}
