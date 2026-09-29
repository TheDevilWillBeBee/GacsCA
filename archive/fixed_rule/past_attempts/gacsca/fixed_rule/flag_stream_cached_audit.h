/* Independent verification of one ephemeral physical spacetime derivation.
   Leaf tables come from the complete delivery native local rule, not Engine::local.
   All dependency equations decrease spatial level, so verification order need
   not follow native hash bucket order. No node or query is created by this audit. */
#include <unordered_set>
struct SeenPosition {uint32_t node;uint64_t offset;bool operator==(const SeenPosition&x)const{return node==x.node&&offset==x.offset;}};
struct SeenHash {size_t operator()(const SeenPosition&x)const{return Table::hash(x.offset)^Table::hash(x.node);}};
static uint32_t checked_join(const Engine&e,uint32_t left,uint32_t right){
 uint32_t out=e.intern.get((uint64_t(left)<<32)|right);if(!out)throw std::runtime_error("audit missing join");return out-1;
}
static uint32_t checked_query(const Engine&e,uint32_t node,uint32_t ticks){
 uint32_t out=e.cache.get((uint64_t(node)<<32)|ticks);if(!out)throw std::runtime_error("audit missing subquery");return out-1;
}
static uint32_t table_leaf(uint32_t a,uint32_t b,uint32_t c,const uint8_t*one,const uint8_t*two){
 if((b&FIRST)&&(b&LAST))throw std::runtime_error("audit invalid geometry tags");
 uint32_t f=(a&255)|((b&255)<<8)|((c&255)<<16),g=((a>>8)&255)|(((b>>8)&255)<<8)|(((c>>8)&255)<<16),out=b&(FIRST|LAST);
 for(unsigned bit=0;bit<8;++bit){unsigned pos=8+bit,rs=0,ls=0;
  for(unsigned j=1;j<=5;++j){rs|=((f>>(pos+j))&1)<<(j-1);ls|=((g>>(pos-j))&1)<<(j-1);}
  unsigned ar=(b&LAST)?std::min(5u,7-bit):5,al=(b&FIRST)?std::min(5u,bit):5;
  unsigned nf=one[(ar*2+((f>>pos)&1))*32+rs];
  unsigned ng=two[((al*2+((g>>pos)&1))*2+nf)*32+ls];out|=nf<<bit;out|=ng<<(8+bit);
 }return out;
}
static bool inside_equal(const Engine&e,uint32_t out,uint32_t source,uint64_t offset){
 auto a=e.node(out),b=e.node(source);uint64_t width=UINT64_C(1)<<a.level;
 if(a.level>b.level||offset+width>(UINT64_C(1)<<b.level))return false;
 if(a.level==b.level)return offset==0&&out==source;
 uint64_t half=UINT64_C(1)<<(b.level-1);
 if(offset+width<=half)return inside_equal(e,out,b.left,offset);
 if(offset>=half)return inside_equal(e,out,b.right,offset-half);
 if(!a.level)return false;
 return inside_equal(e,a.left,source,offset)&&inside_equal(e,a.right,source,offset+(width>>1));
}
static bool periodic_equal(const Engine&e,uint32_t out,uint32_t source,uint64_t offset,std::unordered_set<SeenPosition,SeenHash>&seen){
 offset%=e.period;if(!seen.insert({out,offset}).second)return true;
 auto a=e.node(out);uint64_t width=UINT64_C(1)<<a.level;
 if(offset+width<=e.period)return inside_equal(e,out,source,offset);
 if(!a.level)return false;
 return periodic_equal(e,a.left,source,offset,seen)&&periodic_equal(e,a.right,source,(offset+(width>>1))%e.period,seen);
}
static uint64_t audit_trial(const Engine&e,uint32_t source,uint32_t ticks,const uint8_t*one,const uint8_t*two,const Table&certified){
 for(size_t i=0;i<e.nodes.size();++i){auto n=e.nodes[i];uint32_t id=LEAVES+uint32_t(i);
  if(n.left>=id||n.right>=id||e.level(n.left)!=n.level-1||e.level(n.right)!=n.level-1||checked_join(e,n.left,n.right)!=id)throw std::runtime_error("audit node DAG");}
 auto initial=e.node(e.initial);if(initial.level<2)throw std::runtime_error("audit initial size");
 std::unordered_set<SeenPosition,SeenHash> seen;uint64_t quarter=UINT64_C(1)<<(initial.level-2);
 if(!periodic_equal(e,e.initial,source,(e.period-quarter%e.period)%e.period,seen))throw std::runtime_error("audit periodic initial state");
 uint64_t checked=0;
 for(size_t i=0;i<e.cache.values.size();++i)if(e.cache.values[i]){
  uint32_t proven=certified.get(e.cache.keys[i]);
  if(proven){if(proven!=e.cache.values[i])throw std::runtime_error("audit certificate conflict");continue;}
  uint32_t id=e.cache.keys[i]>>32,t=uint32_t(e.cache.keys[i]),out=e.cache.values[i]-1;auto p=e.node(id);
  if(p.level<2||!t||uint64_t(t)>(UINT64_C(1)<<(p.level-2)))throw std::runtime_error("audit causal interval");
  uint32_t expected;
  if(p.level==2){auto l=e.node(p.left),r=e.node(p.right);expected=checked_join(e,table_leaf(l.left,l.right,r.left,one,two),table_leaf(l.right,r.left,r.right,one,two));}
  else{uint32_t limit=1u<<(p.level-3),first=std::min(t,limit),middle=checked_join(e,e.node(p.left).right,e.node(p.right).left);
   uint32_t a=checked_query(e,p.left,first),b=checked_query(e,middle,first),c=checked_query(e,p.right,first);
   if(t<=limit)expected=checked_join(e,checked_join(e,e.node(a).right,e.node(b).left),checked_join(e,e.node(b).right,e.node(c).left));
   else expected=checked_join(e,checked_query(e,checked_join(e,a,b),t-limit),checked_query(e,checked_join(e,b,c),t-limit));}
  if(out!=expected)throw std::runtime_error("audit physical query result");
  ++checked;
 }
 if(checked_query(e,e.initial,ticks)!=e.final)throw std::runtime_error("audit final state");
 return checked;
}
