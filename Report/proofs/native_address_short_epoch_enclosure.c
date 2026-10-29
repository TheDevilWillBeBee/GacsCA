/* Short-duration conditional native prefix certificate.
 * See SP28_SHORT_EPOCH_ENCLOSURE_GAP.md for the one-step refinement.
 * Arbitrary private inputs are bounded by the literal WF1 guard.
 * Stops when lower/upper native flags allow different GF selectors.
 * No active candidate, ROM, compiler or earlier proposal is modified.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 1024
#define U 475136
#define TF 278401
#define N (256*Q)
#define MASK (N-1)
enum {LABEL,F1LO,F1HI,F2LO,F2HI,WF1HI,PV,PT,CV,BP,PLANES};
static uint8_t state[PLANES][N],next[PLANES][N],refined[N];
static uint16_t code[N],newcode[N];
static int duration,wf1_mode;
static long long quorums;
static int get(const uint8_t *a,int x){return a[x&MASK];}

static void save(const char *stage,int offset){
    char path[200];snprintf(path,sizeof(path),"/tmp/SP28_short_epoch_enclosure_%d_mode%d_%s_%d.bin",duration,wf1_mode,stage,offset);
    FILE *f=fopen(path,"wb");if(!f)exit(8);
    if(fwrite(state,1,sizeof(state),f)!=sizeof(state) ||
       fwrite(code,2,N,f)!=N)exit(8);
    fclose(f);
}

static int packet_cohort(int x,int radius){
    int tags[13],count=0;
    for(int d=-radius;d<=radius;d++)if(get(state[PV],x+d)){
        int tag=(get(state[PT],x+d)-d)&15;
        tags[count++]=tag;
    }
    if(count<3)return 0;
    for(int j=0;j<count;j++){
        int votes=0;for(int k=0;k<count;k++)votes+=tags[k]==tags[j];
        if(votes>=3)return 1;
    }
    return 0;
}

static void service(int x,int offset,int *pv,int *tag,int *cv,int *pos,int *cohort){
    int adjusted[11],alive[11],combined[11],ca[11],np=0,nc=0;
    for(int d=-5;d<=5;d++){
        int k=d+5,y=(x+d)&MASK;
        alive[k]=state[PV][y];np+=alive[k];
        adjusted[k]=(state[PT][y]-d)&15;
        ca[k]=(offset<=1791) && (state[PV][y] || state[CV][y]);nc+=ca[k];
        int localpos=state[PV][y]?state[PT][y]+6:code[y];
        combined[k]=(localpos-d)&2047;
    }
    *pv=*tag=*cv=*pos=*cohort=0;
    if(np>=3)for(int j=0;j<11;j++)if(alive[j]){
        int votes=0;for(int k=0;k<11;k++)votes+=alive[k] && adjusted[k]==adjusted[j];
        if(votes>=3){
            *cohort=1;
            if(!*pv && offset<=1791 && adjusted[j]<5){*pv=1;*tag=adjusted[j];}
        }
    }
    if(nc>=3)for(int j=0;j<11;j++)if(ca[j] && combined[j]<Q+5){
        int votes=0;for(int k=0;k<11;k++)votes+=ca[k] && combined[k]==combined[j];
        if(votes>=3){*cv=1;*pos=combined[j];break;}
    }
}

static void flags(int x,int right,int upper,int force,int *f1,int *f2){
    int phase=(x+512*right)&(Q-1);
    int p1=upper?F1HI:F1LO,p2=upper?F2HI:F2LO;
    int mismatch=0,right_flags=0,quiet=0,left_flags=0,left_inside=0,wf1=0,wf2=0;
    for(int d=1;d<=5;d++){
        if(d<=phase){mismatch+=get(refined,x-d)!=right;left_inside+=get(state[p2],x-d);}
        left_flags+=get(state[p2],x-d);
        quiet+=get(refined,x+d)==right && !get(state[p1],x+d);
    }
    for(int d=1;d<=8;d++)if(phase+d<Q)right_flags+=get(state[p1],x+d);
    for(int d=-5;d<=5;d++)if(0<=phase+d && phase+d<Q){
        if(upper || wf1_mode==1)wf1+=get(state[WF1HI],x+d);
        wf2+=get(state[PV],x+d);
    }
    *f1=mismatch>=3 || wf1>=3 || right_flags>=3 ||
        (state[p1][x] && right_flags>=2) || (phase<Q-5 && quiet<3);
    int on=left_inside>=4 || (*f1 && left_flags>=4);
    int erase=(!*f1 && left_inside<2) || (*f1 && left_flags==0);
    *f2=(state[p2][x] ? !erase : on) || wf2>=3 || force;
}

static int step(int offset){
    for(int x=0;x<N;x++){
        if(wf1_mode==-1){
            int expected=128*Q-512-3*offset<=x && x<144*Q-3*offset;
            if(state[LABEL][x]!=expected)return 9;
        }
        int votes=0;const int centers[4]={-30,-10,10,30};
        for(int k=0;k<4;k++){
            int ones=0;for(int d=-2;d<=2;d++)ones+=get(state[LABEL],x+centers[k]+d);
            votes+=ones>=3;
        }
        refined[x]=votes>=3?1:votes<=1?0:state[LABEL][x];
    }
    for(int x=0;x<N;x++){
        int right=0,left=0;
        for(int d=1;d<=5;d++){right+=get(refined,x+d);left+=get(refined,x-d);}
        right=right>=3;left=left>=3;
        int phase=(x+512*right)&(Q-1);
        int pv,tag,cv,pos,cohort;
        service(x,offset,&pv,&tag,&cv,&pos,&cohort);
        int bp=0;
        if(offset<=1792){
            int votes=0;for(int d=1;d<=5;d++)votes+=get(state[BP],x+d);
            bp=packet_cohort(x,6) || (phase!=Q-1 && votes>=3);
        }
        int force=offset<duration || cohort || cv || bp;
        int f1lo,f1hi,f2lo,f2hi;
        flags(x,right,0,force,&f1lo,&f2lo);flags(x,right,1,force,&f1hi,&f2hi);
        if(f1lo>f1hi || f2lo>f2hi)return 7;
        if(right!=left){
            quorums++;
            if(!(!f1hi || f2lo) && !(f1lo && !f2hi)){
                printf("{\"ambiguous_offset\":%d,\"site\":%d,\"duration\":%d,\"bounds\":[%d,%d,%d,%d]}\n",
                       offset,x,duration,f1lo,f1hi,f2lo,f2hi);
                save("ambiguous",offset);fflush(stdout);return 6;
            }
        }
        int selected=(!f1lo || f2lo)?right:left;
        next[LABEL][x]=selected;next[F1LO][x]=f1lo;next[F1HI][x]=f1hi;
        next[F2LO][x]=f2lo;next[F2HI][x]=f2hi;
        next[WF1HI][x]=wf1_mode!=0 && ((x+512*selected)&(Q-1))>=Q-5 && offset<2*Q;
        int birth=offset==0 && 1<=phase && phase<=5;
        next[PV][x]=birth || pv;next[PT][x]=birth?phase-1:tag;
        next[CV][x]=cv;newcode[x]=pos;next[BP][x]=bp;
    }
    memcpy(state,next,sizeof(state));memcpy(code,newcode,sizeof(code));return 0;
}

static int summary(const char *stage,int offset){
    int a=N,b=-1,ones=0,totals[PLANES]={0};
    for(int x=0;x<N;x++){
        if(state[LABEL][x]){if(a==N)a=x;b=x;ones++;}
        for(int p=1;p<PLANES;p++)totals[p]+=state[p][x];
    }
    b++;
    int qt=ones==b-a && ((a+512)&(Q-1))==0 && (b&(Q-1))==0 &&
           !totals[F2LO] && !totals[F2HI] && !totals[WF1HI] && !totals[PV] && !totals[CV] && !totals[BP];
    if(qt)for(int x=0;x<N;x++){
        int f1=(a-512<=x && x<a)||(b-512<=x && x<b);
        if(state[F1LO][x]!=f1 || state[F1HI][x]!=f1){qt=0;break;}
    }
    printf("{\"stage\":\"%s\",\"offset\":%d,\"duration\":%d,\"WF1_mode\":%d,\"left\":%d,\"right_exclusive\":%d,"
           "\"wrong_Addresses\":%d,\"F1_bounds\":[%d,%d],\"F2_bounds\":[%d,%d],"
           "\"WF1_upper\":%d,\"packets\":%d,\"codes\":%d,\"pressure\":%d,"
           "\"quiet_template\":%s,\"quorums\":%lld}\n",stage,offset,duration,wf1_mode,a,b,ones,
           totals[F1LO],totals[F1HI],totals[F2LO],totals[F2HI],totals[WF1HI],totals[PV],totals[CV],totals[BP],
           qt?"true":"false",quorums);fflush(stdout);save(stage,offset);return qt;
}

int main(int argc,char **argv){
    if(argc!=3)return 2;
    duration=atoi(argv[1]);wf1_mode=atoi(argv[2]);
    if(duration<0 || duration>3*Q || wf1_mode < -1 || wf1_mode>1)return 2;
    int a=128*Q-512,b=144*Q;
    for(int x=a;x<b;x++)state[LABEL][x]=1;
    for(int x=0;x<N;x++)state[F1LO][x]=state[F1HI][x]=
        (127*Q<=x && x<a)||(b-512<=x && x<b);
    summary("initial",0);
    const int checkpoints[]={1,2,1791,1792,1793,1794,2048,2049,3*Q,4*Q,6*Q};
    for(int offset=0;offset<6*Q;offset++){
        int rc=step(offset);if(rc)return rc;
        for(int j=0;j<(int)(sizeof(checkpoints)/sizeof(checkpoints[0]));j++)
            if(offset+1==checkpoints[j])summary("trace",offset+1);
    }
    return summary("final",6*Q)?0:5;
}
