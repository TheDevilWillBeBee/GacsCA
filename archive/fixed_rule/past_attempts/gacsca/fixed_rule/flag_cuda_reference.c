/* CPU comparison only; no role in GPU evolution. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define FLAG_INLINE static inline
#include "flag_word_generated.h"
int flag_reference(const uint64_t*input,uint64_t*output,uint64_t words,uint64_t ticks){
 if(!words||words%M)return -1;
 size_t bytes=words*2*sizeof(uint64_t);uint64_t*a=malloc(bytes),*b=malloc(bytes);
 if(!a||!b){free(a);free(b);return -2;}memcpy(a,input,bytes);
 for(uint64_t t=0;t<ticks;++t){
  for(uint64_t j=0;j<words;++j){uint64_t l=j?j-1:words-1,r=j+1==words?0:j+1;
   uint64_t in[6]={a[2*l],a[2*l+1],a[2*j],a[2*j+1],a[2*r],a[2*r+1]};
   fw_word(in,b+2*j,j%M==0,j%M==M-1,0,0,0);
  }uint64_t*tmp=a;a=b;b=tmp;
 }memcpy(output,a,bytes);free(a);free(b);return 0;
}
