/* Native cofactor supplement to the written arbitrary-Flag2 tag proof. */
#include <stdint.h>
#include <string.h>
#include "../unregistered_gawn10/gawn10_two_offset_projection.c"
static const int pairs[6][2]={{-8,8},{-6,8},{-3,8},{-1,1},{1,1},{4,1}};
int gawn16_tag_table(uint8_t*out){
 int n=0;
 for(int k=0;k<6;k++)for(int left=0;left<32;left++)
 for(int right=0;right<32;right++)for(int flags=0;flags<64;flags++)
 for(int f2=0;f2<64;f2++)for(int ws=0;ws<2;ws++){
  Site a[17];memset(a,0,sizeof(a));a[8].f1=(flags>>5)&1;a[8].f2=(f2>>5)&1;
  for(int j=1;j<=5;j++){
   a[8-j].foreign=(left>>(j-1))&1;a[8+j].foreign=(right>>(j-1))&1;
   a[8+j].f1=(flags>>(j-1))&1;a[8-j].f2=(f2>>(j-1))&1;
  }
  for(int j=0;j<17;j++)a[j].wf1=a[j].wf2=ws;
  Site z=transition(a,8,pairs[k][0],pairs[k][1]);
  if(z.wf1||z.wf2)return -1;
  out[n++]=z.foreign|(z.f1<<1)|(z.f2<<2);
 }
 return n;
}
