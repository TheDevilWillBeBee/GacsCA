/* Compact, exact memoized physical flag light cones, eight sites per leaf.
   Physical rule, ring, and clock domain match flag_byte_hash.py. */
#include <cstdint>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <new>
static constexpr uint32_t LEAVES=1u<<18,MASK=255,FIRST=1u<<16,LAST=1u<<17;
static constexpr uint64_t Q=8388608,WORDS=Q/8,U=128*Q;
struct Table {
 std::vector<uint64_t> keys;std::vector<uint32_t> values;size_t used=0;
 Table():keys(1024),values(1024){}
 static uint64_t hash(uint64_t x){x^=x>>30;x*=UINT64_C(0xbf58476d1ce4e5b9);x^=x>>27;x*=UINT64_C(0x94d049bb133111eb);return x^(x>>31);}
 uint32_t get(uint64_t key)const{size_t i=hash(key)&(values.size()-1);while(values[i]){if(keys[i]==key)return values[i];i=(i+1)&(values.size()-1);}return 0;}
 void add_raw(uint64_t key,uint32_t value){size_t i=hash(key)&(values.size()-1);while(values[i]){if(keys[i]==key){values[i]=value;return;}i=(i+1)&(values.size()-1);}keys[i]=key;values[i]=value;++used;}
 void add(uint64_t key,uint32_t value){if((used+1)*10>values.size()*7){auto k=std::move(keys);auto v=std::move(values);keys.assign(k.size()*2,0);values.assign(v.size()*2,0);used=0;for(size_t i=0;i<v.size();++i)if(v[i])add_raw(k[i],v[i]);}add_raw(key,value);}
};
struct Node {uint32_t left,right,level;};
struct Segment {uint64_t end;uint32_t pattern[8];uint32_t length;};
struct Engine {
 std::vector<Node> nodes;Table intern,cache,init_cache,pattern_cache;std::vector<Segment> segments;uint64_t period,leaf_evaluations=0;uint32_t initial=0,final=0;
 uint32_t level(uint32_t id)const{return id<LEAVES?0:nodes[id-LEAVES].level;}
 Node node(uint32_t id)const{return id<LEAVES?Node{id,id,0}:nodes[id-LEAVES];}
 uint32_t join(uint32_t a,uint32_t b){uint64_t key=(uint64_t(a)<<32)|b;uint32_t found=intern.get(key);if(found)return found-1;
  uint32_t k=level(a);if(k!=level(b)||nodes.size()>=UINT32_MAX-LEAVES-1)throw std::runtime_error("node capacity/level");
  uint32_t out=LEAVES+uint32_t(nodes.size());nodes.push_back({a,b,k+1});intern.add(key,out+1);return out;}
 static uint32_t local(uint32_t l,uint32_t c,uint32_t r){
  uint32_t f=c&255,g=(c>>8)&255,rr[5],ll[5],in[5],erasein=255;
  for(int j=1;j<=5;++j){rr[j-1]=((f>>j)|((r&255)<<(8-j)))&((c&LAST)?(255>>j):255);ll[j-1]=((g<<j)|(((l>>8)&255)>>(8-j)))&255;in[j-1]=(c&FIRST)?ll[j-1]&(255<<j):ll[j-1];erasein&=ll[j-1]|((c&FIRST)?((1u<<j)-1):0);}
  auto counts=[](const uint32_t*x,uint32_t&two,uint32_t&three,uint32_t&four){uint32_t s=x[0]^x[1]^x[2],k=(x[0]&x[1])|(x[0]&x[2])|(x[1]&x[2]),m=(s&x[3])|(s&x[4])|(x[3]&x[4]);two=k|m;three=(k&m)|((s^x[3]^x[4])&(k|m));four=k&m;};
  uint32_t two,three,four;counts(rr,two,three,four);uint32_t nf=three|(f&two);counts(in,two,three,four);uint32_t on=four;counts(ll,two,three,four);on|=nf&four;
  uint32_t erase=(~nf&erasein)|(nf&~(ll[0]|ll[1]|ll[2]|ll[3]|ll[4]));uint32_t ng=((g&~erase)|(~g&on))&255;
  return (c&(FIRST|LAST))|nf|(ng<<8);
 }
 uint32_t center(uint32_t id,uint32_t ticks){Node p=node(id);if(p.level<2||uint64_t(ticks)>(UINT64_C(1)<<(p.level-2)))throw std::runtime_error("causal query");
  if(!ticks)return join(node(p.left).right,node(p.right).left);
  uint64_t key=(uint64_t(id)<<32)|ticks;uint32_t found=cache.get(key);if(found)return found-1;
  uint32_t out;
  if(p.level==2){Node l=node(p.left),r=node(p.right);out=join(local(l.left,l.right,r.left),local(l.right,r.left,r.right));leaf_evaluations+=2;}
  else{uint32_t limit=1u<<(p.level-3),first=std::min(ticks,limit);uint32_t mid=join(node(p.left).right,node(p.right).left);
   uint32_t a=center(p.left,first),b=center(mid,first),c=center(p.right,first);
   if(ticks<=limit)out=join(join(node(a).right,node(b).left),join(node(b).right,node(c).left));
   else out=join(center(join(a,b),ticks-limit),center(join(b,c),ticks-limit));}
  cache.add(key,out+1);return out;
 }
 uint32_t pattern(size_t index,uint32_t k,uint32_t offset){const auto&s=segments[index];offset%=s.length;uint64_t key=(uint64_t(index)<<9)|(uint64_t(k)<<3)|offset;uint32_t found=pattern_cache.get(key);if(found)return found-1;
  uint32_t out;if(!k)out=s.pattern[offset];else out=join(pattern(index,k-1,offset),pattern(index,k-1,(offset+(UINT64_C(1)<<(k-1)))%s.length));pattern_cache.add(key,out+1);return out;}
 uint32_t build(uint32_t k,uint64_t offset){offset%=period;uint64_t key=(offset<<6)|k;uint32_t found=init_cache.get(key);if(found)return found-1;
  size_t i=std::upper_bound(segments.begin(),segments.end(),offset,[](uint64_t v,const Segment&s){return v<s.end;})-segments.begin();
  uint32_t out;if(offset+(UINT64_C(1)<<k)<=segments[i].end)out=pattern(i,k,offset%segments[i].length);
  else{if(!k)throw std::runtime_error("initial partition");uint64_t half=UINT64_C(1)<<(k-1);out=join(build(k-1,offset),build(k-1,(offset+half)%period));}
  init_cache.add(key,out+1);return out;}
};
extern "C" {
void fh_free(Engine*e){delete e;}
uint32_t fh_local(uint32_t l,uint32_t c,uint32_t r){return Engine::local(l,c,r);}
Engine* fh_evolve(const uint64_t*runs,size_t nr,size_t colonies,uint64_t age,uint32_t ticks){
 Engine*e=nullptr;try{
  if(!colonies||colonies>=(UINT64_C(1)<<58)/WORDS||age<98*Q||age>=U||uint64_t(ticks)>U-age||!nr)return nullptr;
  e=new Engine;e->period=colonies*WORDS;std::vector<uint64_t> cuts{0,e->period};uint64_t previous=0;
  for(size_t i=0;i<nr;++i){uint64_t end=runs[3*i];if(end<=previous||end>e->period/8)throw std::runtime_error("word input");cuts.push_back(end*8);previous=end;}
  if(previous!=e->period/8)throw std::runtime_error("incomplete ring");
  for(size_t c=0;c<colonies;++c){cuts.push_back(c*WORDS);cuts.push_back(c*WORDS+1);cuts.push_back((c+1)*WORDS-1);cuts.push_back((c+1)*WORDS);}
  std::sort(cuts.begin(),cuts.end());cuts.erase(std::unique(cuts.begin(),cuts.end()),cuts.end());size_t row=0;
  for(size_t k=0;k+1<cuts.size();++k){uint64_t start=cuts[k],end=cuts[k+1];while(runs[3*row]*8<=start)++row;
   Segment s{};s.end=end;s.length=8;for(int j=0;j<8;++j)s.pattern[j]=uint32_t((runs[3*row+1]>>(8*j))&255)|uint32_t(((runs[3*row+2]>>(8*j))&255)<<8);
   uint32_t tag=(start%WORDS==0?FIRST:0)|(start%WORDS==WORDS-1?LAST:0);if(tag){s.pattern[0]=s.pattern[start%8]|tag;s.length=1;}e->segments.push_back(s);}
  uint32_t k=2;uint64_t need=std::max(uint64_t(ticks),(e->period+1)/2);while((UINT64_C(1)<<(k-2))<need)++k;
  if(k>=34)throw std::runtime_error("time/tree capacity");
  uint64_t quarter=UINT64_C(1)<<(k-2);e->initial=e->build(k,(e->period-quarter%e->period)%e->period);e->final=e->center(e->initial,ticks);return e;
 }catch(...){delete e;return nullptr;}
}
void fh_info(Engine*e,uint64_t*out){out[0]=LEAVES+e->nodes.size();out[1]=e->cache.used;out[2]=e->leaf_evaluations;out[3]=e->initial;out[4]=e->final;}
void fh_nodes(Engine*e,uint64_t*out){for(uint32_t i=0;i<LEAVES;++i){out[3*i]=0;out[3*i+1]=out[3*i+2]=i;}for(size_t i=0;i<e->nodes.size();++i){auto n=e->nodes[i];out[3*(LEAVES+i)]=n.level;out[3*(LEAVES+i)+1]=n.left;out[3*(LEAVES+i)+2]=n.right;}}
void fh_queries(Engine*e,uint64_t*out){size_t n=0;for(size_t i=0;i<e->cache.values.size();++i)if(e->cache.values[i]){out[3*n]=e->cache.keys[i]>>32;out[3*n+1]=uint32_t(e->cache.keys[i]);out[3*n+2]=e->cache.values[i]-1;++n;}}
uint32_t fh_at(Engine*e,uint32_t node,uint64_t pos){if(pos>=(UINT64_C(1)<<e->level(node)))return UINT32_MAX;while(node>=LEAVES){auto n=e->node(node);uint64_t half=UINT64_C(1)<<(n.level-1);if(pos<half)node=n.left;else{pos-=half;node=n.right;}}return node;}
}
