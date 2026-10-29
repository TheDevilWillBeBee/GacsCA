/* Exploratory domain evaluation of the unchanged native/voted-Info quotient.
 * No actual fourth-bank lift is supplied. GF is exact; all other domains
 * use 0={0}, 1={1}, 2={0,1}. Undetermined GF stops, not a CA failure. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { Q=1024, LO=80*Q, HI=200*Q, NX=HI-LO, BORDER=64 };
static uint8_t a[5][NX],b[5][NX],info[NX],nextinfo[NX],g[NX],keep[NX];
static int tn(int x){return x==2?2:!x;}
static int ta(int x,int y){return !x||!y?0:x==1?y:y==1?x:2;}
static int to(int x,int y){return x==1||y==1?1:x==0?y:y==0?x:2;}
static int tm(int c,int x,int y){return c==0?y:c==1?x:x==y?x:2;}
static int ge(int low,int high,int t){return low>=t?1:high<t?0:2;}
static void add(int v,int*low,int*high){*low+=v==1;*high+=v!=0;}
static int rd(const uint8_t*p,int i){return 0<=i&&i<NX?p[i]:0;}
static int save(const char*path){
    FILE*f=fopen(path,"wb");if(!f)return 2;
    if(fwrite(a,1,sizeof(a),f)!=sizeof(a)||fwrite(info,1,sizeof(info),f)!=sizeof(info)){fclose(f);return 2;}
    return fclose(f)?2:0;
}
static int certify(int row){
    int gf=0,f1=0,f2=0,w1=0,w2=0,unknown=0,border=0,inf=0;
    for(int i=0;i<NX;i++){
        gf+=a[0][i];f1+=a[1][i]==1;w1+=a[2][i]==1;f2+=a[3][i]==1;w2+=a[4][i]==1;inf+=info[i]!=0;
        for(int j=1;j<5;j++)unknown+=a[j][i]==2;
        if(i<BORDER||i>=NX-BORDER){for(int j=0;j<5;j++)border+=a[j][i]!=0;border+=info[i]!=0;}
    }
    printf("{\"row\":%d,\"GF_sites\":%d,\"F1_ones\":%d,\"WF1_ones\":%d,\"F2_ones\":%d,\"WF2_ones\":%d,\"unknown_native_fields\":%d,\"possible_Info_ones\":%d,\"border_violations\":%d}\n",row,gf,f1,w1,f2,w2,unknown,inf,border);
    return border?42:0;
}
int main(int argc,char**argv){
    if(argc!=2)return 1;
    for(int i=0;i<NX;i++){
        int x=LO+i,col=x/Q,p=x&(Q-1);
        a[0][i]=149*Q-512<=x&&x<152*Q;
        a[1][i]=(148*Q<=x&&x<149*Q-512)||(152*Q-512<=x&&x<152*Q);
        int fixed=(p==509&&149<=col&&col<=151)||(p==1021&&((106<=col&&col<=147)||(152<=col&&col<=154)));
        int free=(p==3&&132<=col&&col<=148)||(p==515&&148<=col&&col<=151);
        if(fixed&&free)return 3;
        info[i]=free?2:fixed;
    }
    int code=certify(0);if(code)return code;
    for(int t=0;t<6144;t++){
        for(int i=0;i<NX;i++){
            int votes=0;const int centers[4]={-30,-10,10,30};
            for(int h=0;h<4;h++){int n=0;for(int d=-2;d<=2;d++)n+=rd(a[0],i+centers[h]+d);votes+=n>=3;}
            g[i]=votes>=3?1:votes<=1?0:a[0][i];
        }
        for(int i=0;i<NX;i++){
            int x=LO+i,r=0,l=0;
            for(int d=1;d<=5;d++){r+=rd(g,i+d);l+=rd(g,i-d);}r=r>=3;l=l>=3;
            int p=(x+512*r)&(Q-1),mm=0;
            int rlo=0,rhi=0,qlo=0,qhi=0,wlo=0,whi=0,vlo=0,vhi=0;
            int llo=0,lhi=0,ilo=0,ihi=0;
            for(int d=1;d<=5;d++){
                if(p-d>=0){mm+=rd(g,i-d)!=r;add(rd(a[3],i-d),&ilo,&ihi);}
                add(rd(a[3],i-d),&llo,&lhi);
                if(rd(g,i+d)==r)add(tn(rd(a[1],i+d)),&qlo,&qhi);
            }
            for(int d=1;d<=8;d++)if(p+d<Q)add(rd(a[1],i+d),&rlo,&rhi);
            for(int d=-5;d<=5;d++)if(0<=p+d&&p+d<Q){add(rd(a[2],i+d),&wlo,&whi);add(rd(a[4],i+d),&vlo,&vhi);}
            int f=to(mm>=3,to(ge(rlo,rhi,3),to(ta(a[1][i],ge(rlo,rhi,2)),to(ge(wlo,whi,3),p<Q-5?tn(ge(qlo,qhi,3)):0))));
            int d4=ge(vlo,vhi,3),on=to(ge(ilo,ihi,4),to(ta(f,ge(llo,lhi,4)),d4));
            int erase=to(ta(tn(f),tn(ge(ilo,ihi,2))),ta(f,tn(ge(llo,lhi,1))));
            int f2=tm(a[3][i],to(d4,tn(erase)),on),choice=to(tn(f),f2);
            if(choice==2&&r!=l){
                printf("{\"abstract_GF_unresolved\":true,\"row\":%d,\"x\":%d,\"right\":%d,\"left\":%d,\"F1_domain\":%d,\"F2_domain\":%d}\n",t+1,x,r,l,f,f2);
                fflush(stdout);if(save(argv[1]))return 2;return 41;
            }
            int selected=choice==2?r:choice?r:l,np=(x+512*selected)&(Q-1);
            b[0][i]=selected;b[1][i]=f;b[3][i]=f2;
            b[2][i]=(t<2*Q&&np>=Q-5)?rd(info,i+Q-3-np):0;
            b[4][i]=(t<2*Q&&np<5)?ta(tn(f),rd(info,i+3-np)):0;
            keep[i]=tn(ta(f,selected!=g[i]));
        }
        for(int i=0;i<NX;i++){
            int low=0,high=0;
            for(int d=-2;d<=2;d++)add(0<=i+d&&i+d<NX?keep[i+d]:1,&low,&high);
            nextinfo[i]=ta(info[i],ge(low,high,3));
        }
        memcpy(a,b,sizeof(a));memcpy(info,nextinfo,sizeof(info));
        code=certify(t+1);if(code){if(save(argv[1]))return 2;return code;}
    }
    if(save(argv[1]))return 2;
    puts("{\"finite_domain_complete\":true,\"actual_fourth_source_enclosure_proved\":false,\"global_reliability_established\":false}");
    return 0;
}
