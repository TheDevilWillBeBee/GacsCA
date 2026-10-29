/* Exact closed-Workspace common-clock native projection of frozen GAWN2.
 * Offsets are FULL uint12 words, not a binary foreign flag. No CA change.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define Q 4096
#define U 524288
typedef struct {uint16_t offset;uint8_t f1,f2,wf1,wf2;} Site25;
typedef struct {int32_t step,gf,f1,f2,wf1,wf2,gf_lo,gf_hi,active_lo,active_hi,no_quorum_inputs,source3_updates;} Event25;

static uint16_t majority25(const Site25 *a,int centre,int side,int *exists){
    for(int j=1;j<=5;j++){
        uint16_t value=a[centre+side*j].offset;int count=0;
        for(int h=1;h<=5;h++)count+=a[centre+side*h].offset==value;
        if(count>=3){*exists=1;return value;}
    }
    *exists=0;return a[centre].offset;
}

static Site25 step25(const Site25 *a,int i,int x,int nextage,int *noq,int *pulse){
    int exists=0,left_exists=0;
    uint16_t right=majority25(a,i,1,&exists),left=majority25(a,i,-1,&left_exists);
    int r=(x+right)&(Q-1),mismatch=0,rightf1=0,w1=0,w2=0,lf2=0,li2=0;
    for(int j=-5;j<=5;j++){
        int inside=exists&&0<=r+j&&r+j<Q;
        w1+=inside&&a[i+j].wf1;w2+=inside&&a[i+j].wf2;
        if(j<0){mismatch+=inside&&(a[i+j].offset!=right);lf2+=a[i+j].f2;li2+=inside&&a[i+j].f2;}
        if(j>0)rightf1+=inside&&a[i+j].f1;
    }
    int f1=!exists||mismatch>=3||w1>=3||rightf1>=3||(a[i].f1&&rightf1>=2);
    int source3=!exists&&nextage%16==0,source4=w2>=3;
    if(noq)*noq+=!exists;
    if(pulse)*pulse+=source3;
    int turn_on=li2>=4||(f1&&lf2>=4)||source3||source4;
    int erase=(!f1&&li2<=1)||(f1&&lf2==0);
    int f2=a[i].f2?(source3||source4||!erase):turn_on;
    Site25 result={(uint16_t)((exists&&(!f1||f2))?right:left),(uint8_t)f1,(uint8_t)f2,0,0};
    return result;
}

int gawn25_site_size(void){return sizeof(Site25);}
int gawn25_event_size(void){return sizeof(Event25);}
int gawn25_local(const Site25 *eleven,int x,int nextage,Site25 *result){
    if(nextage<0||nextage>=U||(96*Q<=nextage&&nextage<98*Q))return -1;
    for(int j=0;j<11;j++)if(eleven[j].offset>=Q||eleven[j].f1>1||eleven[j].f2>1||eleven[j].wf1>1||eleven[j].wf2>1)return -2;
    *result=step25(eleven,5,x,nextage,NULL,NULL);return 0;
}

/* Single exact finite initial fault, optionally re-forced on the next
 * duration-1 after-rows. The initial prefix and all unforced exterior
 * sites are the actual canonical, quiet common-clock native row.
 * Capacity includes the COMPLETE radius5 causal cone for maxstep.
 * All sites outside the active native halo have exact quiet successors.
 */
int gawn25_run(const Site25 *forcing,int width,int duration,int b,int t0,int maxstep,
               Event25 *events,Site25 *final,int *summary){
    if(width<1||width>104||duration<1||duration>104||maxstep<1||maxstep>=U)return -1;
    for(int s=0;s<=maxstep;s++){
        int theta=(t0+s)&(U-1);if(96*Q<=theta&&theta<98*Q)return -2;
    }
    int base=b-5*maxstep-16,n=10*maxstep+width+33,start=b-base;
    Site25 *buf[2]={calloc(n,sizeof(Site25)),calloc(n,sizeof(Site25))};
    if(!buf[0]||!buf[1]){free(buf[0]);free(buf[1]);return -3;}
    int allowed[Q]={0};allowed[0]=1;
    for(int i=0;i<duration*width;i++){
        if(forcing[i].offset>=Q||forcing[i].f1>1||forcing[i].f2>1||forcing[i].wf1>1||forcing[i].wf2>1){free(buf[0]);free(buf[1]);return -4;}
        allowed[forcing[i].offset]=1;
    }
    memcpy(buf[0]+start,forcing,width*sizeof(Site25));
    int oldlo[2]={start,n},oldhi[2]={start+width-1,-1};
    int lo=start,hi=start+width-1,status=1,steps=0,maxgf=0,maxspan=0,maxactive=0;
    int offsetdomain=1,bounds=1;
    for(int s=0;s<=maxstep;s++){
        int slot=s&1;Site25 *a=buf[slot];
        int no_quorum_inputs=0,source3_updates=0;
        if(s){
            Site25 *old=buf[1-slot];
            if(oldhi[slot]>=oldlo[slot])memset(a+oldlo[slot],0,(oldhi[slot]-oldlo[slot]+1)*sizeof(Site25));
            int from=lo-5,to=hi+5;
            if(from<5||to>=n-5){bounds=0;status=-5;steps=s-1;break;}
            for(int i=from;i<=to;i++){
                a[i]=step25(old,i,base+i,(t0+s)&(U-1),&no_quorum_inputs,&source3_updates);
                if(!allowed[a[i].offset])offsetdomain=0;
            }
            oldlo[slot]=from;oldhi[slot]=to;
            if(s<duration){
                memcpy(a+start,forcing+s*width,width*sizeof(Site25));
                if(start<oldlo[slot])oldlo[slot]=start;
                if(start+width-1>oldhi[slot])oldhi[slot]=start+width-1;
            }
        }
        int gf=0,f1=0,f2=0,wf1=0,wf2=0,nlo=n,nhi=-1,glo=n,ghi=-1;
        for(int i=oldlo[slot];i<=oldhi[slot];i++){
            Site25 v=a[i];gf+=v.offset!=0;f1+=v.f1;f2+=v.f2;wf1+=v.wf1;wf2+=v.wf2;
            if(v.offset){if(i<glo)glo=i;ghi=i;}
            if(v.offset||v.f1||v.f2||v.wf1||v.wf2){if(i<nlo)nlo=i;nhi=i;}
        }
        events[s]=(Event25){s,gf,f1,f2,wf1,wf2,gf?base+glo:0,gf?base+ghi+1:0,
                           nhi>=nlo?base+nlo:0,nhi>=nlo?base+nhi+1:0,no_quorum_inputs,source3_updates};
        if(gf>maxgf)maxgf=gf;
        if(gf&&ghi-glo+1>maxspan)maxspan=ghi-glo+1;
        if(nhi>=nlo&&nhi-nlo+1>maxactive)maxactive=nhi-nlo+1;
        steps=s;lo=nlo;hi=nhi;
        if(nhi<0){
            if(s>=duration-1){status=0;break;}
            lo=start;hi=start+width-1;
        }
    }
    int lastslot=steps&1;
    memcpy(final,buf[lastslot],n*sizeof(Site25));
    summary[0]=status;summary[1]=steps;summary[2]=base;summary[3]=n;
    summary[4]=maxgf;summary[5]=maxspan;summary[6]=maxactive;
    summary[7]=offsetdomain;summary[8]=bounds;
    free(buf[0]);free(buf[1]);return status;
}
