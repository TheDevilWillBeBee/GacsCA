/* NEW analysis driver of the SAME frozen scalar/native factor.
 * Starts at the proved actual3U row, with sources derived from that
 * row's actual fourth gathers/early heads/couriers. No rule changes.
 */
#define main old_interval_main
#include "../unregistered_gaw23/gaw23_interval_native.c"
#undef main
#include <assert.h>
int main(int argc,char **argv){
    assert(argc==3);FILE *s=fopen(argv[2],"r");assert(s);
    while(nsrc<MAXSRC&&fscanf(s,"%d",&sources[nsrc].p)==1){sources[nsrc].bits=0;nsrc++;}fclose(s);
    assert(nsrc>0);FILE *f=fopen(argv[1],"wb");assert(f);
    nseg=3;old[0]=(Seg){21*Q,43*Q/2,2};old[1]=(Seg){43*Q/2,51*Q/2,1};old[2]=(Seg){51*Q/2,26*Q,3};
    int row=0,updates=0;long long events=0;record(f,row);
    printf("{\"Q\":%d,\"U\":%d,\"physical_period_index\":4,\"snapshots\":[",Q,U);print_state(row);
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
    printf("],\"computed_updates\":%d,\"event_intervals\":%lld,\"source_Info_at_4U_commit_not_claimed\":true,\"passed\":true}\n",updates,events);
    fclose(f);return 0;
}
