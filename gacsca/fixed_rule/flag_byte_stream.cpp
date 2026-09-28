/* Bounded physical-time continuation. The included engine's physical leaf
   transition is unchanged; only host allocation guards are injected. */
#include <memory>
#include <limits>
#include <cstring>
static thread_local size_t stream_limit=std::numeric_limits<size_t>::max();
#include "flag_stream_engine.h"
#include "flag_stream_audit.h"
struct Stream {
 std::unique_ptr<Engine> state;uint64_t age,time=0,queries=0,leaves=0,rejected=0,chunks=0,peak_nodes=0;
 uint64_t last_ticks=0,last_nodes=0,last_queries=0,live_nodes=0;uint32_t proposal=65536;
 uint8_t one[384],two[768];bool configured=false;uint64_t verified=0;
 bool valid=true;std::string error;
 Stream(Engine*e,uint64_t a):state(e),age(a){live_nodes=e->nodes.size();}
};
static uint32_t copy_node(Engine&to,const Engine&from,uint32_t id,std::vector<uint32_t>&mapped){
 if(id<LEAVES)return id;
 uint32_t &out=mapped[id-LEAVES];if(out!=UINT32_MAX)return out;
 auto n=from.node(id);uint32_t l=copy_node(to,from,n.left,mapped),r=copy_node(to,from,n.right,mapped);out=to.join(l,r);return out;
}
static std::unique_ptr<Engine> clone_state(const Engine&from){
 auto to=std::make_unique<Engine>();to->period=from.period;
 std::vector<uint32_t> mapped(from.nodes.size(),UINT32_MAX);to->final=copy_node(*to,from,from.final,mapped);to->initial=to->final;return to;
}
static uint32_t slice(Engine&e,uint32_t node,uint32_t k,uint64_t offset){
 auto n=e.node(node);uint64_t size=UINT64_C(1)<<k;
 if(k>n.level||offset+size>(UINT64_C(1)<<n.level))throw std::runtime_error("slice range");
 if(k==n.level){if(offset)throw std::runtime_error("slice alignment");return node;}
 uint64_t half=UINT64_C(1)<<(n.level-1);
 if(offset+size<=half)return slice(e,n.left,k,offset);
 if(offset>=half)return slice(e,n.right,k,offset-half);
 if(!k)throw std::runtime_error("split leaf");
 uint32_t l=slice(e,node,k-1,offset),r=slice(e,node,k-1,offset+(size>>1));return e.join(l,r);
}
static uint32_t periodic(Engine&e,uint32_t source,uint32_t k,uint64_t offset){
 offset%=e.period;uint64_t key=(offset<<6)|k;uint32_t cached=e.init_cache.get(key);if(cached)return cached-1;
 uint64_t size=UINT64_C(1)<<k;uint32_t out;
 if(offset+size<=e.period)out=slice(e,source,k,offset);
 else{if(!k)throw std::runtime_error("periodic split");uint32_t l=periodic(e,source,k-1,offset),r=periodic(e,source,k-1,(offset+(size>>1))%e.period);out=e.join(l,r);}
 e.init_cache.add(key,out+1);return out;
}
extern "C" {
Stream*fs_create(const uint64_t*runs,size_t nr,size_t colonies,uint64_t age){
 stream_limit=std::numeric_limits<size_t>::max();Engine*e=fh_evolve(runs,nr,colonies,age,0);if(!e)return nullptr;
 try{return new Stream(e,age);}catch(...){delete e;return nullptr;}
}
void fs_free(Stream*s){delete s;}
void fs_tables(Stream*s,const uint8_t*one,const uint8_t*two){std::copy(one,one+384,s->one);std::copy(two,two+768,s->two);s->configured=true;}
/* One accepted chunk, retried with shorter physical duration on a host budget
   exception. Failed trials cannot change the last committed physical state. */
int fs_advance(Stream*s,uint32_t requested,size_t budget){
 if(!s||!s->valid||!s->configured||!requested||requested>U-s->age||budget<1024)return -1;
 uint32_t ticks=requested;
 for(;;){
  try{
   stream_limit=std::numeric_limits<size_t>::max();auto e=clone_state(*s->state);stream_limit=budget;
   uint32_t source=e->final,k=2;uint64_t need=std::max(uint64_t(ticks),(e->period+1)/2);while((UINT64_C(1)<<(k-2))<need)++k;
   if(k>=34)throw std::runtime_error("tree capacity");
   uint64_t quarter=UINT64_C(1)<<(k-2);e->initial=periodic(*e,source,k,(e->period-quarter%e->period)%e->period);e->final=e->center(e->initial,ticks);
   uint64_t verified=audit_trial(*e,source,ticks,s->one,s->two);
   s->last_nodes=e->nodes.size();s->last_queries=e->cache.used;s->peak_nodes=std::max(s->peak_nodes,s->last_nodes);
   s->queries+=e->cache.used;s->leaves+=e->leaf_evaluations;
   stream_limit=std::numeric_limits<size_t>::max();auto next=clone_state(*e);s->live_nodes=next->nodes.size();
   s->state=std::move(next);s->verified+=verified;s->age+=ticks;s->time+=ticks;++s->chunks;s->last_ticks=ticks;s->error.clear();return 0;
  }catch(const std::bad_alloc&){s->error="allocation failure";}
   catch(const std::exception&ex){s->error=ex.what();if(s->error!="host node budget"&&s->error!="host table budget")return -3;}
  ++s->rejected;
  if(ticks==1)return -2;
  ticks=std::max(1u,ticks/2);
 }
}
void fs_info(Stream*s,uint64_t*out){uint64_t values[]={s->age%U,s->time,s->chunks,s->rejected,s->queries,s->leaves,s->peak_nodes,s->live_nodes,s->last_ticks,s->last_nodes,s->last_queries,s->state->period,s->state->final,s->verified};std::copy(values,values+14,out);}
const char*fs_error(Stream*s){return s?s->error.c_str():"invalid stream";}
uint32_t fs_at(Stream*s,uint64_t position){if(!s||!s->valid||position>=s->state->period)return UINT32_MAX;return fh_at(s->state.get(),s->state->final,position);}
void fs_nodes(Stream*s,uint64_t*out){fh_nodes(s->state.get(),out);}
}
