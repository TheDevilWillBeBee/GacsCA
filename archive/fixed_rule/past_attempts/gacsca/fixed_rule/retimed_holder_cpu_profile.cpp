// Exact mixed-right/left-zero Signal family with its proved flag trajectory.
static uint64_t signal_at(uint64_t a,uint64_t right){return a>=Q-5?right<<(Q-1-a):0;}
static uint64_t flag_at(uint64_t age,uint64_t a,uint64_t right){
 if(!right||age<=WF_START)return 0;
 if(age<=WF_END){uint64_t moved=3*(age-WF_START-1),lo=moved>=Q-8?0:Q-8-moved;return a>=lo;}
 uint64_t moved=2*(age-WF_END),hi=moved>=Q?0:Q-moved;return a<hi;
}
static uint64_t wf_at(uint64_t age,uint64_t a,uint64_t right){return right&&age>=WF_START&&age<WF_END&&a>=Q-5;}
static void profile_input(uint64_t*out,uint64_t position,uint64_t age,const uint64_t*rom,
                          const uint64_t*data,const uint64_t*heads,const uint64_t*where,
                          uint64_t n,const uint64_t*right){
 raw_input(out,position,age,rom,data,heads,where,n);
 out[RAW_F1]=flag_at(age,position%Q,right[position/Q]);
 out[RAW_SIGNAL]=signal_at(position%Q,right[position/Q]);
 for(int d=-2;d<=2;++d){uint64_t primary=(position+n*Q+d)%(n*Q);out[RAW_WF1[d+2]]=wf_at(age,primary%Q,right[primary/Q]);}
}
extern "C" int profile_step(Local local,const uint64_t *rom,const uint64_t *data,
                              const uint64_t *heads,const uint64_t *where,uint64_t n,uint64_t age,
                              const uint64_t *right,uint64_t *next_data,uint64_t *next_heads,
                              uint64_t *next_where,uint64_t *next_right){
 uint64_t in[15*RAW_FIELDS],out[RAW_FIELDS],next_age=(age+1)%PERIOD;
 for(uint64_t col=0;col<n;++col){next_right[col]=UINT64_MAX;for(unsigned k=0;k<HWORDS;++k)next_heads[col*HWORDS+k]=0;}
 for(uint64_t position=0;position<n*Q;++position){
  for(int j=-7;j<=7;++j)profile_input(in+(j+7)*RAW_FIELDS,(position+n*Q+j)%(n*Q),age,rom,data,heads,where,n,right);
  local(in,out);uint64_t col=position/Q,at=position%Q;
  if(out[RAW_ADDRESS]!=at||out[RAW_AGE]!=next_age)return -30;
  if(out[RAW_F2]||out[RAW_F1]!=flag_at(next_age,at,right[col]))return -31;
  for(int d=-2;d<=2;++d){uint64_t primary=(position+n*Q+d)%(n*Q);
   if(out[RAW_WF2[d+2]]||out[RAW_WF1[d+2]]!=wf_at(next_age,primary%Q,right[primary/Q]))return -32;
  }
  uint64_t signal=out[RAW_SIGNAL];
  if(at<Q-5){if(signal)return -33;}
  else{
   uint64_t mask=signal_at(at,1);if(signal!=0&&signal!=mask)return -34;
   uint64_t value=signal!=0;
   if(next_right[col]!=UINT64_MAX&&next_right[col]!=value)return -35;
   next_right[col]=value;
   if(age!=CAPTURE-1&&value!=right[col])return -36;
  }
  for(unsigned k=0;k<MAIL_WORDS;++k)if(out[RAW_MAIL[k]])return -37;
  next_data[position]=out[RAW_DATA];
  if(out[RAW_HEAD]){
   if(next_heads[col*HWORDS]||at>=ROM_ROWS)return -38;
   for(unsigned k=0;k<HWORDS;++k)next_heads[col*HWORDS+k]=out[RAW_CONTROL[k]];
   next_where[col]=at;
  }else for(unsigned k=1;k<HWORDS;++k)if(out[RAW_CONTROL[k]])return -39;
 }
 return 0;
}
