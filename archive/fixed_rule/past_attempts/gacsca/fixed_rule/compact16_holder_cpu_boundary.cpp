// A full synchronous physical step, streamed into coherent staged storage.
extern "C" int boundary_step(Local local,const uint64_t *rom,const uint64_t *data,
                              const uint64_t *heads,const uint64_t *where,uint64_t n,uint64_t age,
                              uint64_t *next_data,uint64_t *next_heads,uint64_t *next_where){
 uint64_t in[15*RAW_FIELDS],out[RAW_FIELDS];
 for(uint64_t col=0;col<n;++col)for(unsigned k=0;k<HWORDS;++k)next_heads[col*HWORDS+k]=0;
 for(uint64_t position=0;position<n*Q;++position){
  for(int j=-7;j<=7;++j)raw_input(in+(j+7)*RAW_FIELDS,(position+n*Q+j)%(n*Q),age,rom,data,heads,where,n);
  local(in,out);
  if(out[RAW_ADDRESS]!=position%Q||out[RAW_AGE]!=(age+1)%PERIOD)return -20;
  for(unsigned k=0;k<CONTEXT_WORDS;++k)if(out[RAW_CONTEXT[k]])return -21;
  for(unsigned k=0;k<MAIL_WORDS;++k)if(out[RAW_MAIL[k]])return -22;
  uint64_t col=position/Q,at=position%Q;
  next_data[position]=out[RAW_DATA];
  if(out[RAW_HEAD]){
   if(next_heads[col*HWORDS]||at>=ROM_ROWS)return -23;
   for(unsigned k=0;k<HWORDS;++k)next_heads[col*HWORDS+k]=out[RAW_CONTROL[k]];
   next_where[col]=at;
  }else for(unsigned k=1;k<HWORDS;++k)if(out[RAW_CONTROL[k]])return -24;
 }
 return 0;
}
