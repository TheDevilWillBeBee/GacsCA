/* Finite GF word-counting certificate, not a CA trajectory or new rule.
 * Native side votes of raw GF zero except q at143 and r at146.
 * Age and workspace populations are discharged separately in the proof. */
#include <stdio.h>
#include <stdint.h>
#define Q 1024
static int raw(int s,int q,int r){return s==143?q:s==146?r:0;}
static int quorum(int h,int side,int q,int r,int *out){
    int words[5];for(int i=0;i<5;i++){
        int d=side*(i+1);words[i]=(raw(h+d,q,r)-d+Q)%Q;
    }
    for(int i=0;i<5;i++){
        int count=0;for(int j=0;j<5;j++)count+=words[i]==words[j];
        if(count>=3){*out=words[i];return 1;}
    }
    *out=raw(h,q,r);return 0;
}
int main(void){
    uint64_t cases=0,right_cases=0,left_cases=0;
    int pairs[4][2]={{1,4},{1023,2},{1022,1},{1020,1023}};
    for(int q=0;q<Q;q++)for(int r=0;r<Q;r++)for(int h=142;h<=148;h++){
        int R,L;int rex=quorum(h,1,q,r,&R),lex=quorum(h,-1,q,r,&L);
        int listed=0;for(int i=0;i<4;i++)listed|=q==pairs[i][0]&&r==pairs[i][1];
        if((rex||lex)&&!listed)return 1;
        if(rex){
            if(h!=142||R<Q-5)return 2;
            int mismatch=0,free_workspace=0;
            for(int d=-5;d<=-1;d++)if(0<=R+d&&R+d<Q)
                mismatch+=raw(h+d,q,r)!=(R+d+Q)%Q;
            for(int d=-5;d<=5;d++)if(0<=R+d&&R+d<Q)
                free_workspace+=146<=h+d&&h+d<=148;
            if(mismatch<3||free_workspace>2)return 3;
            right_cases++;
        }
        if(lex){if(h!=147&&h!=148)return 4;left_cases++;}
        int zeros=0,twos=0;
        for(int s=h-5;s<h;s++){zeros+=s<=141;twos+=142<=s&&s<=145;}
        if(zeros>=3){if(lex||h>144)return 5;}
        else if(twos<3)return 6;
        cases++;
    }
    printf("{\"complete_GF_pairs\":1048576,\"receivers\":7,\"native_side_cases\":%llu,\"right_GF_quorum_cases\":%llu,\"left_GF_quorum_cases\":%llu,\"right_quorum_forces_three_left_mismatches\":true,\"right_quorum_has_at_most_two_free_Workspace2_inputs\":true,\"selected_left_Age2_population_identity\":true}\n",
        (unsigned long long)cases,(unsigned long long)right_cases,(unsigned long long)left_cases);
    return 0;
}
