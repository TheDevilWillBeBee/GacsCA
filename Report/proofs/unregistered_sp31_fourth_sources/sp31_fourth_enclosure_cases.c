/* Prepared fourth enclosure pilots only; physical reachability unproved.
 * The unchanged proved event factor retains all flags and voted Info. */
#define main frozen_first_pulse_main
#include "../sp31_two_flag2_sources.c"
#undef main
int main(int argc,char**argv){
    int mask=argc>1?atoi(argv[1]):0,ticks=argc>2?atoi(argv[2]):6144;
    if(mask<0||mask>=(1<<21)||ticks<1||ticks>6144)return 1;
    static State a,next;static Info m,newm;
    append(&a,148*Q,149*Q-512,2);
    append(&a,149*Q-512,152*Q-512,1);
    append(&a,152*Q-512,152*Q,3);
    for(int col=106;col<=154;col++){
        if(132<=col&&col<=148&&(mask&(1<<(col-132))))m.x[m.n++]=col*Q+3;
        if(149<=col&&col<=151)m.x[m.n++]=col*Q+509;
        if(148<=col&&col<=151&&(mask&(1<<(17+col-148))))m.x[m.n++]=col*Q+515;
        if((106<=col&&col<=147)||(152<=col&&col<=154))m.x[m.n++]=col*Q+1021;
    }
    uint64_t events=0;report(&a,&m,0,events);
    for(int t=0;t<ticks;t++){events+=step(&a,&m,&next,&newm,t);a=next;m=newm;report(&a,&m,t+1,events);}
    printf("{\"fourth_enclosure_mask\":%d,\"endpoint_segments\":[",mask);
    for(int i=0;i<a.n;i++)printf("%s[%d,%d,%u]",i?",":"",a.seg[i].lo,a.seg[i].hi,a.seg[i].v);
    printf("],\"endpoint_Info\":[");for(int i=0;i<m.n;i++)printf("%s%d",i?",":"",m.x[i]);
    puts("],\"exact_event_execution_complete\":true,\"physical_reachability_of_mask_proved\":false,\"all2097152_masks_exhausted\":false}");
    return 0;
}
