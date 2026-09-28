// Emitted payloads and protected-target packet transport. Complete F at heads.
#include <vector>
#include <algorithm>
struct Packet {uint64_t birth,pos,track,target,data,remaining;};
static bool protected_target(uint64_t a){return a<Q&&PROTECTED[a];}

static bool protected_access(uint64_t at,const uint64_t*h){
 if(!protected_target(at)||h[P_DIRECTION-P_HEAD])return false;
 uint64_t phase=h[P_PHASE-P_HEAD];
 return ((phase==1||phase==4||phase==5)&&h[P_RA-P_HEAD]==at)||
        (phase==2&&h[P_RB-P_HEAD]==at)||(phase==3&&h[P_RD-P_HEAD]==at);
}
static uint64_t hit_distance(const Packet&p){
 int64_t at=p.pos%Q;
 int64_t distance=p.remaining*Q+(p.track==0?at-(int64_t)p.target:(int64_t)p.target-at);
 return distance>0?(uint64_t)distance:UINT64_MAX;
}
static uint64_t drop_distance(const Packet&p){return p.remaining*Q+(p.track==0?p.pos%Q+1:Q-p.pos%Q);}
static uint64_t lifetime(const Packet&p){return std::min(hit_distance(p),drop_distance(p));}
static uint64_t moved(const Packet&p,uint64_t ticks,uint64_t size){
 int64_t at=(int64_t)p.pos+(p.track==0?-(int64_t)ticks:(int64_t)ticks);
 at%=(int64_t)size;return at<0?at+size:at;
}
static uint64_t line(const Packet&p,uint64_t size){
 int64_t at=(int64_t)p.pos+(p.track==0?(int64_t)p.birth:-(int64_t)p.birth);
 at%=(int64_t)size;return at<0?at+size:at;
}
extern "C" int run_gather(Local local,const uint64_t *rom,uint64_t *data,uint64_t *heads,
                           uint64_t *where,uint64_t n,uint64_t age,uint64_t ticks,
                           uint64_t event_budget,const uint64_t *initial,uint64_t initial_count,
                           uint64_t *live,uint64_t capacity,uint64_t *live_count,uint64_t *metrics){
 World w{rom};std::vector<Packet> packets;packets.reserve(capacity);
 for(uint64_t k=0;k<6;++k)metrics[k]=0;
 auto add=[&](Packet packet){
  if(packet.pos>=n*Q||packet.track>1||packet.remaining>7||!protected_target(packet.target))return false;
  if(meta(w,packet.target,0)!=0||meta(w,packet.target,1)!=packet.target||packets.size()>=capacity)return false;
  packets.push_back(packet);return true;
 };
 for(uint64_t k=0;k<initial_count;++k){const uint64_t *row=initial+5*k;
  if(!add({0,row[0],row[1],row[2],row[3],row[4]}))return -10;
 }
 uint64_t in[15*RAW_FIELDS],out[RAW_FIELDS];
 for(uint64_t col=0;col<n;++col){
  uint64_t *h=heads+col*HWORDS,elapsed=0,events=0;
  while(elapsed<ticks&&h[0]){
   if(where[col]>=ROM_ROWS)return -1;
   uint64_t jump=std::min(independent_distance(w,where[col],h),ticks-elapsed);
   if(jump){if(h[P_DIRECTION-P_HEAD])where[col]-=jump;else where[col]+=jump;elapsed+=jump;metrics[1]+=jump;continue;}
   if(events>=event_budget)return -2;
   if(protected_access(where[col],h))return -11;
   uint64_t next[HWORDS]={0},next_at=0,next_heads=0,points[3],values[3];unsigned used=0;
   for(int delta=-1;delta<=1;++delta){
    int64_t at=(int64_t)where[col]+delta;if(at<0||at>=(int64_t)ROM_ROWS)continue;
    uint64_t position=col*Q+at;
    for(int j=-7;j<=7;++j)raw_input(in+(j+7)*RAW_FIELDS,(position+n*Q+j)%(n*Q),age+elapsed,rom,data,heads,where,n);
    local(in,out);++metrics[2];
    for(unsigned track=0;track<2;++track){
     uint64_t words[4];for(unsigned k=0;k<4;++k)words[k]=out[RAW_PACKET[track][k]];
     if(words[3]){
      if(!add({elapsed+1,position,track,words[0],words[1],words[2]}))return -12;
      ++metrics[3];
     }else if(words[0]||words[1]||words[2])return -13;
    }
    if(out[RAW_HEAD]){++next_heads;next_at=at;for(unsigned k=0;k<HWORDS;++k)next[k]=out[RAW_CONTROL[k]];}
    else for(unsigned k=1;k<HWORDS;++k)if(out[RAW_CONTROL[k]])return -4;
    points[used]=position;values[used++]=out[RAW_DATA];
   }
   if(next_heads>1)return -5;
   for(unsigned k=0;k<used;++k){if(points[k]%Q>=MEM_ROWS&&values[k])return -6;data[points[k]]=values[k];}
   for(unsigned k=0;k<HWORDS;++k)h[k]=next[k];
   where[col]=next_at;++elapsed;++events;
  }
  metrics[0]+=events;
 }
 // Exclude an overlapping later birth on every actual ring world-line.
 std::sort(packets.begin(),packets.end(),[&](const Packet&a,const Packet&b){
  if(a.track!=b.track)return a.track<b.track;
  uint64_t x=line(a,n*Q),y=line(b,n*Q);return x!=y?x<y:a.birth<b.birth;
 });
 for(size_t k=1;k<packets.size();++k){const Packet&a=packets[k-1],&b=packets[k];
  if(a.track==b.track&&line(a,n*Q)==line(b,n*Q)&&b.birth<a.birth+lifetime(a))return -14;
 }
 struct Delivery {uint64_t time,pos,track,data;};std::vector<Delivery> deliveries;*live_count=0;
 for(const Packet&packet:packets){
  uint64_t elapsed=ticks-packet.birth,hit=hit_distance(packet),drop=drop_distance(packet);
  if(hit<drop&&hit<=elapsed){deliveries.push_back({packet.birth+hit,moved(packet,hit,n*Q),packet.track,packet.data});++metrics[4];}
  else if(drop<=elapsed)++metrics[5];
  if(elapsed<lifetime(packet)){
   uint64_t crossed=packet.track==0?(elapsed+Q-1-packet.pos%Q)/Q:(elapsed+packet.pos%Q)/Q;
   if(crossed>packet.remaining||*live_count>=capacity)return -15;
   uint64_t *row=live+5*(*live_count)++;
   row[0]=moved(packet,elapsed,n*Q);row[1]=packet.track;row[2]=packet.target;row[3]=packet.data;row[4]=packet.remaining-crossed;
  }
 }
 std::sort(deliveries.begin(),deliveries.end(),[](const Delivery&a,const Delivery&b){
  if(a.time!=b.time)return a.time<b.time;
  if(a.pos!=b.pos)return a.pos<b.pos;
  return a.track<b.track;
 });
 // Later delivery wins; at equal time the right track wins, as in F.
 for(const Delivery&delivery:deliveries)data[delivery.pos]=delivery.data;
 return 0;
}
