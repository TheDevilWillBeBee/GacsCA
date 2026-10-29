/* Exact late common-clock/two-offset native projection of frozen GAWN2.
 * No rule change or externally prescribed future Workspace. The written
 * proof establishes that the actual computed Workspace guard is closed.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define Q 4096
#define U (128*Q)
#define T0 (100*Q+2)
#define OFFSET (-Q-16)
#define N (2*Q+32)
#define SNAPSHOTS 8
typedef struct {uint8_t foreign,f1,f2,wf1,wf2;} Site;
typedef struct {int steps,gf_quiet,native_quiet,max_gf,min_gf,max_gf_x,
 max_f1,max_f2,snapshots,status;} Result;
static int phase(int x){int r=x%Q;return r<0?r+Q:r;}
static Site transition(const Site*a,int i,int x,int delta){
 Site old=a[i],out={0};int right=0,left=0;
 for(int j=1;j<=5;j++){right+=a[i+j].foreign;left+=a[i-j].foreign;}
 right=right>=3;left=left>=3;
 const int addr=phase(x+delta*right);
 int mismatch=0,rf=0,lf=0,linside=0,w1=0,w2=0;
 for(int j=-5;j<=5;j++){
  const int inside=0<=addr+j&&addr+j<Q;
  w1+=inside&&a[i+j].wf1;w2+=inside&&a[i+j].wf2;
  if(j<0){mismatch+=inside&&(a[i+j].foreign!=right);
   lf+=a[i+j].f2;linside+=inside&&a[i+j].f2;}
  if(j>0)rf+=inside&&a[i+j].f1;
 }
 out.f1=mismatch>=3||w1>=3||rf>=3||(old.f1&&rf>=2);
 const int source=w2>=3;
 const int on=linside>=4||(out.f1&&lf>=4)||source;
 const int erase=(!out.f1&&linside<=1)||(out.f1&&lf==0);
 out.f2=old.f2?(source||!erase):on;
 out.foreign=(!out.f1||out.f2)?right:left;
 /* Computed clock is common, above100Q (or0 at U); actual WF guard closed. */
 return out;
}
int gawn10_cofactor(const Site*a,int x,int delta,Site*out){
 if(delta<=0||delta>=Q)return -1;
 *out=transition(a,8,x,delta);return 0;
}
static void overwrite(Site*a,int b,int width,int flags){
 for(int x=b;x<b+width;x++)a[x-OFFSET]=(Site){1,flags&1,(flags>>1)&1,
  (flags>>2)&1,(flags>>3)&1};
}
int gawn10_campaign(int b,int width,int delta,int flags,int rows,int limit,
 int*events,Site*final,Site*snapshots,int*snapshot_rows,Result*result){
 if(b<0||width<1||width>104||b+width>Q||delta<=0||delta>=Q||
  flags<0||flags>15||rows<1||rows>104||limit<1||T0+rows+limit>=U)return -1;
 Site*a=calloc(N,sizeof(Site)),*next=calloc(N,sizeof(Site));
 if(!a||!next){free(a);free(next);return -2;}
 memset(result,0,sizeof(*result));result->min_gf=Q;result->max_gf_x=-Q;
 overwrite(a,b,width,flags);int lo=b-OFFSET,hi=b+width-1-OFFSET;
 int preset[6]={0,rows-1,rows,rows+1,rows+16,rows+128};
 int r=phase(b-3+delta),ell=r<=5?b-3-r:b-3;
 int status=1;
 for(int step=0;step<=rows-1+limit;step++){
  if(step){
   memset(next,0,N*sizeof(Site));int start=lo-5,end=hi+5;
   if(start<5)start=5;if(end>N-6)end=N-6;
   for(int i=start;i<=end;i++)next[i]=transition(a,i,OFFSET+i,delta);
   Site*tmp=a;a=next;next=tmp;
   if(step<rows)overwrite(a,b,width,flags);
  }
  int gc=0,f1=0,f2=0,w1=0,w2=0,glo=Q,ghi=-Q,nlo=N,nhi=-1;
  for(int i=0;i<N;i++){
   const int x=OFFSET+i;Site c=a[i];
   if(c.foreign){gc++;if(x<glo)glo=x;if(x>ghi)ghi=x;}
   f1+=c.f1;f2+=c.f2;w1+=c.wf1;w2+=c.wf2;
   if(c.foreign||c.f1||c.f2||c.wf1||c.wf2){if(i<nlo)nlo=i;nhi=i;}
   if((c.foreign&&(x<ell||x>=Q))||(c.f2&&(x<b-3||x>=Q))||
    (c.f1&&(x<-Q||x>=Q))||((c.wf1||c.wf2)&&(x<b||x>=b+width)))
    {status=-3;goto done;}
  }
  if(gc>result->max_gf)result->max_gf=gc;
  if(gc&&glo<result->min_gf)result->min_gf=glo;
  if(gc&&ghi>result->max_gf_x)result->max_gf_x=ghi;
  if(f1>result->max_f1)result->max_f1=f1;
  if(f2>result->max_f2)result->max_f2=f2;
  int*event=events+10*step;event[0]=step;event[1]=gc;event[2]=gc?glo:0;
  event[3]=gc?ghi:0;event[4]=f1;event[5]=f2;event[6]=w1;event[7]=w2;
  event[8]=nhi>=0?OFFSET+nlo:0;event[9]=nhi>=0?OFFSET+nhi:0;
  int snap=0;for(int j=0;j<6;j++)snap|=step==preset[j];
  if(step>=rows&&!gc&&!result->gf_quiet){result->gf_quiet=step-rows+1;snap=1;}
  if(step>=rows&&!gc&&!f1&&!f2&&!w1&&!w2){result->native_quiet=step-rows+1;snap=1;status=0;}
  if(snap&&result->snapshots<SNAPSHOTS){
   const int n=result->snapshots++;memcpy(snapshots+n*N,a,N*sizeof(Site));snapshot_rows[n]=step;
  }
  result->steps=step;
  if(status==0)break;
  lo=nlo;hi=nhi;
  if(nhi<0){lo=b-OFFSET;hi=b+width-1-OFFSET;}
 }
done:
 result->status=status;memcpy(final,a,N*sizeof(Site));free(a);free(next);return status;
}
