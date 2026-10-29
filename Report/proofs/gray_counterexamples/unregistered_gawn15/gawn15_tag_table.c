/* Supplement to the separately proved exact positive-tail tag induction. */
#include <stdint.h>
#include <string.h>
#include "../unregistered_gawn10/gawn10_two_offset_projection.c"
static const int pairs[10][2]={{Q-1,1},{Q-2,2},{1,Q-1},{5,Q-1},
 {Q-6,Q-1},{Q-3,Q-1},{Q-1,Q-1},{Q-104,104},{Q-100,104},{Q-6,104}};
int gawn15_tag_table(uint8_t*out){
 int n=0;
 for(int k=0;k<10;k++)for(int left=0;left<32;left++)
 for(int right=0;right<32;right++)for(int flags=0;flags<64;flags++){
  const int x=pairs[k][0],delta=pairs[k][1];Site a[17];memset(a,0,sizeof(a));
  a[8].f1=flags&1;
  for(int j=1;j<=5;j++){
   a[8-j].foreign=(left>>(j-1))&1;
   if(x+j<Q){a[8+j].foreign=(right>>(j-1))&1;a[8+j].f1=(flags>>j)&1;}
  }
  Site z=transition(a,8,x,delta);
  if(z.f2||z.wf1||z.wf2)return -1;
  out[n++]=z.foreign|(z.f1<<1);
 }
 return n;
}
