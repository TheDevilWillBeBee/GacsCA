/* Diagnostic wrapper only: imports the frozen, unchanged physical evaluator. */
#include "flag_byte_native.cpp"
#include <string>
static thread_local int profile_code=0;
static thread_local std::string profile_message;
static thread_local uint64_t profile_metrics[8];
static void profile_capture(Engine*e){if(!e)return;profile_metrics[0]=e->nodes.size();profile_metrics[1]=e->nodes.capacity();profile_metrics[2]=e->cache.used;profile_metrics[3]=e->cache.values.size();profile_metrics[4]=e->intern.used;profile_metrics[5]=e->intern.values.size();profile_metrics[6]=e->leaf_evaluations;profile_metrics[7]=e->period;}
extern "C" {
Engine* profile_evolve(const uint64_t*runs,size_t nr,size_t colonies,uint64_t age,uint32_t ticks){
 profile_code=0;profile_message.clear();std::fill(profile_metrics,profile_metrics+8,0);
 Engine*e=nullptr;try{
  if(!colonies||colonies>=(UINT64_C(1)<<58)/WORDS||age<98*Q||age>=U||uint64_t(ticks)>U-age||!nr)throw std::runtime_error("invalid domain");
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
  uint64_t quarter=UINT64_C(1)<<(k-2);e->initial=e->build(k,(e->period-quarter%e->period)%e->period);e->final=e->center(e->initial,ticks);profile_capture(e);return e;
 }catch(const std::bad_alloc&){profile_code=1;profile_message="bad_alloc";}
 catch(const std::exception&ex){profile_code=2;profile_message=ex.what();}
 catch(...){profile_code=3;profile_message="unknown exception";}
 profile_capture(e);delete e;return nullptr;
}
int profile_status(uint64_t*out){std::copy(profile_metrics,profile_metrics+8,out);return profile_code;}
const char*profile_error(){return profile_message.c_str();}
}
