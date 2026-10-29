/* Evaluation of the unchanged proved native/voted-Info quotient.
 * Integer operations only. Every finite cut is guarded at every row.
 * No physical-source, reachability, full upper successor or iid claim. */
#include <cuda_runtime.h>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <vector>
constexpr int Q=1024, LO=80*Q, HI=192*Q, NX=HI-LO;
constexpr int NF=9, BORDER=64, CAP=512, ICAP=64, THREADS=256;
static void ck(cudaError_t e){if(e!=cudaSuccess){fprintf(stderr,"CUDA: %s\n",cudaGetErrorString(e));exit(2);}}
template<class T>static T* alloc(size_t n){T*p;ck(cudaMalloc(&p,n*sizeof(T)));ck(cudaMemset(p,0,n*sizeof(T)));return p;}
__device__ int rd(const uint8_t*a,size_t base,int i){return 0<=i&&i<NX?a[base+i]:0;}
__device__ void add_metrics(uint32_t*m,int v[NF]){
    __shared__ int sw[8][NF];
    const int lane=threadIdx.x&31,warp=threadIdx.x>>5;
    for(int k=0;k<NF;k++){
        for(int d=16;d;d>>=1){int w=__shfl_down_sync(0xffffffff,v[k],d);v[k]=(k==1||k==2)?max(v[k],w):v[k]+w;}
        if(lane==0)sw[warp][k]=v[k];
    }
    __syncthreads();
    if(warp==0)for(int k=0;k<NF;k++){
        int w=lane<8?sw[lane][k]:0;
        for(int d=16;d;d>>=1){int z=__shfl_down_sync(0xffffffff,w,d);w=(k==1||k==2)?max(w,z):w+z;}
        if(lane==0&&w){if(k==1||k==2)atomicMax(m+k,(uint32_t)w);else atomicAdd(m+k,(uint32_t)w);}
    }
}
__device__ void native_metrics(int val,int i,int v[NF]){
    v[0]=val&1;v[1]=(val&1)?HI-(LO+i):0;v[2]=(val&1)?LO+i+1:0;
    for(int b=1;b<5;b++)v[b+2]=(val>>b)&1;
    v[7]=0;v[8]=(i<BORDER||i>=NX-BORDER)&&val;
}
__global__ void init(uint8_t*a,uint8_t*info,const int*masks,uint32_t*metrics,int rows){
    size_t id=(size_t)blockIdx.x*blockDim.x+threadIdx.x;
    int c=id/NX,i=id%NX,x=LO+i,mask=masks[c],col=x/Q,ph=x&(Q-1);
    int v=141*Q<=x&&x<142*Q-512?2:142*Q-512<=x&&x<149*Q-512?1:149*Q-512<=x&&x<149*Q?3:0;
    int z=(ph==509&&142<=col&&col<=148)||(ph==1021&&((112<=col&&col<=140)||(149<=col&&col<=151)))
        ||(ph==3&&131<=col&&col<=141&&(mask&(1<<(col-131))))||(ph==515&&col==148&&(mask&(1<<11)));
    a[id]=v;info[id]=z;
    int vs[NF];native_metrics(v,i,vs);vs[7]=z;vs[8]+=(i<BORDER||i>=NX-BORDER)&&z;
    add_metrics(metrics+(size_t)c*rows*NF,vs);
}
__global__ void refine(const uint8_t*a,uint8_t*g){
    size_t id=(size_t)blockIdx.x*blockDim.x+threadIdx.x;int i=id%NX;size_t base=id-i;
    const int centers[4]={-30,-10,10,30};int num=0;
    #pragma unroll
    for(int b=0;b<4;b++){
        int n=0;
        #pragma unroll
        for(int d=-2;d<=2;d++)n+=(rd(a,base,i+centers[b]+d)&1)!=0;
        num+=n>=3;
    }
    g[id]=num>=3?1:num<=1?0:(a[id]&1);
}
__global__ void update(const uint8_t*a,const uint8_t*info,const uint8_t*g,uint8_t*b,uint8_t*keep,
        uint32_t*metrics,uint32_t*endbad,int elapsed,int rows){
    size_t id=(size_t)blockIdx.x*blockDim.x+threadIdx.x;int c=id/NX,i=id%NX,x=LO+i;size_t base=id-i;
    int labels[11],r=0,l=0;
    #pragma unroll
    for(int d=-5;d<=5;d++){labels[d+5]=rd(g,base,i+d);if(d>0)r+=labels[d+5];if(d<0)l+=labels[d+5];}
    r=r>=3;l=l>=3;int p=(x+512*r)&(Q-1),mm=0,rf=0,wf=0,quiet=0,w2=0,la=0,li=0;
    #pragma unroll
    for(int d=1;d<=5;d++){
        if(p-d>=0)mm+=labels[5-d]!=r;
        quiet+=labels[5+d]==r&&!(rd(a,base,i+d)&2);
        int f=(rd(a,base,i-d)&8)!=0;la+=f;if(p-d>=0)li+=f;
    }
    #pragma unroll
    for(int d=1;d<=8;d++)if(p+d<Q)rf+=(rd(a,base,i+d)&2)!=0;
    #pragma unroll
    for(int d=-5;d<=5;d++)if(0<=p+d&&p+d<Q){int old=rd(a,base,i+d);wf+=(old&4)!=0;w2+=(old&16)!=0;}
    int f=mm>=3||rf>=3||((a[id]&2)&&rf>=2)||wf>=3||(p<Q-5&&quiet<3);
    int d4=w2>=3,on=li>=4||(f&&la>=4)||d4,erase=(!f&&li<2)||(f&&!la);
    int f2=(a[id]&8)?(d4||!erase):on;
    int selected=(!f||f2)?r:l,newp=(x+512*selected)&(Q-1);
    int wnew=elapsed<2*Q&&newp>=Q-5&&rd(info,base,i+Q-3-newp);
    int w2new=elapsed<2*Q&&newp<5&&!f&&rd(info,base,i+3-newp);
    int val=selected|(f<<1)|(wnew<<2)|(f2<<3)|(w2new<<4);
    b[id]=val;keep[id]=!(f&&selected!=labels[5]);
    int vs[NF];native_metrics(val,i,vs);add_metrics(metrics+((size_t)c*rows+elapsed+1)*NF,vs);
    if(elapsed==6143){int expected=151552<=x&&x<152064?2:152064<=x&&x<155136?1:155136<=x&&x<155648?3:0;if(val!=expected)atomicAdd(endbad+c,1u);}
}
__global__ void update_info(const uint8_t*a,const uint8_t*keep,uint8_t*b,uint32_t*metrics,int row,int rows){
    size_t id=(size_t)blockIdx.x*blockDim.x+threadIdx.x;int c=id/NX,i=id%NX;size_t base=id-i;
    int value=0;
    if(a[id]){int count=0;for(int d=-2;d<=2;d++)count+=0<=i+d&&i+d<NX?keep[base+i+d]:1;value=count>=3;}
    b[id]=value;int v[NF]={0,0,0,0,0,0,0,value,(i<BORDER||i>=NX-BORDER)&&value};
    add_metrics(metrics+((size_t)c*rows+row)*NF,v);
}
__global__ void capture(const uint8_t*a,const uint8_t*info,const int*indices,uint32_t*nc,int2*trans,uint32_t*ic,int*ip,int row){
    int selected=blockIdx.x/(NX/THREADS),i=(blockIdx.x%(NX/THREADS))*THREADS+threadIdx.x,c=indices[selected];if(c<0)return;
    size_t base=(size_t)c*NX,key=(size_t)row*4+selected;int val=a[base+i],prev=i?a[base+i-1]:0;
    if(val!=prev){uint32_t n=atomicAdd(nc+key,1u);if(n<CAP)trans[key*CAP+n]=make_int2(LO+i,val);}
    if(info[base+i]){uint32_t n=atomicAdd(ic+key,1u);if(n<ICAP)ip[key*ICAP+n]=LO+i;}
}
template<class T>static std::vector<T> fetch(T*p,size_t n){std::vector<T>v(n);ck(cudaMemcpy(v.data(),p,n*sizeof(T),cudaMemcpyDeviceToHost));return v;}
template<class T>static void save(const std::string&p,const std::vector<T>&v){std::ofstream f(p,std::ios::binary);f.write((const char*)v.data(),v.size()*sizeof(T));if(!f){fprintf(stderr,"file write failed\n");exit(3);}}
int main(int argc,char**argv){
    if(argc!=5)return 1;std::string dir=argv[1];int first=atoi(argv[2]),count=atoi(argv[3]),ticks=atoi(argv[4]);
    if(ticks<1||ticks>6144||count<1||first<-1||first+count>4096)return 1;
    std::vector<int>masks;if(first==-1)masks={0,2047,2048,4095};else for(int i=0;i<count;i++)masks.push_back(first+i);
    count=masks.size();int rows=ticks+1;size_t cells=(size_t)count*NX,records=(size_t)count*rows*NF,keys=(size_t)rows*4;
    std::vector<int>indices(4,-1);int wanted[4]={0,2047,2048,4095};for(int k=0;k<4;k++)for(int c=0;c<count;c++)if(masks[c]==wanted[k])indices[k]=c;
    auto start=std::chrono::steady_clock::now();
    uint8_t*a=alloc<uint8_t>(cells),*b=alloc<uint8_t>(cells),*g=alloc<uint8_t>(cells),*keep=alloc<uint8_t>(cells),*info=alloc<uint8_t>(cells),*nextinfo=alloc<uint8_t>(cells);
    int*dm=alloc<int>(count),*di=alloc<int>(4);ck(cudaMemcpy(dm,masks.data(),count*sizeof(int),cudaMemcpyHostToDevice));ck(cudaMemcpy(di,indices.data(),4*sizeof(int),cudaMemcpyHostToDevice));
    uint32_t*met=alloc<uint32_t>(records),*endbad=alloc<uint32_t>(count),*nc=alloc<uint32_t>(keys),*ic=alloc<uint32_t>(keys);
    int2*tr=alloc<int2>(keys*CAP);int*ip=alloc<int>(keys*ICAP);int blocks=cells/THREADS;
    init<<<blocks,THREADS>>>(a,info,dm,met,rows);capture<<<4*(NX/THREADS),THREADS>>>(a,info,di,nc,tr,ic,ip,0);
    for(int t=0;t<ticks;t++){
        refine<<<blocks,THREADS>>>(a,g);update<<<blocks,THREADS>>>(a,info,g,b,keep,met,endbad,t,rows);
        update_info<<<blocks,THREADS>>>(info,keep,nextinfo,met,t+1,rows);
        capture<<<4*(NX/THREADS),THREADS>>>(b,nextinfo,di,nc,tr,ic,ip,t+1);
        std::swap(a,b);std::swap(info,nextinfo);
        if((t+1)%64==0||t+1==ticks){ck(cudaGetLastError());ck(cudaDeviceSynchronize());double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();fprintf(stderr,"completed %d/%d rows cases%d seconds%.6f\n",t+1,ticks,count,sec);fflush(stderr);}
    }
    ck(cudaDeviceSynchronize());auto stats=fetch(met,records),nb=fetch(nc,keys),ib=fetch(ic,keys),eb=fetch(endbad,count);
    uint64_t borderbad=0;for(size_t i=8;i<stats.size();i+=NF)borderbad+=stats[i];
    uint64_t endpointbad=0;for(auto v:eb)endpointbad+=v;
    bool capacity=true;for(auto v:nb)capacity&=v<=CAP;for(auto v:ib)capacity&=v<=ICAP;
    save(dir+"/metrics.bin",stats);save(dir+"/native_transition_counts.bin",nb);save(dir+"/native_transitions.bin",fetch(tr,keys*CAP));
    save(dir+"/Info_counts.bin",ib);save(dir+"/Info_coordinates.bin",fetch(ip,keys*ICAP));save(dir+"/endpoint_bad.bin",eb);
    save(dir+"/masks.bin",masks);save(dir+"/selected_case_indices.bin",indices);
    cudaDeviceProp prop;ck(cudaGetDeviceProperties(&prop,0));double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    bool ok=!borderbad&&capacity&&(ticks!=6144||!endpointbad);
    std::ofstream meta(dir+"/metadata.json");
    meta<<"{\"passed\":"<<(ok?"true":"false")<<",\"cases\":"<<count<<",\"ticks\":"<<ticks<<",\"NX\":"<<NX<<",\"LO\":"<<LO<<",\"HI\":"<<HI
        <<",\"fields\":9,\"border_width\":64,\"border_nonzero_count\":"<<borderbad<<",\"endpoint_bad_sites\":"<<endpointbad<<",\"capture_capacity_passed\":"<<(capacity?"true":"false")
        <<",\"native_transition_capacity\":512,\"Info_capacity\":64,\"GPU\":\""<<prop.name<<"\",\"seconds\":"<<sec<<",\"physical_reachability_proved\":false,\"global_reliability_established\":false}\n";
    fprintf(stderr,"finished passed%d border%llu end%llu seconds%.6f\n",ok,(unsigned long long)borderbad,(unsigned long long)endpointbad,sec);return ok?0:4;
}
