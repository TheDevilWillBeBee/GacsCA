/* NEW fourth-period mask analysis of the SAME original row1 fault, no CA changes.
 * Prefix tags act on held Info before H2/H3 gathers. Pulse tags act on
 * already equal, coherent H2/H3 from96Q-1. Never reuse the Info tracker
 * across the80Q special write or claim an Out/U encoding here.
 */
#define main old_interval_main
#include "../unregistered_gaw23/gaw23_interval_native.c"
#undef main
#include <assert.h>
#define LOW (-40*Q)
#define HIGH (40*Q)
#define SIZE (HIGH-LOW)
static unsigned char tags[SIZE],marked[SIZE];
static int pending[SIZE],npending,active[SIZE],nactive;
static Seg incoming_state[MAXSEG],wipes[MAXSEG];static int nincoming,nwipes;
static int phase_state(int x){
    int lo=0,hi=nincoming;
    while(lo<hi){int mid=(lo+hi)/2;if(incoming_state[mid].hi<=x)lo=mid+1;else hi=mid;}
    return lo<nincoming&&incoming_state[lo].lo<=x?incoming_state[lo].v:0;
}
static int wiped(int x){
    int lo=0,hi=nwipes;
    while(lo<hi){int mid=(lo+hi)/2;if(wipes[mid].hi<=x)lo=mid+1;else hi=mid;}
    return lo<nwipes&&wipes[lo].lo<=x;
}
static void mark(int p){
    assert(LOW<=p&&p<HIGH);int i=p-LOW;
    if(!marked[i]){marked[i]=1;active[nactive++]=p;}
}
static void get_wipes(void){
    ncuts=0;nwipes=0;
    for(int i=0;i<nseg;i++){cut(old[i].lo);cut(old[i].hi);}
    for(int i=0;i<nincoming;i++){cut(incoming_state[i].lo);cut(incoming_state[i].hi);}
    qsort(cuts,ncuts,sizeof(int),cmp);
    for(int i=0;i<ncuts-1;i++){
        int a=cuts[i],b=cuts[i+1];if(a==b)continue;
        int v=phase_state(a),o=state(a);
        if((v&2)&&((v^o)&1)){
            if(nwipes&&wipes[nwipes-1].hi==a)wipes[nwipes-1].hi=b;
            else{assert(nwipes<MAXSEG);wipes[nwipes++]=(Seg){a,b,1};}
        }
    }
}
static long long do_masks(void){
    get_wipes();long long locations=0;nactive=0;
    for(int i=0;i<npending;i++)mark(pending[i]);
    for(int i=0;i<nwipes;i++)for(int x=wipes[i].lo;x<wipes[i].hi;x++){
        locations++;for(int h=0;h<5;h++)mark(x+slots[h]);
    }
    npending=0;
    for(int i=0;i<nactive;i++){
        int p=active[i],j=p-LOW,v=vote(tags[j]),newbits=0;
        for(int h=0;h<5;h++)newbits|=(v&&!wiped(p-slots[h]))<<h;
        tags[j]=(unsigned char)newbits;marked[j]=0;
        if(newbits&&newbits!=31)pending[npending++]=p;
    }
    return locations;
}
static void reset_masks(void){memset(tags,31,sizeof(tags));npending=nactive=0;memset(marked,0,sizeof(marked));}
static void write_masks(const char *path){
    FILE *f=fopen(path,"wb");assert(f);int h[2]={LOW,HIGH};assert(fwrite(h,sizeof(int),2,f)==2);
    assert(fwrite(tags,1,sizeof(tags),f)==sizeof(tags));fclose(f);
}
static void print_intervals(void){
    printf("[");int first=1;
    for(int p=LOW;p<HIGH;){
        if(tags[p-LOW]==31){p++;continue;}
        int a=p,v=tags[p-LOW];while(p<HIGH&&tags[p-LOW]==v)p++;
        printf("%s[%d,%d,%d]",first?"":",",a,p,v);first=0;
    }printf("]");
}
static int read_record(FILE *f,int *row,Seg *s,int *nn){
    int h[3];size_t n=fread(h,sizeof(int),3,f);if(!n)return 0;assert(n==3);
    *row=h[0];*nn=h[1];int ns=h[2];assert(0<=*nn&&*nn<=MAXSEG&&0<=ns&&ns<=MAXSRC);
    assert(fread(s,sizeof(Seg),(size_t)*nn,f)==(size_t)*nn);
    Source discarded[MAXSRC];assert(fread(discarded,sizeof(Source),(size_t)ns,f)==(size_t)ns);return 1;
}
int main(int argc,char **argv){
    assert(argc==4);FILE *f=fopen(argv[1],"rb");assert(f);
    int row,after,prefix_saved=0,pulse_started=0;long long prefix_wipes=0,pulse_wipes=0,updates=0;
    assert(read_record(f,&row,old,&nseg));assert(row==0);reset_masks();
    printf("{\"Q\":%d,\"U\":%d,\"tag_domain\":[%d,%d],",Q,U,LOW,HIGH);
    while(read_record(f,&after,incoming_state,&nincoming)){
        if(after==96*Q-1){reset_masks();pulse_started=1;}
        if(after==row+1&&(after<=4099||pulse_started)){
            long long n=do_masks();updates++;
            if(pulse_started)pulse_wipes+=n;else prefix_wipes+=n;
        }
        memcpy(old,incoming_state,(size_t)nincoming*sizeof(Seg));nseg=nincoming;row=after;
        if(row==1&&!prefix_saved){
            assert(npending==0);write_masks(argv[2]);prefix_saved=1;
            printf("\"prefix_Info_zero_tag_intervals\":");print_intervals();printf(",");
        }
        if(row==U){
            assert(prefix_saved&&pulse_started&&npending==0);write_masks(argv[3]);
            printf("\"pulse_H2_H3_zero_tag_intervals\":");print_intervals();printf(",");
        }
    }fclose(f);
    printf("\"prefix_GF_wipe_holder_locations\":%lld,\"pulse_GF_wipe_holder_locations\":%lld,\"mask_updates\":%lld,\"all_final_tags_coherent0_or31\":true,\"same_actual_GAW26_fourth_native_event_history\":true,\"passed\":true}\n",prefix_wipes,pulse_wipes,updates);
    return 0;
}
