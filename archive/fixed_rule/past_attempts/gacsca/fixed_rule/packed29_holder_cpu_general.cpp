// Literal full-F boundary with both coherent Signal sides and arbitrary flags.
static uint64_t flag_at(const uint64_t *flags,uint64_t position,unsigned kind){
 return (flags[2*(position/64)+kind]>>(position%64))&1;
}
static uint64_t signal_at(uint64_t a,uint64_t right,uint64_t left){
 return (a>=Q-5?right<<(Q-1-a):0)|(a>=1&&a<=5?left<<(5-a):0);
}
static void general_input(uint64_t*out,uint64_t position,uint64_t age,const uint64_t*rom,
                          const uint64_t*data,const uint64_t*heads,const uint64_t*where,
                          uint64_t n,const uint64_t*right,const uint64_t*left,const uint64_t*flags){
 raw_input(out,position,age,rom,data,heads,where,n);
 out[RAW_F1]=flag_at(flags,position,0);out[RAW_F2]=flag_at(flags,position,1);
 out[RAW_SIGNAL]=signal_at(position%Q,right[position/Q],left[position/Q]);
 for(int d=-2;d<=2;++d){uint64_t primary=(position+n*Q+d)%(n*Q),col=primary/Q,a=primary%Q;
  bool on=age>=WF_START&&age<WF_END;
  out[RAW_WF1[d+2]]=on&&a>=Q-5&&right[col];
  out[RAW_WF2[d+2]]=on&&a<=4&&left[col]&&!flag_at(flags,primary,0);
 }
}
extern "C" int general_step(Local local,const uint64_t *rom,const uint64_t *data,
                              const uint64_t *heads,const uint64_t *where,uint64_t n,uint64_t age,
                              const uint64_t *right,const uint64_t *left,const uint64_t *flags,
                              uint64_t *next_data,uint64_t *next_heads,uint64_t *next_where,
                              uint64_t *next_right,uint64_t *next_left,uint64_t *next_flags){
 uint64_t in[15*RAW_FIELDS],out[RAW_FIELDS],next_age=(age+1)%PERIOD;
 for(uint64_t k=0;k<n*Q/32;++k)next_flags[k]=0;
 for(uint64_t col=0;col<n;++col){next_right[col]=UINT64_MAX;next_left[col]=UINT64_MAX;
  for(unsigned k=0;k<HWORDS;++k)next_heads[col*HWORDS+k]=0;
 }
 for(uint64_t position=0;position<n*Q;++position){
  for(int j=-7;j<=7;++j)general_input(in+(j+7)*RAW_FIELDS,(position+n*Q+j)%(n*Q),age,rom,data,heads,where,n,right,left,flags);
  local(in,out);uint64_t col=position/Q,at=position%Q;
  if(out[RAW_ADDRESS]!=at||out[RAW_AGE]!=next_age)return -40;
  if(out[RAW_F1]>1||out[RAW_F2]>1)return -41;
  next_flags[2*(position/64)]|=out[RAW_F1]<<(position%64);
  next_flags[2*(position/64)+1]|=out[RAW_F2]<<(position%64);
  uint64_t signal=out[RAW_SIGNAL];
  bool isleft=at>=1&&at<=5,isright=at>=Q-5;
  if(!isleft&&!isright){if(signal)return -42;}
  else{
   uint64_t mask=signal_at(at,isright,isleft);if(signal!=0&&signal!=mask)return -43;
   uint64_t value=signal!=0,*dest=isleft?next_left+col:next_right+col;
   if(*dest!=UINT64_MAX&&*dest!=value)return -44;
   *dest=value;
   if(age!=CAPTURE-1&&value!=(isleft?left[col]:right[col]))return -45;
  }
  for(unsigned k=0;k<MAIL_WORDS;++k)if(out[RAW_MAIL[k]])return -46;
  next_data[position]=out[RAW_DATA];
  if(out[RAW_HEAD]){
   if(next_heads[col*HWORDS]||at>=ROM_ROWS)return -47;
   for(unsigned k=0;k<HWORDS;++k)next_heads[col*HWORDS+k]=out[RAW_CONTROL[k]];
   next_where[col]=at;
  }else for(unsigned k=1;k<HWORDS;++k)if(out[RAW_CONTROL[k]])return -48;
 }
 return 0;
}
