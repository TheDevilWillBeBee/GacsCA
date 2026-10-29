/* Exploratory sparse Address seeds under unchanged frozen GAWN2.
 * The included GAWN10 native projection is verbatim; no rule change.
 * Late correct clocks make this projection independent of all SF.
 */
#include "../unregistered_gawn10/gawn10_two_offset_projection.c"

int gawn13_run(const Site *initial,int delta,int limit,int *events,
              Site *final,int *summary){
 if(delta<=0||delta>=Q||limit<1||T0+limit>U)return -1;
 Site *a=malloc(N*sizeof(Site)),*next=calloc(N,sizeof(Site));
 if(!a||!next){free(a);free(next);return -2;}
 memcpy(a,initial,N*sizeof(Site));
 int lo=5,hi=N-6,steps=0,status=1,maxgf=0,maxf1=0;
 for(int step=0;step<=limit;step++){
  if(step){
   memset(next,0,N*sizeof(Site));
   int start=lo-5,end=hi+5;
   if(start<5)start=5;if(end>N-6)end=N-6;
   for(int i=start;i<=end;i++)next[i]=transition(a,i,OFFSET+i,delta);
   Site *tmp=a;a=next;next=tmp;
  }
  int gf=0,f1=0,f2=0,wf1=0,wf2=0,nlo=N,nhi=-1;
  for(int i=0;i<N;i++){
   Site c=a[i];gf+=c.foreign;f1+=c.f1;f2+=c.f2;
   wf1+=c.wf1;wf2+=c.wf2;
   if(c.foreign||c.f1||c.f2||c.wf1||c.wf2){if(i<nlo)nlo=i;nhi=i;}
  }
  events[6*step]=step;events[6*step+1]=gf;events[6*step+2]=f1;
  events[6*step+3]=f2;events[6*step+4]=wf1;events[6*step+5]=wf2;
  if(gf>maxgf)maxgf=gf;if(f1>maxf1)maxf1=f1;steps=step;
  if(!gf&&!f1&&!f2&&!wf1&&!wf2){status=0;break;}
  lo=nlo;hi=nhi;
  if(nhi<0){lo=5;hi=5;}
 }
 memcpy(final,a,N*sizeof(Site));
 summary[0]=status;summary[1]=steps;summary[2]=maxgf;summary[3]=maxf1;
 free(a);free(next);return status;
}
