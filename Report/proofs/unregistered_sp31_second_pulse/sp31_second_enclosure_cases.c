/* Analysis quotient only. The included F31 binary-GF/common-clock
 * native/Info transition is unchanged. This supplies selected members
 * of J229's source enclosure, not their physical reachability. */
#define main sp31_previous_first_pulse_main
#include "../sp31_two_flag2_sources.c"
#undef main
int main(int argc,char **argv){
    unsigned mask=argc>1?(unsigned)strtoul(argv[1],NULL,10):0;
    int ticks=argc>2?atoi(argv[2]):6144;
    if(mask>262143||ticks<1||ticks>6144)return 1;
    static State a,next;static Info m,newm;
    append(&a,134*Q,135*Q-512,2);
    append(&a,135*Q-512,146*Q-512,1);
    append(&a,146*Q-512,146*Q,3);
    for(int col=118;col<=148;col++){
        if((col==124&&(mask&1))||(130<=col&&col<=134&&(mask&(1u<<(col-129)))))
            m.x[m.n++]=col*Q+3;
        if(135<=col&&col<=145)m.x[m.n++]=col*Q+509;
        if(134<=col&&col<=145&&(mask&(1u<<(col-134+6))))m.x[m.n++]=col*Q+515;
        if((118<=col&&col<=133)||(146<=col&&col<=148))m.x[m.n++]=col*Q+1021;
    }
    for(int i=1;i<m.n;i++)if(m.x[i]<=m.x[i-1])return 7;
    uint64_t events=0;report(&a,&m,0,events);
    for(int t=0;t<ticks;t++){
        events+=step(&a,&m,&next,&newm,t);a=next;m=newm;report(&a,&m,t+1,events);
    }
    printf("{\"mask\":%u,\"endpoint_segments\":[",mask);
    for(int i=0;i<a.n;i++)printf("%s[%d,%d,%u]",i?",":"",a.seg[i].lo,a.seg[i].hi,a.seg[i].v);
    printf("],\"endpoint_Info\":[");for(int i=0;i<m.n;i++)printf("%s%d",i?",":"",m.x[i]);
    printf("],\"exact_event_execution_complete\":true,\"physical_source_reachability_proved\":false}\n");
    return 0;
}
