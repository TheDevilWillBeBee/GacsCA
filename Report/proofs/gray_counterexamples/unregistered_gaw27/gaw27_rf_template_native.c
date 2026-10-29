/* NEW analysis driver of the SAME frozen scalar/native factor.
 * Starts at the proved actual5U row, with sources derived from that
 * row's actual fifth gathers/early heads/couriers. No rule changes.
 */
#define main old_interval_main
#include "../unregistered_gaw23/gaw23_interval_native.c"
#undef main
#include <assert.h>
int main(int argc,char **argv){
    assert(argc==2);FILE *f=fopen(argv[1],"wb");assert(f);
    nsrc=6;
    for(int g=1;g<=3;g++)sources[g-1]=(Source){g*Q+Q/2-3,0};
    for(int g=4;g<=6;g++)sources[g-1]=(Source){(g+1)*Q-3,0};
    nseg=3;old[0]=(Seg){0,Q/2,2};old[1]=(Seg){Q/2,7*Q/2,1};old[2]=(Seg){7*Q/2,4*Q,3};
    int row=0,updates=0;long long events=0;record(f,row);
    printf("{\"Q\":%d,\"U\":%d,\"conditional_RF_template_component\":true,\"snapshots\":[",Q,U);print_state(row);
    /* The exact native fixed point has closed Workspace guards, source3
     * never fires, and no Age dependency remains before the80Q write.
     */
    assert(step(1,&events));updates++;row=1;record(f,row);
    row=80*Q-2;record(f,row);
    while(row<U){
        int unchanged=step(++row,&events);updates++;
        if(row==80*Q-1){
            for(int i=0;i<nsrc;i++){
                Native z=native(sources[i].p);assert(gf(sources[i].p,z.label)==Q-3&&!z.wipe);
                sources[i].bits=31;
            }
        }
        record(f,row);
        if(row==80*Q-1){printf(",");print_state(row);row=96*Q-1;record(f,row);}
        if(row==96*Q||row==97*Q||row==98*Q||row==99*Q||row==102*Q){printf(",");print_state(row);}
        if(row>=98*Q&&unchanged){row=U;record(f,row);break;}
    }
    printf(",");print_state(row);
    printf("],\"computed_updates\":%d,\"event_intervals\":%lld,\"source_Info_at_5U_commit_not_claimed\":true,\"passed\":true}\n",updates,events);
    fclose(f);return 0;
}
