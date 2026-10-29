/* Exact finite pilot of the twelve-bit third enclosure. Not a physical
 * reachability claim or an exhaustive4096-case certificate. Frozen factor
 * includes all native flags and actual special-Info erasure. */
#define main sp31_frozen_first_pulse_main
#include "../sp31_two_flag2_sources.c"
#undef main
int main(int argc,char **argv){
    int mask=argc>1?atoi(argv[1]):0,ticks=argc>2?atoi(argv[2]):6144;
    if(mask<0||mask>=4096||ticks<1||ticks>6144)return 1;
    static State a,next;static Info m,newm;
    append(&a,141*Q,142*Q-512,2);
    append(&a,142*Q-512,149*Q-512,1);
    append(&a,149*Q-512,149*Q,3);
    for(int col=112;col<=151;col++){
        if(131<=col&&col<=141&&(mask&(1<<(col-131))))m.x[m.n++]=col*Q+3;
        if(142<=col&&col<=148)m.x[m.n++]=col*Q+509;
        if(col==148&&(mask&(1<<11)))m.x[m.n++]=col*Q+515;
        if((112<=col&&col<=140)||(149<=col&&col<=151))m.x[m.n++]=col*Q+1021;
    }
    uint64_t events=0;report(&a,&m,0,events);
    for(int t=0;t<ticks;t++){
        events+=step(&a,&m,&next,&newm,t);a=next;m=newm;report(&a,&m,t+1,events);
    }
    printf("{\"third_enclosure_mask\":%d,\"endpoint_segments\":[",mask);
    for(int i=0;i<a.n;i++)printf("%s[%d,%d,%u]",i?",":"",a.seg[i].lo,a.seg[i].hi,a.seg[i].v);
    printf("],\"endpoint_Info\":[");
    for(int i=0;i<m.n;i++)printf("%s%d",i?",":"",m.x[i]);
    printf("],\"exact_event_execution_complete\":true,\"physical_reachability_of_mask_proved\":false,\"all4096_masks_exhausted\":false}\n");
    return 0;
}
