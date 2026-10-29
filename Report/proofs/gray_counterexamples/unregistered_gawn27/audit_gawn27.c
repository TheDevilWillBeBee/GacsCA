/* Receipt harness only. Includes, without editing, the frozen exact kernel. */
#include "../unregistered_gawn25/gawn25_many_offset_native.c"

int gawn27_run(const Site25 *forcing,int width,int duration,int b,int t0,
               int maxstep,int32_t *events,Site25 *final,int *summary){
    if(width<1||width>104||duration<1||duration>104||b<0||b+width>Q)return -1;
    int d=duration-1,srow=duration,c0=b-5*duration;
    if(c0>0)c0=0;
    int dmin=9-c0,rrow=srow+Q-2;
    int nbound=16*((Q-c0+3+11)/12),bound=rrow+nbound+Q/2;
    if(maxstep!=bound||t0!=100*Q+2||t0+maxstep>=U)return -2;
    int base=b-5*maxstep-16,n=10*maxstep+width+33,start=b-base;
    Site25 *buf[2]={calloc(n,sizeof(Site25)),calloc(n,sizeof(Site25))};
    if(!buf[0]||!buf[1]){free(buf[0]);free(buf[1]);return -3;}
    int allowed[Q]={0};allowed[0]=1;
    for(int i=0;i<duration*width;i++){
        Site25 v=forcing[i];
        if(v.offset>=Q||(v.offset&&v.offset<dmin)||v.f1>1||v.f2>1||v.wf1>1||v.wf2>1){
            free(buf[0]);free(buf[1]);return -4;}
        allowed[v.offset]=1;
    }
    memcpy(buf[0]+start,forcing,width*sizeof(Site25));
    int oldlo[2]={start,n},oldhi[2]={start+width-1,-1},lo=start,hi=start+width-1;
    int firstquiet=-1,lastgf=-1,lastactive=-1,c=c0,violations=0;
    long long checked=0;
    for(int s=0;s<=maxstep;s++){
        int slot=s&1;Site25 *a=buf[slot];int noq=0,pulse=0;
        if(s){
            Site25 *old=buf[1-slot];
            if(oldhi[slot]>=oldlo[slot])memset(a+oldlo[slot],0,(oldhi[slot]-oldlo[slot]+1)*sizeof(Site25));
            int from=lo-5,to=hi+5;
            if(hi<lo){from=n;to=-1;}
            if(from<=to&&(from<5||to>=n-5)){free(buf[0]);free(buf[1]);return -5;}
            for(int i=from;i<=to;i++)a[i]=step25(old,i,base+i,(t0+s)&(U-1),&noq,&pulse);
            oldlo[slot]=from;oldhi[slot]=to;
            if(s<duration){
                memcpy(a+start,forcing+s*width,width*sizeof(Site25));
                if(start<oldlo[slot])oldlo[slot]=start;
                if(start+width-1>oldhi[slot])oldhi[slot]=start+width-1;
            }
        }
        int phase=(t0+s)%16;
        if(s>=srow&&s<=rrow)c=c0-(phase<3?3-phase:0);
        else if(s>rrow&&c<Q)c+=phase?1:-3;
        if(c>Q)c=Q;
        int gf=0,f1=0,f2=0,w1=0,w2=0,nlo=n,nhi=-1,glo=n,ghi=-1;
        int badprefix=0,badtag=0,badright=0,badpalette=0;
        for(int i=oldlo[slot];i<=oldhi[slot];i++){
            Site25 v=a[i];int x=base+i;checked++;
            gf+=v.offset!=0;f1+=v.f1;f2+=v.f2;w1+=v.wf1;w2+=v.wf2;
            badpalette+=!allowed[v.offset];
            if(v.offset){if(i<glo)glo=i;ghi=i;}
            if(v.offset||v.f1||v.f2||v.wf1||v.wf2){if(i<nlo)nlo=i;nhi=i;}
            if(x>=Q)badright+=v.offset||v.f1||v.f2||v.wf1||v.wf2;
            if(s>=srow){
                if(x<c)badprefix+=v.offset||v.f2;
                if(v.wf1||v.wf2)violations++;
                int age=s-srow;
                if(age>=1&&v.offset&&x<Q){
                    int front=Q-age-2,begin=Q-v.offset;
                    if(front<begin)front=begin;
                    if(x>=front&&!v.f1)badtag++;
                }
            }
        }
        if(s==rrow+nbound&&(gf||f2))violations++;
        if(s==bound&&(gf||f1||f2||w1||w2))violations++;
        violations+=badprefix+badtag+badright+badpalette;
        int32_t row[16]={s,gf,f1,f2,w1,w2,gf?base+glo:0,gf?base+ghi+1:0,
            nhi>=nlo?base+nlo:0,nhi>=nlo?base+nhi+1:0,noq,pulse,
            s>=srow?c:0,badprefix,badtag,badright+badpalette};
        memcpy(events+16*s,row,sizeof(row));
        if(gf)lastgf=s;
        if(nhi>=nlo)lastactive=s;
        if(s>=d&&nhi<0&&firstquiet<0)firstquiet=s;
        lo=nlo;hi=nhi;
    }
    memcpy(final,buf[maxstep&1],n*sizeof(Site25));
    summary[0]=violations;summary[1]=base;summary[2]=n;summary[3]=firstquiet;
    summary[4]=lastgf;summary[5]=lastactive;summary[6]=c0;summary[7]=dmin;
    summary[8]=rrow;summary[9]=nbound;summary[10]=bound;
    summary[11]=(int)checked;
    free(buf[0]);free(buf[1]);return violations?1:0;
}
