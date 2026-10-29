/* SP28 short-window native factor with the ACTUAL Info/WF1 dynamics.
 * No native rule/interface is changed. Durations Q/2Q are already explicit
 * proposed changes. This source projects their given raw Boolean equations;
 * it does not emit a matching own programme or an intact-history argument.
 * Info voting uses its exact old logical majority; wipe is then applied at
 * each holder. Only primaries 509/1021 can supply WF1 in the two-GF alphabet.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 1024
#define N (256*Q)
#define MASK (N-1)
enum {LABEL,F1,F2,WF1,PV,PT,CV,BP,PLANES};
static uint8_t state[PLANES][N],next[PLANES][N],refined[N];
static uint8_t info[N],newinfo[N];
static uint16_t code[N],newcode[N];
static int duration,info_mode;
static int get(const uint8_t *a,int x){return a[x&MASK];}

static void save(const char *stage,int offset){
    char path[220];
    snprintf(path,sizeof(path),"/tmp/SP28_info_factor_%d_mode%d_%s_%d.bin",duration,info_mode,stage,offset);
    FILE *f=fopen(path,"wb");if(!f)exit(8);
    if(fwrite(state,1,sizeof(state),f)!=sizeof(state) ||
       fwrite(code,2,N,f)!=N || fwrite(info,1,N,f)!=N)exit(8);
    fclose(f);
}

static int cohort(int x,int radius){
    int tags[13],count=0;
    for(int d=-radius;d<=radius;d++)if(get(state[PV],x+d))
        tags[count++]=(get(state[PT],x+d)-d)&15;
    if(count<3)return 0;
    for(int j=0;j<count;j++){
        int votes=0;for(int k=0;k<count;k++)votes+=tags[k]==tags[j];
        if(votes>=3)return 1;
    }
    return 0;
}

static void service(int x,int offset,int *pv,int *tag,int *cv,int *pos,int *packet_force){
    int adjusted[11],alive[11],combined[11],ca[11],np=0,nc=0;
    for(int d=-5;d<=5;d++){
        int k=d+5,y=(x+d)&MASK;
        alive[k]=state[PV][y];np+=alive[k];
        adjusted[k]=(state[PT][y]-d)&15;
        ca[k]=(offset<=1791) && (state[PV][y] || state[CV][y]);nc+=ca[k];
        combined[k]=((state[PV][y]?state[PT][y]+6:code[y])-d)&2047;
    }
    *pv=*tag=*cv=*pos=*packet_force=0;
    if(np>=3)for(int j=0;j<11;j++)if(alive[j]){
        int votes=0;for(int k=0;k<11;k++)votes+=alive[k] && adjusted[k]==adjusted[j];
        if(votes>=3){
            *packet_force=1;
            if(!*pv && offset<=1791 && adjusted[j]<5){*pv=1;*tag=adjusted[j];}
        }
    }
    if(nc>=3)for(int j=0;j<11;j++)if(ca[j] && combined[j]<Q+5){
        int votes=0;for(int k=0;k<11;k++)votes+=ca[k] && combined[k]==combined[j];
        if(votes>=3){*cv=1;*pos=combined[j];break;}
    }
}

static void flags(int x,int right,int force,int *f1,int *f2){
    int phase=(x+512*right)&(Q-1);
    int mismatch=0,right_flags=0,quiet=0,left_flags=0,left_inside=0,wf1=0,wf2=0;
    for(int d=1;d<=5;d++){
        if(d<=phase){mismatch+=get(refined,x-d)!=right;left_inside+=get(state[F2],x-d);}
        left_flags+=get(state[F2],x-d);
        quiet+=get(refined,x+d)==right && !get(state[F1],x+d);
    }
    for(int d=1;d<=8;d++)if(phase+d<Q)right_flags+=get(state[F1],x+d);
    for(int d=-5;d<=5;d++)if(0<=phase+d && phase+d<Q){
        wf1+=get(state[WF1],x+d);wf2+=get(state[PV],x+d);
    }
    *f1=mismatch>=3 || wf1>=3 || right_flags>=3 ||
        (state[F1][x] && right_flags>=2) || (phase<Q-5 && quiet<3);
    int on=left_inside>=4 || (*f1 && left_flags>=4);
    int erase=(!*f1 && left_inside<2) || (*f1 && left_flags==0);
    *f2=(state[F2][x]?!erase:on) || wf2>=3 || force;
}

static void step(int offset){
    for(int x=0;x<N;x++){
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
        int phase=(x+512*right)&(Q-1),pv,tag,cv,pos,packet_force;
        service(x,offset,&pv,&tag,&cv,&pos,&packet_force);
        int bp=0;
        if(offset<=1792){
            int votes=0;for(int d=1;d<=5;d++)votes+=get(state[BP],x+d);
            bp=cohort(x,6) || (phase!=Q-1 && votes>=3);
        }
        int f1,f2;flags(x,right,offset<duration || packet_force || cv || bp,&f1,&f2);
        int selected=(!f1 || f2)?right:left;
        next[LABEL][x]=selected;next[F1][x]=f1;next[F2][x]=f2;
        int output_address=(x+512*selected)&(Q-1);
        int primary=(x+Q-3-output_address)&MASK;
        next[WF1][x]=output_address>=Q-5 && offset<2*Q && info[primary];
        int birth=offset==0 && 1<=phase && phase<=5;
        next[PV][x]=birth || pv;next[PT][x]=birth?phase-1:tag;
        next[CV][x]=cv;newcode[x]=pos;next[BP][x]=bp;
    }
    for(int y=0;y<N;y++){
        int residue=y&(Q-1);newinfo[y]=0;
        if(residue!=509 && residue!=1021)continue;
        int keeps=0;
        for(int s=-2;s<=2;s++){
            int x=(y-s)&MASK;
            keeps+=!(next[F1][x] && next[LABEL][x]!=state[LABEL][x]);
        }
        newinfo[y]=info[y] && keeps>=3;
    }
    memcpy(state,next,sizeof(state));memcpy(code,newcode,sizeof(code));memcpy(info,newinfo,sizeof(info));
}

static void summary(const char *stage,int offset){
    int a=N,b=-1,count=0,totals[PLANES]={0},m509=0,m1021=0;
    for(int x=0;x<N;x++){
        if(state[LABEL][x]){if(a==N)a=x;b=x;count++;}
        for(int p=1;p<PLANES;p++)totals[p]+=state[p][x];
        if((x&(Q-1))==509)m509+=info[x];
        if((x&(Q-1))==1021)m1021+=info[x];
    }
    b++;
    int qt=count==b-a && ((a+512)&(Q-1))==0 && (b&(Q-1))==0 &&
        !totals[F2] && !totals[WF1] && !totals[PV] && !totals[CV] && !totals[BP];
    if(qt)for(int x=0;x<N;x++){
        int f1=(a-512<=x && x<a)||(b-512<=x && x<b);
        if(state[F1][x]!=f1){qt=0;break;}
    }
    printf("{\"stage\":\"%s\",\"offset\":%d,\"duration\":%d,\"Info_mode\":%d,"
           "\"left\":%d,\"right_exclusive\":%d,\"wrong_Addresses\":%d,\"contiguous\":%s,"
           "\"Flag1\":%d,\"Flag2\":%d,\"WF1\":%d,\"packets\":%d,\"codes\":%d,"
           "\"pressure\":%d,\"Info509_ones\":%d,\"Info1021_ones\":%d,\"quiet_template\":%s}\n",
           stage,offset,duration,info_mode,a,b,count,count==b-a?"true":"false",
           totals[F1],totals[F2],totals[WF1],totals[PV],totals[CV],totals[BP],
           m509,m1021,qt?"true":"false");
    fflush(stdout);save(stage,offset);
}

int main(int argc,char **argv){
    if(argc!=3)return 2;
    duration=atoi(argv[1]);info_mode=atoi(argv[2]);
    if((duration!=Q && duration!=2*Q) || info_mode<0 || info_mode>2)return 2;
    int a=128*Q-512,b=144*Q;
    for(int x=0;x<N;x++){
        state[LABEL][x]=a<=x && x<b;
        state[F1][x]=(127*Q<=x && x<a)||(b-512<=x && x<b);
        int residue=x&(Q-1);
        info[x]=(info_mode==1 && (residue==509 || residue==1021)) ||
            (info_mode==2 && residue==509 && a<=x && x<b);
    }
    summary("initial",0);
    const int checkpoints[]={1,2,1791,1792,1793,1794,2048,2049,2064,2368,3*Q,4*Q,6*Q};
    for(int offset=0;offset<6*Q;offset++){
        step(offset);
        for(int j=0;j<(int)(sizeof(checkpoints)/sizeof(checkpoints[0]));j++)
            if(offset+1==checkpoints[j])summary("trace",offset+1);
    }
    summary("final",6*Q);return 0;
}
