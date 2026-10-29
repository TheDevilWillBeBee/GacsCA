/* SP28 binary-Address-phase/common-Age projection and WF1 enclosure.
 * No existing CA, constants, ROM, compiler or backend is changed.
 * Actual header forces are redundant inside the common-clock epoch and
 * vanish outside it by counter ancestry. See SP28_FULL_ADDRESS_ISLAND.md
 * for the full-rule projection and infinite-line lift obligations.
 * Native flags are enclosed for arbitrary WF1 under its literal guard.
 * Stop if the enclosure does not certify a unique Address output.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 1024
#define U 475136
#define TF 278401
#define EPOCH 4096
#define N (256*Q)
#define MASK (N-1)
enum {LABEL,F1LO,F1HI,F2LO,F2HI,WF1HI,PLANES};
static uint8_t state[PLANES][N],next[PLANES][N],refined[N];
static int displacement=512;
static long long checked_quorums=0;
static int get(const uint8_t *a,int x){return a[x&MASK];}

static void save_state(const char *path){
    FILE *out=fopen(path,"wb");if(!out || fwrite(state,1,sizeof(state),out)!=sizeof(state))exit(3);fclose(out);
}

static void snapshot(int t){
    int offset=t-TF;
    const int times[]={0,1,2,1791,1792,1793,2047,2048,2049,4095,4096,4097};
    for(int j=0;j<(int)(sizeof(times)/sizeof(times[0]));j++)if(offset==times[j]){
        char path[160];snprintf(path,sizeof(path),"/tmp/SP28_Address_bounds_trace_%d.bin",t);
        save_state(path);break;
    }
}

static void flags(int x,int right,int upper,int force,int *f1,int *f2){
    int phase=(x+displacement*right)%Q;
    int f1plane=upper?F1HI:F1LO,f2plane=upper?F2HI:F2LO;
    int mismatch=0,right_flags=0,quiet=0,left_flags=0,left_inside=0,wf1=0;
    for(int d=1;d<=5;d++){
        if(d<=phase){mismatch+=(get(refined,x-d)!=right);left_inside+=get(state[f2plane],x-d);}
        left_flags+=get(state[f2plane],x-d);
        quiet+=(get(refined,x+d)==right && !get(state[f1plane],x+d));
    }
    for(int d=1;d<=8;d++)if(phase+d<Q)right_flags+=get(state[f1plane],x+d);
    for(int d=-5;d<=5;d++)if(0<=phase+d && phase+d<Q && upper)wf1+=get(state[WF1HI],x+d);
    *f1=mismatch>=3 || wf1>=3 || right_flags>=3 ||
        (state[f1plane][x] && right_flags>=2) || (phase<Q-5 && quiet<3);
    int on=left_inside>=4 || (*f1 && left_flags>=4);
    int erase=(!*f1 && left_inside<2) || (*f1 && left_flags==0);
    *f2=(state[f2plane][x] ? !erase : on) || force;
}

static int step(int t){
    int force=(TF<=t%U && t%U<TF+EPOCH);
    int wf1window=(TF<=t%U && t%U<TF+2*Q);
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
        int f1lo,f1hi,f2lo,f2hi;
        flags(x,right,0,force,&f1lo,&f2lo);flags(x,right,1,force,&f1hi,&f2hi);
        if(f1lo>f1hi || f2lo>f2hi)return 7;
        if(right!=left){
            checked_quorums++;
            if(!(!f1hi || f2lo) && !(f1lo && !f2hi)){
                printf("{\"ambiguous_row\":%d,\"site\":%d,\"Address_bounds\":[%d,%d]}\n",t,x,f1lo,f2hi);
                fflush(stdout);return 6;
            }
        }
        int selected=(!f1lo || f2lo)?right:left;
        next[LABEL][x]=selected;next[F1LO][x]=f1lo;next[F1HI][x]=f1hi;
        next[F2LO][x]=(t%U==U-1)?0:f2lo;next[F2HI][x]=(t%U==U-1)?0:f2hi;
        next[WF1HI][x]=((x+displacement*selected)%Q>=Q-5) && wf1window;
    }
    memcpy(state,next,sizeof(state));return 0;
}

static int summary(const char *stage,int t){
    int a=N,b=-1,ones=0,f1lo=0,f1hi=0,f2lo=0,f2hi=0,aux=0;
    for(int x=0;x<N;x++){
        if(state[LABEL][x]){if(a==N)a=x;b=x;ones++;}
        f1lo+=state[F1LO][x];f1hi+=state[F1HI][x];
        f2lo+=state[F2LO][x];f2hi+=state[F2HI][x];aux+=state[WF1HI][x];
    }
    b++;
    int contiguous=(ones==b-a),aligned=((a+displacement)%Q==0 && b%Q==0);
    int quiet_template=contiguous && aligned && !f2lo && !f2hi && !aux;
    if(quiet_template)for(int x=0;x<N;x++){
        int expected=(a-(Q-displacement)<=x && x<a)||(b-displacement<=x && x<b);
        if(state[F1LO][x]!=expected || state[F1HI][x]!=expected){quiet_template=0;break;}
    }
    printf("{\"stage\":\"%s\",\"time\":%d,\"displacement\":%d,\"left\":%d,"
           "\"right_exclusive\":%d,\"wrong_Addresses\":%d,\"Flag1_bounds\":[%d,%d],"
           "\"Flag2_bounds\":[%d,%d],\"WF1_upper_total\":%d,\"quiet_template\":%s,"
           "\"distinct_Address_quorums\":%lld}\n",stage,t,displacement,a,b,ones,f1lo,f1hi,
           f2lo,f2hi,aux,quiet_template?"true":"false",checked_quorums);
    fflush(stdout);
    char path[160];snprintf(path,sizeof(path),"/tmp/SP28_Address_bounds_%s.bin",stage);
    save_state(path);
    return quiet_template;
}

int main(int argc,char **argv){
    if(argc>1)displacement=atoi(argv[1]);
    if(displacement<16 || displacement>Q-16)return 2;
    int a=128*Q-displacement,b=144*Q;
    for(int x=a;x<b;x++)state[LABEL][x]=1;
    for(int x=0;x<N;x++)state[F1LO][x]=state[F1HI][x]=
        (127*Q<=x && x<a)||(b-displacement<=x && x<b);
    if(!summary("initial",0))return 4;
    for(int t=TF;t<TF+6*Q;t++){snapshot(t);int rc=step(t);if(rc)return rc;}
    if(!summary("after_epoch",TF+6*Q))return 5;
    summary("period",U);return 0;
}
