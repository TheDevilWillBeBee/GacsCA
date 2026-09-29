// Portable physical controller events. Included after generated constants/helpers.
using Local = void(*)(const uint64_t*,uint64_t*);
struct World {const uint64_t *rom;};
uint64_t meta(World w,uint64_t a,unsigned k){return w.rom[7*a+k];}
// DISTANCE_FUNCTION
static void raw_input(uint64_t *out,uint64_t position,uint64_t age,const uint64_t *rom,
                      const uint64_t *data,const uint64_t *heads,const uint64_t *where,uint64_t n){
 const uint64_t size=n*Q;
 for(unsigned k=0;k<RAW_FIELDS;++k){
  int kind=RAW_KIND[k],arg=RAW_ARG[k];
  uint64_t primary=(position+size+RAW_OFFSET[k])%size,a=primary%Q,col=primary/Q;
  if(kind==0)out[k]=rom[7*a+arg];
  else if(kind==1)out[k]=data[primary];
  else if(kind==2)out[k]=(where[col]==a)?heads[col*HWORDS+arg]:0;
  else if(kind==3)out[k]=position%Q;
  else if(kind==4)out[k]=age;
  else out[k]=0;
 }
}
extern "C" int run_events(Local local,const uint64_t *rom,uint64_t *data,uint64_t *heads,
                           uint64_t *where,uint64_t n,uint64_t age,uint64_t ticks,
                           uint64_t event_budget,uint64_t *metrics){
 World w{rom};
 uint64_t in[15*RAW_FIELDS],out[RAW_FIELDS];
 metrics[0]=metrics[1]=metrics[2]=0;
 for(uint64_t col=0;col<n;++col){
  uint64_t *h=heads+col*HWORDS,elapsed=0,events=0;
  while(elapsed<ticks&&h[0]){
   if(where[col]>=ROM_ROWS)return -1;
   uint64_t jump=independent_distance(w,where[col],h),remaining=ticks-elapsed;
   if(jump>remaining)jump=remaining;
   if(jump){
    // Travel only between literal local evaluations of the physical rule.
    if(h[P_DIRECTION-P_HEAD])where[col]-=jump;else where[col]+=jump;
    elapsed+=jump;metrics[1]+=jump;continue;
   }
   if(events>=event_budget)return -2;
   uint64_t next[HWORDS]={0},next_at=0,next_heads=0;
   uint64_t points[3],values[3];unsigned used=0;
   for(int delta=-1;delta<=1;++delta){
    int64_t at=(int64_t)where[col]+delta;
    if(at<0||at>=(int64_t)ROM_ROWS)continue;
    uint64_t position=col*Q+at;
    for(int j=-7;j<=7;++j)raw_input(in+(j+7)*RAW_FIELDS,(position+n*Q+j)%(n*Q),age+elapsed,rom,data,heads,where,n);
    local(in,out);++metrics[2];
    for(unsigned k=0;k<MAIL_WORDS;++k)if(out[RAW_MAIL[k]])return -3;
    if(out[RAW_HEAD]){
     ++next_heads;next_at=at;
     for(unsigned k=0;k<HWORDS;++k)next[k]=out[RAW_CONTROL[k]];
    }else for(unsigned k=1;k<HWORDS;++k)if(out[RAW_CONTROL[k]])return -4;
    points[used]=position;values[used++]=out[RAW_DATA];
   }
   if(next_heads>1)return -5;
   for(unsigned k=0;k<used;++k){
    if(points[k]%Q>=MEM_ROWS && values[k])return -6;
    data[points[k]]=values[k];
   }
   for(unsigned k=0;k<HWORDS;++k)h[k]=next[k];
   where[col]=next_at;++elapsed;++events;
  }
  metrics[0]+=events;
 }
 return 0;
}
