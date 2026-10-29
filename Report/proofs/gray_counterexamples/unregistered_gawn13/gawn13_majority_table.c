/* Exhaustive local cofactors for the written GAWN13 majority identity.
 * Unchanged frozen GAWN10 projection; no CA rule change.
 */
#include "../unregistered_gawn10/gawn10_two_offset_projection.c"

int gawn13_majority_table(uint8_t *outputs){
 const int xs[4]={5,5,Q-1,Q-1};
 const int deltas[4]={1,Q-6,6,Q-6};
 int count=0;
 for(int phase_case=0;phase_case<4;phase_case++){
  for(int gf=0;gf<1024;gf++){
   for(int f1=0;f1<64;f1++){
    for(int workspace1=0;workspace1<2;workspace1++){
     Site raw[17]={{0}};
     for(int j=1;j<=5;j++){
      raw[8-j].foreign=(gf>>(5-j))&1;
      raw[8+j].foreign=(gf>>(4+j))&1;
      raw[8-j].f1=(gf>>(j-1))&1;
      raw[8+j].f1=(f1>>j)&1;
     }
     raw[8].foreign=(gf>>5)&1;raw[8].f1=f1&1;
     for(int j=3;j<=13;j++)raw[j].wf1=workspace1;
     Site out=transition(raw,8,xs[phase_case],deltas[phase_case]);
     outputs[count++]=out.foreign|(out.f1<<1)|(out.f2<<2)|(out.wf1<<3)|(out.wf2<<4);
    }
   }
  }
 }
 return count;
}
