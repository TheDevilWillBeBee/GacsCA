/* Exact native/Info-lowbit projection of frozen GAWN2, not a new CA.
 * Premises: canonical GF; two unwrapped clock classes avoid Age0/80Q-1;
 * five coherent Info-lowbit copies, logical primary3 in true colony0 is1,
 * every other special primary is0. Other SF fields are arbitrary.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define Q 4096
#define U (128*Q)
#define T (100*Q+2)
#define A (96*Q-1)
typedef struct {uint16_t gf;uint32_t age;uint8_t f1,f2,wf1,wf2;} Site;
typedef struct {int steps,age_quiet,flags_quiet,max_age_count,max_age_span,
 min_age_x,max_age_x,max_flag_count,source_updates;} Result;
static int phase(int x){int p=x%Q;return p<0?p+Q:p;}
static uint32_t majority(const uint32_t w[5],uint32_t fallback,int*exists){
 for(int i=0;i<3;i++){int c=0;for(int j=0;j<5;j++)c+=w[i]==w[j];
 if(c>=3){*exists=1;return w[i];}}*exists=0;return fallback;
}
static Site transition(const Site*a,int x,int coordinate){
 const Site old=a[x];Site out=old;uint32_t l[5],r[5];int re,le;
 const int gf=phase(coordinate);
 for(int j=1;j<=5;j++){l[j-1]=a[x-j].age;r[j-1]=a[x+j].age;}
 const uint32_t ra=majority(r,old.age,&re),la=majority(l,old.age,&le);(void)le;
 int mismatch=0,rf=0,lf=0,linside=0,w1=0,w2=0;
 for(int j=-5;j<=5;j++){
  const int inside=0<=gf+j&&gf+j<Q;
  w1+=inside&&a[x+j].wf1;w2+=inside&&a[x+j].wf2;
  if(j<0){mismatch+=inside&&a[x+j].age!=ra;
   lf+=a[x+j].f2;linside+=inside&&a[x+j].f2;}
  if(j>0)rf+=inside&&a[x+j].f1;
 }
 out.gf=(uint16_t)gf;
 out.f1=!re||mismatch>=3||w1>=3||rf>=3||(old.f1&&rf>=2);
 const int source=w2>=3;
 const int on=linside>=4||(out.f1&&lf>=4)||source;
 const int erase=(!out.f1&&linside<=1)||(out.f1&&lf==0);
 out.f2=old.f2?(source||!erase):on;
 out.age=((!out.f1||out.f2?ra:la)+1)&(U-1);
 out.wf1=out.wf2=0;
 if(96*Q<=out.age&&out.age<98*Q&&gf<=4&&!out.f1)
  out.wf2=(coordinate-gf==0); /* Actual fixed five-copy special Info. */
 return out;
}
int gawn5_cofactor(const Site*a,int centre,Site*out){
 *out=transition(a,8,centre);return 0;
}
int gawn5_campaign(int flags,int limit,int*events,Site*final,Result*out){
 const int offset=-3*Q,n=6*Q;
 Site*a=calloc((size_t)n,sizeof(Site)),*b=calloc((size_t)n,sizeof(Site));
 if(!a||!b){free(a);free(b);return -1;}
 memset(out,0,sizeof(*out));out->min_age_x=0;out->max_age_x=103;
 for(int i=0;i<n;i++){
  int x=offset+i;a[i].gf=(uint16_t)phase(x);a[i].age=T;
  if(0<=x&&x<104){a[i].age=A;a[i].f1=flags&1;a[i].f2=(flags>>1)&1;
   a[i].wf1=(flags>>2)&1;a[i].wf2=(flags>>3)&1;}
 }
 int status=1;
 for(int t=0;t<limit;t++){
  for(int i=0;i<n;i++)b[i]=(Site){.gf=(uint16_t)phase(offset+i),.age=(uint32_t)(T+t+1)};
  int count=0,fc=0,lo=n,hi=-1,boundary=0;
  for(int i=5;i<n-5;i++){
   b[i]=transition(a,i,offset+i);
   if(b[i].age!=(uint32_t)(T+t+1)&&b[i].age!=(uint32_t)(A+t+1)){status=-2;goto done;}
   if(b[i].age!=(uint32_t)(T+t+1)){count++;if(lo==n)lo=i;hi=i;}
   int flag=b[i].f1||b[i].f2||b[i].wf1||b[i].wf2;fc+=flag;
   out->source_updates+=b[i].wf2;
   if((count&&hi==i)||flag)if(i<20||i>=n-20)boundary=1;
  }
  if(boundary){status=-4;goto done;}
  if(count>out->max_age_count)out->max_age_count=count;
  if(count&&hi-lo+1>out->max_age_span)out->max_age_span=hi-lo+1;
  if(count&&offset+lo<out->min_age_x)out->min_age_x=offset+lo;
  if(count&&offset+hi>out->max_age_x)out->max_age_x=offset+hi;
  if(fc>out->max_flag_count)out->max_flag_count=fc;
  if(!count&&!out->age_quiet)out->age_quiet=t+1;
  if(!count&&!fc&&!out->flags_quiet)out->flags_quiet=t+1;
  int*e=events+8*t;e[0]=t+1;e[1]=count;e[2]=count?offset+lo:0;
  e[3]=count?offset+hi:0;e[4]=fc;e[5]=out->source_updates;
  e[6]=b[3*Q].f1;e[7]=b[3*Q].wf2;
  Site*tmp=a;a=b;b=tmp;out->steps=t+1;
  if(!count&&!fc){status=0;break;}
 }
done:
 memcpy(final,a,(size_t)n*sizeof(Site));free(a);free(b);return status;
}
