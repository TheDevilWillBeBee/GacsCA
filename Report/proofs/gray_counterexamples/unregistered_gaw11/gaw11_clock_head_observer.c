/* Read-only composition with the frozen exact GAW7 event partition.
 * The new proof must derive the actual zero Workspace history, independently
 * of any surviving Head. This observer does not simulate SF fields.
 */
#define main gaw7_frozen_main
#include "../unregistered_gaw7/gaw7_clock_events.c"
#undef main

int main(int argc,char **argv) {
    int b=argc>1?atoi(argv[1]):3842;
    int first=argc>2?atoi(argv[2]):128;
    State a={.n=1,.seg={{b,b+16,1}}},next={0};
    uint64_t events=0;
    int t=0,last_clock=0,last_head_clock=0,max_segments=1;
    printf("t,n,head_wrong_clock,segments\n");
    for(;;) {
        int clock=0,head=0;
        for(int j=0;j<a.n;j++) clock|=(a.seg[j].v&1)!=0;
        for(int x=3846;x<=3850;x++) head|=(at(&a,x)&1)!=0;
        if(clock)last_clock=t;
        if(head)last_head_clock=t;
        printf("%d,%d,%d,",t,a.n,head);
        for(int j=0;j<a.n;j++) printf("%s%d:%d:%u",j?";":"",a.seg[j].lo,a.seg[j].hi,a.seg[j].v);
        printf("\n");
        if(t>=first&&head) {fprintf(stderr,"wrong clock at surviving head, t%d\n",t);return 8;}
        if(!a.n)break;
        if(t>=4*Q)return 9;
        events+=step(&a,&next);a=next;t++;
        if(a.n>max_segments)max_segments=a.n;
    }
    fprintf(stderr,"b=%d width16 quiet=%d clock_recovery=%d last_head_wrong_clock=%d event_checks=%llu max_segments=%d protected_from=%d\n",
        b,t,last_clock+1,last_head_clock,(unsigned long long)events,max_segments,first);
    return 0;
}
