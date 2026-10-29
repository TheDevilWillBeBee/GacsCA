/* NEW diagnostic batching only. The total frozen local_R still computes
 * every Head/Out/History/Info/Workspace field. No future SF is omitted.
 * native() is the accepted literal native transcription, included read-only.
 */
#include "../unregistered_gaw9/gaw9_native_info.c"
int gaw11_native_batch(const Site *a,int n,Site *b){
    View v={.a=a,.initial=NULL,.lo=0,.hi=n-1,.n=n,.offset=0,.t=0};
    for(int x=5;x<n-5;x++)b[x]=native(&v,x);
    return 0;
}
